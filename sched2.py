from functools import partial
import sched


class scheduler(sched.scheduler):
    def repeat(self, interval, priority, action, argument=None, kwargs=None):
        """A variant of enter that re-enters itself."""
        argument = argument if argument else ()
        kwargs = kwargs if kwargs else {}

        partial_action = partial(action, *argument, **kwargs)

        def repeater(action):
            action()
            self.enter(interval, priority, repeater, (partial_action,))

        s.enter(interval, priority, repeater, (partial_action,))

    def every(self, interval, priority):
        """A variant of repeat as a decorator."""
        return partial(self.repeat, interval, priority)
