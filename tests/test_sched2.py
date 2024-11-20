import datetime as dt
import random
import time

import pytest

import sched2


@pytest.fixture
def scheduler(mocker):
    mocker.patch("time.time", return_value=0)
    mocker.patch("time.sleep", return_value=None)

    yield sched2.scheduler(time.time, time.sleep)


@pytest.fixture
def action(mocker):
    # mock must return Falsy value to keep repeating
    return mocker.Mock(return_value=False)


def test_repeat_method_returns_action(scheduler, action):
    repeat_return_value = scheduler.repeat(1, 1, action, immediate=False)
    assert repeat_return_value is action


def test_every_decorator_method_returns_action(scheduler, action):
    every_return_value = scheduler.every(1)(action)
    assert every_return_value is action


def test_cron_decorator_method_returns_action(scheduler, action):
    cron_return_value = scheduler.cron("* * * * *")(action)
    assert cron_return_value is action


def test_on_decorator_method_returns_action(scheduler, action):
    on_return_value = scheduler.on("event")(action)
    assert on_return_value is action


def test_repeat_adds_a_single_event(scheduler, action):
    # starts empty
    assert len(scheduler.queue) == 0

    # adds a single event
    scheduler.repeat(1, 1, action, immediate=False)
    assert len(scheduler.queue) == 1


def test_repeat_immediate_runs_immediately(scheduler, action):
    scheduler.repeat(1, 1, action, immediate=True)
    scheduler.run(blocking=False)

    action.assert_called_once()


def test_repeat_delayed_only_runs_after_delay(scheduler, action):
    scheduler.repeat(1, 1, action, immediate=False)

    scheduler.run(blocking=False)
    action.assert_not_called()

    time.time.return_value = 1
    scheduler.run(blocking=False)
    action.assert_called_once()


def test_that_the_every_decorator_works(scheduler, action):
    # use the decorator as a function
    # this use case is equivalent to the repeat method
    # or the python decorator syntax
    scheduler.every(1)(action)
    assert len(scheduler.queue) == 1

    scheduler.run(blocking=False)
    action.assert_called_once()


def test_invalid_cron_fields_raise_value_error():
    with pytest.raises(ValueError):
        sched2.parse_field("a", 10)

    with pytest.raises(ValueError):
        sched2.parse_field("5-10-15", 10)

    with pytest.raises(ValueError):
        sched2.parse_field("5~10~15", 10)

    with pytest.raises(ValueError):
        sched2.parse_field("5/2", 10)

    with pytest.raises(ValueError):
        sched2.parse_field("5-15", 10)

    with pytest.raises(ValueError):
        sched2.parse_field("5~15", 10)

    with pytest.raises(ValueError):
        sched2.parse_field("--5", 10)

    with pytest.raises(ValueError):
        sched2.parse_field("5/-2", 10)


def test_parse_cron_wildcards():
    assert sched2.parse_field("*", 10) == set(range(11))
    assert sched2.parse_field("*/2", 10) == set(range(0, 11, 2))
    assert sched2.parse_field("*/15", 10) == {0}
    assert sched2.parse_field("*/30", 59) == {0, 30}


def test_parse_cron_ranges():
    assert sched2.parse_field("5", 10) == {5}
    assert sched2.parse_field("5-10", 10) == set(range(5, 11))
    assert sched2.parse_field("5-", 10) == set(range(5, 11))
    assert sched2.parse_field("-10", 10) == set(range(11))
    assert sched2.parse_field("5-5", 69) == {5}

    assert sched2.parse_field("5-10/2", 10) == set(range(5, 11, 2))
    assert sched2.parse_field("5-/2", 10) == set(range(5, 11, 2))
    assert sched2.parse_field("-10/2", 10) == set(range(0, 11, 2))

    with pytest.raises(ValueError):
        sched2.parse_field("1-13", 12, 1)

    with pytest.raises(ValueError):
        sched2.parse_field("0-12", 12, 1)


def test_parse_cron_random():
    # these are tested to make sure the random numbers are within the range
    assert sched2.parse_field("5~10", 10) <= set(range(5, 11))
    assert sched2.parse_field("5~10/2", 10) <= set(range(5, 11))
    assert sched2.parse_field("5~/2", 10) <= set(range(5, 11))
    assert sched2.parse_field("~10/2", 10) <= set(range(11))
    assert len(sched2.parse_field("~/30", 59)) == 2
    assert len(sched2.parse_field("5~5", 59)) == 1

    # test a single known exact value
    # this tests the range and step parsing
    random.seed(0)
    assert sched2.parse_field("5~10/2", 10) == {6, 8, 10}


def test_parsing_cron_lists():
    assert sched2.parse_field("1,2,3", 10) == {1, 2, 3}
    assert sched2.parse_field("1,2,3-5", 10) == {1, 2, 3, 4, 5}
    assert sched2.parse_field("-5/2,5-/3", 10) == {0, 2, 4, 5, 8}
    assert sched2.parse_field("1-7,4-10", 10) == set(range(1, 11))


def test_parsing_cron_rule():
    # monday at 9am
    rule = "0 9 * * 1"
    assert sched2.parse_rule(rule) == {
        "minute": {0},
        "hour": {9},
        "day": set(range(1, 32)),
        "month": set(range(1, 13)),
        "day_of_week": {0},
    }

    # every friday at midnight
    rule = "0 0 * * 5"
    assert sched2.parse_rule(rule) == {
        "minute": {0},
        "hour": {0},
        "day": set(range(1, 32)),
        "month": set(range(1, 13)),
        "day_of_week": {4},
    }

    # first of august at noon
    rule = "0 12 1 8 *"
    assert sched2.parse_rule(rule) == {
        "minute": {0},
        "hour": {12},
        "day": {1},
        "month": {8},
        "day_of_week": set(range(7)),
    }

    # minute 1 of every hour
    rule = "1 * * * *"
    assert sched2.parse_rule(rule) == {
        "minute": {1},
        "hour": set(range(24)),
        "day": set(range(1, 32)),
        "month": set(range(1, 13)),
        "day_of_week": set(range(7)),
    }

    rule = "5 * * * *"
    assert sched2.parse_rule(rule) == {
        "minute": {5},
        "hour": set(range(24)),
        "day": set(range(1, 32)),
        "month": set(range(1, 13)),
        "day_of_week": set(range(7)),
    }


def test_rule_checker():
    # sunday morning
    parsed_rule = sched2.parse_rule("0 9 * * 0")
    assert sched2.check_rule(parsed_rule, dt.datetime(2024, 2, 25, 9, 0))

    # friday midnight
    rule = sched2.parse_rule("0 0 * * 5")
    assert sched2.check_rule(rule, dt.datetime(2024, 2, 23, 0, 0))

    rule = sched2.parse_rule("1 * * * *")
    assert sched2.check_rule(rule, dt.datetime(2024, 2, 25, 0, 1))


def test_event_listener_is_called(scheduler, action):
    scheduler.on("event")(action)
    scheduler.emit("event")

    time.time.return_value = 10
    scheduler.run(blocking=False)

    action.assert_called_once()


def test_event_listener_is_not_called_for_different_event(scheduler, action):
    scheduler.on("event")(action)
    scheduler.emit("other_event")

    time.time.return_value = 10
    scheduler.run(blocking=False)

    action.assert_not_called()


def test_event_listener_is_called_with_arguments(scheduler, mocker):
    def action(message): ...

    action = mocker.Mock(action)
    scheduler.on("event")(action)
    scheduler.emit("event", kwargs={"message": "hello"})

    time.time.return_value = 10
    scheduler.run(blocking=False)

    action.assert_called_once_with("hello")


def test_multiple_event_listeners_are_called(scheduler, mocker):
    action = mocker.Mock()
    action2 = mocker.Mock()

    scheduler.on("event")(action)
    scheduler.on("event")(action2)

    scheduler.emit("event")

    time.time.return_value = 10
    scheduler.run(blocking=False)

    action.assert_called_once()
    action2.assert_called_once()


def test_event_listener_is_called_with_delay(scheduler, action):
    scheduler.on("event", priority=1)(action)
    scheduler.emit("event", delay=5)

    time.time.return_value = 0
    scheduler.run(blocking=False)

    action.assert_not_called()

    time.time.return_value = 10
    scheduler.run(blocking=False)

    action.assert_called_once()
