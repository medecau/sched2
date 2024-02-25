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
