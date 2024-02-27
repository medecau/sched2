The `sched2` module extends the general purpose event scheduler `sched` from Python's standard library. `sched2.scheduler` is a subclass of `sched.scheduler` that adds new features such as the `every` and `cron` decorators. It's a practical tool for automating tasks that need to run repeatedly after certain time delays or at specific times.

# Install

To install the `sched2` module, you can use `pip`, the package installer for Python. Open a terminal and run the following command:

```bash
pip install sched2
```

# Examples

The code below uses the `every` decorator to schedule checking the public IP address every two minutes.

```python
from urllib.request import urlopen
from sched2 import scheduler

# Create a scheduler
sc = scheduler()


@sc.every(120)  # Run every two minutes
def print_ip_address():
    ip = urlopen("https://icanhazip.com/").read().decode("utf-8").strip()
    print(f"Public IP address: {ip}")

# Run the scheduler
sc.run()
```


The following code does something similar, but here we use the `cron` decorator to schedule an email report to be sent every weekday at 9:00.

```python
from smtplib import SMTP_SSL
from sched2 import scheduler

# Create a scheduler
sc = scheduler()


@sc.cron("0 9 * * 1-5")  # Run every weekday at 9:00
def send_report():
    with SMTP_SSL("smtp.example.com") as smtp:
        smtp.login("me@example.com", "password")
        smtp.sendmail(
            "me@example.com",
            "team@example.com",
            "Subject: Daily Report\n\nThe numbers are up!",
        )


# Run the scheduler
sc.run()
```

# Source Code and Issues

Help improve sched2 by reporting any issues or suggestions on the issue tracker at [github.com/medecau/sched2/issues](https://github.com/medecau/sched2/issues).
