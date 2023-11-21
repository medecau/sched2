"""
.. include:: README.md
"""
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
        after each run. If the `kwargs` argument is not provided, it defaults
        to an empty dictionary.
        """

        if kwargs is _sentinel:
            kwargs = {}

        partial_action = partial(action, *argument, **kwargs)

        def repeater(action):
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
        """

        # we return a partial application of repeat
        # this will be immediately called to decorate the function
        return partial(self.repeat, delay, priority, immediate=immediate)
