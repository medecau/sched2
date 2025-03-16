````python notest
import sched2
sc = sched2.scheduler()

@sc.every(5)
def magic():
    ```python
    print("✨ Magic sparkles every five seconds! ✨")
    ```

sc.run()
````

The `sched2` module extends the general purpose event scheduler `sched` from Python's standard library. `sched2.scheduler` is a subclass of `sched.scheduler` that adds new features such as the `every` and `cron` decorators. It's a practical tool for automating tasks that need to run repeatedly after certain time delays or at specific times.

# Install

`sched2` is available on PyPI.

```bash
pip install sched2
```

# How to use

```python notest
from urllib.request import urlopen
import sched2

# create the scheduler
sc = sched2.scheduler()

# we'll use this to remember the last IP address between runs
last_ip = None


@sc.every(10)  # seconds
def check_ip_address():
    global last_ip  # in case we need to update this

    # get the current IP address
    current_ip = urlopen("https://icanhazip.com/").read().decode("utf-8").strip()

    # if the IP address has changed
    if last_ip != current_ip:
        last_ip = current_ip

        # emit an event to notify the change
        sc.emit("ip_changed", kwargs={"new_ip": current_ip})

@sc.on("ip_changed")  # 'ip_changed' is the event name
def notify_ip_change(new_ip):  # 'new_ip' is the keyword argument passed to the event
    print(f'Your IP address has changed to {new_ip}')

@sc.cron("0 9 * * 1-5")  # every weekday at 9:00
def daily_greeting():
    print(f'Good morning, your current IP address is {last_ip}')

sc.run()
```

# Source Code and Issues

The source code for `sched2` is available on GitHub at [github.com/medecau/sched2](https://github.com/medecau/sched2).

You can help improve sched2 by reporting any issues or suggestions on the issue tracker at [github.com/medecau/sched2/issues](https://github.com/medecau/sched2/issues).
