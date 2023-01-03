"""
.. include:: README.md
"""
from datetime import timedelta
from functools import partial
import sched


__all__ = ["scheduler"]

_sentinel = object()


class scheduler(sched.scheduler):
    """A subclass of the `sched.scheduler` class from the standard library.

    This subclass adds additional functionality to the `scheduler` class,
    including the ability to schedule events using relative time intervals
    and a decorator for scheduling events to run at regular intervals.
    """

    def enter(self, delay, priority, action, argument=(), kwargs=_sentinel):
        """Schedule an event to be run at a specific time.

        This variant of the `sched.enter` method allows the delay argument to be
        specified as a `datetime.timedelta` object. If the `kwargs` argument
        is not provided, it defaults to an empty dictionary.
        """
        if isinstance(delay, timedelta):
            delay = delay.total_seconds()

        if kwargs is _sentinel:
            kwargs = {}

        return super().enter(delay, priority, action, argument, kwargs)

    def repeat(self, delay, priority, action, argument=(), kwargs=_sentinel):
        """Schedule an event to be run at regular intervals.

        This method is a variant of the `sched2.enter` method that re-schedules itself
        after each run. If the `kwargs` argument is not provided, it defaults
        to an empty dictionary.
        """
        if kwargs is _sentinel:
            kwargs = {}

        partial_action = partial(action, *argument, **kwargs)

        def repeater(action):
            action()
            self.enter(delay, priority, repeater, (partial_action,))

        self.enter(delay, priority, repeater, (partial_action,))

    def every(self, delay, priority=0):
        """Schedule an event to be run at regular intervals using a decorator.

        This method is a variant of the `sched2.repeat` method that can be used as a
        decorator. It allows a function to be scheduled to run at regular
        intervals by specifying the `delay` and `priority` as arguments. The
        default `priority` is `0`.
        """
        return partial(self.repeat, delay, priority)
