The `sched2` module is a subclass of Python's `sched.scheduler`, designed for interval-based task scheduling. It extends the standard sched module with additional features such as the `repeat` method and the `every` decorator, allowing for regular interval-based execution of functions. It's a practical tool for automating tasks that need to run repeatedly after certain time delays.

# Install

To install the `sched2` module, you can use `pip`, the package installer for Python. Open a terminal and run the following command:

```bash
pip install sched2
```

# Examples

The code bellow defines a function that checks if the IP address has changed and prints a message if it has. Then it creates an instance of a scheduler class and uses the `repeat` method to schedule the IP check function to run every two minutes. Finally, it starts the scheduler, so the IP check function will run indefinitely.

```python
from urllib.request import urlopen
from sched2 import scheduler


def check_ip():
    # Get the public IP address
    global current_ip
    ip = urlopen("https://icanhazip.com/").read().decode("utf-8").strip()

    # Check if the IP address has changed
    if ip != current_ip:
        current_ip = ip
        print(f"IP changed to {ip}")


# Initialize the current_ip variable to None
current_ip = None

# Create a scheduler
sc = scheduler()

# Run the check_ip function every 120 seconds
sc.repeat(120, 1, check_ip)

# Run the scheduler
sc.run()
```

The following code creates an instance of a scheduler class and decorates a function, so it runs every two minutes. First, the decorated function gets the public IP address and checks if it has changed. If it has, it updates and prints a message. Finally, it starts the scheduler, so the decorated function runs indefinitely.

```python
from urllib.request import urlopen
from sched2 import scheduler

# Create a scheduler
sc = scheduler()


@sc.every(120)  # Run every two minutes
def check_ip():
    # Get the public IP address and check if it has changed
    global current_ip
    ip = urlopen("https://icanhazip.com/").read().decode("utf-8").strip()
    if ip != current_ip:
        current_ip = ip
        print(f"IP changed to {ip}")


# Initialize the current_ip variable to None
current_ip = None

# Run the scheduler
sc.run()
```

# Source Code and Issues

Help improve sched2 by reporting any issues or suggestions on the issue tracker at [github.com/medecau/sched2/issues](https://github.com/medecau/sched2/issues).
