from functools import partial
import sched


__all__ = ["scheduler"]

_sentinel = object()


class scheduler(sched.scheduler):
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
