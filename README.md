# Event scheduler 2

sched2, like sched, provides a `scheduler` class - same name.
The `sched2.scheduler` class is a *subclass* of `sched.scheduler`.
The new scheduler class provides two new methods.


## The new methods
- `repeat` - has the same signature as `scheduler.enter` but behaves diferently. As you can guess it will repeatedly call `action`. It does this by repeatedly pushing the `action` call back into the scheduler queue. The `delay` and `priority` values are respected for all reintroductions into the queue.
- `every` -  is a decorator variant of `repeat` that enters the decorated function into the queue at definition time.


## Classic example
```python
import time
import sched2

def some_function():
    print(time.time())

s = sched2.scheduler()
s.repeat(delay=1, priority=0, action=some_function)

s.run()  # runs forever...
```


## Decorator example
```python
import time
import sched2

s = sched2.scheduler()

@s.every(1, 0)
def some_function():
    print(time.time())

s.run()  # never stops...
```
