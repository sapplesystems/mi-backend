#  locust -f benchmark_with_get_url.py --headless -u 2 -t 5
import datetime
import json

from locust import HttpUser, task, constant_throughput, constant_pacing
from locust import events


def timestring():
    now = datetime.datetime.now()
    return datetime.datetime.strftime(now, "%m:%S.%f")[:-5]


# print("1. Starting benchmarking at " + timestring())

# If you want to get something over HTTP at this time you can use `requests` directly:


queue = None
file_appender = None


@events.init.add_listener
def _(environment, **_kwargs):
    global queue
    queue = []


@events.quitting.add_listener
def _(environment, **_kwargs):
    print("9. Shutting down!!")


class MIIGetInfo(HttpUser):
    wait_time = constant_throughput(5)  # request per second

    # wait_time = constant_pacing(1) # request every second
    def on_start(self):
        # print("user was started")
        # This is a good place to fetch user-specific test data. It is executed once per User
        # If you do not want the request logged, you can replace self.client.<method> with requests.<method>

    @task
    def t(self):
        # http://mi-backend.qci.solutions/api/v1/product/bce9145f2338445ab6bfb203cf07b96a/D1S1500388/
        response = self.client.get(f"/api/v1/product/bce9145f2338445ab6bfb203cf07b96a/D1S1500388/")
        if response.status_code == 200:
            # print(response.json())
        else:
            # print(f"Error: {response.status_code} {response.text}")

    def on_stop(self):
        # this is a good place to clean up/release any user-specific test data
        # print("user was stopped")
