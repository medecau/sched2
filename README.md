The `sched2` module extends the general purpose event scheduler `sched` from Python's standard library. `sched2.scheduler` is a subclass of `sched.scheduler` that adds new features such as the `every` and `cron` decorators. It's a practical tool for automating tasks that need to run repeatedly after certain time delays or at specific times.

# Install

`sched2` is available on PyPI.

```bash
pip install sched2
```

# Examples

The code below uses the `every` decorator to schedule checking the public IP address every two minutes.
Then every day at 9:00, the `cron` decorator is used to send a report via email.
Finally, the `on` decorator is used to send an email when the IP address changes.


```python
from smtplib import SMTP_SSL
from urllib.request import urlopen

from sched2 import scheduler

# Create a scheduler
sc = scheduler()

# we'll use this to remember the last IP address between runs
last_ip = None


@sc.every(30)  # Run every two minutes
def print_ip_address():
    global last_ip

    ip = urlopen("https://icanhazip.com/").read().decode("utf-8").strip()

    print(f"Public IP address: {ip}")

    last_ip = last_ip or ip  # reset last_ip
    if ip != last_ip:
        last_ip = ip

        # Emit an event when the IP address changes
        sc.emit("ip_changed", kwargs={"new_ip": ip})


@sc.cron("0 9 * * 1-5")  # Run every weekday at 9:00
def send_report():
    sendmail("Daily Report", "The numbers are up!")


@sc.on("ip_changed")  # Run when 'ip_changed' event is emitted
def send_email(new_ip):
    sendmail("IP Address Changed", f"New IP address: {ip}")


def sendmail(subject, body):
    """Send an email using SMTP_SSL."""
    with SMTP_SSL("smtp.example.com") as smtp:
        smtp.login("me@example.com", "password")
        smtp.sendmail(
            "me@example.com",
            "team@example.com",
            f"{subject}\n\n{body}",
        )


# Run the scheduler
sc.run()

```

# Source Code and Issues

The source code for `sched2` is available on GitHub at [github.com/medecau/sched2](https://github.com/medecau/sched2).

You can help improve sched2 by reporting any issues or suggestions on the issue tracker at [github.com/medecau/sched2/issues](https://github.com/medecau/sched2/issues).
