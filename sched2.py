"""
.. include:: README.md
"""

import datetime as dt
import random
import re
import sched
from collections import defaultdict
from functools import partial

__all__ = ["scheduler"]

_sentinel = object()


class scheduler(sched.scheduler):
    """A subclass of the `sched.scheduler` class from the standard library.

    This subclass adds additional functionality to the `scheduler` class,
    including the ability to schedule events using relative time intervals
    and a decorator for scheduling events to run at regular intervals.
    """

    __listeners = defaultdict(list)

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

    def cron(self, rule, priority=0):
        """Schedule an event to be run at specific times using a cron-like syntax.

        A cron rule is a string with five space-separated fields that represent
        the minute, hour, day, month, and day of the week. Each field can contain
        a single value, a range of values, or a list of values separated by commas.

        The implementation resembles the cron syntax used in OpenBSD's `cron` and
        other Unix-like operating systems.

        The fields support the following operators:

        - `*` (asterisk) - matches all values
        - `-` (hyphen) - matches a range of values
        - `~` (tilde) - matches a random value
        - `/` (slash) - modifies ranges to include only every nth value

        Examples of valid cron rules include:

        - `0 0 * * *` - midnight of every day
        - `*/5 * * * *` - every 5 minutes
        - `0 0 * * 5` - midnight of every Friday
        - `0 0 1 */3 *` - midnight of the first day of every quarter
        - `0 9 * * 1-5` - 9:00 of every weekday
        - `0~10 9 * * 1-5` - a random minute just past 9:00 of every weekday
        - `~/30 * * * *` - twice an hour at random minutes

        Random values are chosen when the event is scheduled, and do not change
        for the lifetime of the event.

        The `priority` argument specifies the priority of the event in the
        scheduler. The default is `0`.

        """
        parsed_rule = parse_rule(rule)

        def cron_runner(action):
            if check_rule(parsed_rule):
                self.enter(0, priority, action)
            delay = 60 - self.timefunc() % 60
            self.enter(delay, 0, cron_runner, (action,))

            return action

        return cron_runner

    @property
    def listeners(self):
        return self.__listeners.copy()

    def on(self, event, priority=0, action=None):
        """Register a function to be called when an event is emitted.

        This method is a decorator that registers a function to be called when
        an event is emitted.

        The `event` argument is a string that represents
        the name of the event.

        The `priority` argument specifies the priority
        of the event in the scheduler. The default is `0`.

        The decorated function is called with the same arguments and keyword
        arguments that are passed to the `emit` method.

        """

        def decorator(action):
            # we use a tuple of (action, priority) as the value
            self.__listeners[event].append((action, priority))

            return action

        if action is not None:
            return decorator(action)

        return decorator

    def emit(self, event, *, delay=0, args=(), kwargs=None):
        """Emit an event to call all registered listeners.

        This method schedules calls to all registered listeners for the
        specified event.

        The `event` argument is a string that represents the name of the event.

        The `delay` argument specifies the delay in seconds before the listeners
        are called. The default is `0`.

        The `args` and `kwargs` arguments are passed to the listeners when they
        are called.

        """
        if kwargs is None:
            kwargs = {}

        if event not in self.__listeners:
            return

        # sort the listeners by priority
        self.__listeners[event] = sorted(self.__listeners[event], key=lambda x: x[1])

        # schedule calls to the listeners
        for action, priority in self.__listeners[event]:
            self.enter(delay, priority, action, args, kwargs)

        return


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
                    start = random.randint(start, start + step - 1)

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
