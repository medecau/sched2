The `sched2` module provides a simple and intuitive way to schedule the execution of code in Python. For example, it allows you to schedule a function to be called at a specific time or after a particular delay or to schedule a function to be called repeatedly at a specific time interval. This can be useful for automating tasks or scheduling the execution of code without having to write your own scheduling logic. In addition, it is lightweight and easy to use, making it an excellent choice for scheduling the execution of code in Python.

`sched2` implements a subclass of the `sched.scheduler` class from Python's standard library that adds additional functionality. This means that `sched2` includes all of the features and functionality of the `sched` module and adds extra methods. As a result, you can use `sched2` in place of `sched` in your code without any further modifications, and you will have access to the additional features provided by `sched2`. These other features include the `repeat` method and the `every` decorator, which allow you to repeatedly schedule a function to be called at a specific time interval.

# Functionality
- Schedule the execution of code at specific times or intervals
- Schedule repeat function calls at specific time intervals
- Simple and intuitive interface for scheduling code
- Lightweight and easy to use
- No external dependencies

# Install

To install the sched2 module, you can use pip, the package installer for Python. Open a terminal and run the following command:

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
