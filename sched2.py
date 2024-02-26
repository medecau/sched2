"""
.. include:: README.md
"""

import datetime as dt
import random
import re
import sched
from functools import partial

__all__ = ["scheduler"]

_sentinel = object()


class scheduler(sched.scheduler):
    """A subclass of the `sched.scheduler` class from the standard library.

    This subclass adds additional functionality to the `scheduler` class,
    including the ability to schedule events using relative time intervals
    and a decorator for scheduling events to run at regular intervals.
    """

    def repeat(
        self, delay, priority, action, immediate=True, argument=(), kwargs=_sentinel
    ):
        """Schedule an event to be run at regular intervals.

        This method is a variant of the `sched2.enter` method that re-schedules itself
        after each run. It allows a function to be scheduled to run at regular
        intervals by specifying the `delay` and `priority` as arguments.

        The `immediate` argument controls whether the first run of the function
        is scheduled immediately or after the specified delay. The default is
        `True`, which schedules the first run immediately.

        The `argument` and `kwargs` arguments are passed to the function when
        it is called. If the `kwargs` argument is not provided, it defaults to
        an empty dictionary.

        In the event that the function returns a `True`ish value, the function
        will not be re-scheduled.
        """

        if kwargs is _sentinel:
            kwargs = {}

        partial_action = partial(action, *argument, **kwargs)

        def repeater(action):
            # if the action returns a Trueish value, do not re-schedule
            if not action():
                self.enter(delay, priority, repeater, (partial_action,))

        initial_delay = 0 if immediate else delay
        self.enter(initial_delay, priority, repeater, (partial_action,))

        # this return value is used by the decorator
        # do not change this to return partial_action
        # we return the original action so it can be decorated multiple times
        return action

    def every(self, delay, priority=0, immediate=True):
        """Schedule an event to be run at regular intervals using a decorator.

        This method is a variant of the `sched2.repeat` method that can be used as a
        decorator. It allows a function to be scheduled to run at regular
        intervals by specifying the `delay` and `priority` as arguments. The
        default `priority` is `0`.

        The `immediate` argument controls whether the first run of the function
        is scheduled immediately or after the specified delay. The default is
        `True`, which schedules the first run immediately.

        In the event that the function returns a `True`ish value, the function
        will not be re-scheduled.
        """

        # we return a partial application of repeat
        # this will be immediately called to decorate the function
        return partial(self.repeat, delay, priority, immediate=immediate)


field_pattern = re.compile(
    r"^(?P<start>\d{1,2})?(?P<operator>[*~-])?(?P<stop>\d{1,2})?(?:/(?P<step>\d{1,2}))?$"
)


def parse_field(field, max, min=0):
    # compute set of allowed values

    allowed = set()

    for part in field.split(","):
        match = field_pattern.match(part)
        if not match:
            raise ValueError(f"invalid field[{field}]")
        start, operator, stop, step = match.groups()

        # convert to integers
        start = int(start) if start else None
        stop = int(stop) if stop else None
        step = int(step) if step else None

        # check bounds
        if (start is not None and start < min) or (stop is not None and stop > max):
            raise ValueError(f"invalid field[{field}]")

        # compute allowed values
        if operator in {"-", "~"}:
            start = start if start is not None else min
            stop = stop if stop is not None else max

        if operator == "*":
            step = step or 1
            allowed.update(range(min, max + 1, step))

        elif operator == "-":
            step = step or 1
            allowed.update(range(start, stop + 1, step))

        elif operator == "~":
            if step:  # multiple random values at regular intervals
                if step > (stop - start):
                    start = random.randint(start, stop)
                else:
                    start = random.randint(start, start + step)

                allowed.update(range(start, stop + 1, step))

            else:  # a single random value
                allowed.add(random.randint(start, stop))

        elif not operator:
            if (step or stop) or start is None:
                raise ValueError(f"invalid field[{field}]")
            allowed.add(start)

    return allowed


def parse_rule(rule):
    minute, hour, day, month, day_of_week = rule.split()

    # day of week requires special handling
    # it allows for two values for sunday
    # and is misaligned with the datetime module

    day_of_week = parse_field(day_of_week, 7)
    # for cron 0 is sunday, but for datetime 0 is monday
    day_of_week = {wd - 1 for wd in day_of_week}

    # if the rule contains -1, it means sunday  is not included
    # we need to remove it and add 6 (sunday) to the set

    if -1 in day_of_week:
        day_of_week.remove(-1)
        day_of_week.add(6)

    return {
        "minute": parse_field(minute, 59),
        "hour": parse_field(hour, 23),
        "day": parse_field(day, 31, 1),
        "month": parse_field(month, 12, 1),
        "day_of_week": day_of_week,
    }


def check_rule(parsed_rule, now=None):
    if now is None:
        now = dt.datetime.now()
    return (
        now.minute in parsed_rule["minute"]
        and now.hour in parsed_rule["hour"]
        and now.day in parsed_rule["day"]
        and now.month in parsed_rule["month"]
        and now.weekday() in parsed_rule["day_of_week"]
    )
