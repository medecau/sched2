from datetime import timedelta
from functools import partial
import sched


__all__ = ["scheduler"]

_sentinel = object()


class scheduler(sched.scheduler):
    def enter(self, delay, priority, action, argument=(), kwargs=_sentinel):
        """A variant that specifies the time as a relative time.

        The delay argument may be provided as a datetime.timedelta object.
        """
        if isinstance(delay, timedelta):
            delay = delay.total_seconds()

        if kwargs is _sentinel:
            kwargs = {}

        return super().enter(delay, priority, action, argument, kwargs)

    def repeat(self, delay, priority, action, argument=(), kwargs=_sentinel):
        """A variant of enter that re-enters itself."""
        if kwargs is _sentinel:
            kwargs = {}

        partial_action = partial(action, *argument, **kwargs)

        def repeater(action):
            action()
            self.enter(delay, priority, repeater, (partial_action,))

        self.enter(delay, priority, repeater, (partial_action,))

    def every(self, delay, priority):
        """A variant of repeat as a decorator."""
        return partial(self.repeat, delay, priority)
