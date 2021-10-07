from functools import partial
import sched


class scheduler(sched.scheduler):
    def repeat(self, delay, priority, action, argument=None, kwargs=None):
        """A variant of enter that re-enters itself."""
        argument = argument if argument else ()
        kwargs = kwargs if kwargs else {}

        partial_action = partial(action, *argument, **kwargs)

        def repeater(action):
            action()
            self.enter(delay, priority, repeater, (partial_action,))

        self.enter(delay, priority, repeater, (partial_action,))

    def every(self, delay, priority):
        """A variant of repeat as a decorator."""
        return partial(self.repeat, delay, priority)
