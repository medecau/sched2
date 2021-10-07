# Event scheduler 2

`sched2`' provides a *subclass* of `sched.scheduler` with extra functionality.
If you're already using `sched` then `sched2` is a drop-in-place change.

## The extra functionality
- `enter` - now also accepts `datetime.timedelta` objects as values for the delta parameter.
- `repeat` - a new method with the same signature as `enter` that re-schedules `action` after it returns.
- `every` -  is a decorator variant of `repeat` that schedules the decorated function at definition time.

 ### Enter
Schedules an `action` to be called only once after some `delay` whereas `repeat` will re-schedule the `action` to be called again and again forever. It does this by repeatedly pushing the `action` *callable* back into the scheduler queue. The `delay` and `priority` values are fixed for all reintroductions into the queue.

### Every
A decorator that provides a friendly way of scheduling functions at definition time.


## Install

`pip install sched2`


## Use


```python
from urllib.request import urlopen
from sched2 import scheduler


sc = scheduler()


# repeatedly print public IP every 60 seconds
@sc.every(60, 0)
def echo_ip():
    ip = urlopen("https://icanhazip.com/").read().decode("utf-8").strip()
    print(f"ip: {ip}")

sc.run()
```


Now a less realistic example showing all the extra functionality

```python
from time import time
from datetime import datetime, timedelta

from sched2 import scheduler


started_at = time()

# we'll use this in a bit
def echo_time_elapsed():
    seconds_since_started = round(time() - started_at, 2)
    print(f"started {seconds_since_started}s ago")


print(f"started at {started_at}")


# create a scheduler object
sc = scheduler()


# schedule calling a function repeatedly
# with a delay of 10 seconds between calls
sc.repeat(delay=10, priority=1, action=echo_time_elapsed)


# schedule a funcion by decorating it
@sc.every(delay=15, priority=0)
def print_current_time():
    iso_dt = datetime.utcnow().isoformat()
    print(f"decorated function - {iso_dt}")


# you can also use datetime.timedelta objects
# see: https://docs.python.org/3/library/datetime.html#timedelta-objects
@sc.every(delay=timedelta(minutes=1), priority=0)
def echo_iso_date_every_minute():
    iso_dt = datetime.utcnow().isoformat()
    print(f"decorated function with timedelta - {iso_dt}")


# run the scheduler
sc.run()
```
