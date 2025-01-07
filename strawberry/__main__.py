import time
import random
import prometheus_client


request_counter = prometheus_client.Counter(
    'requests_count', 
    'Count of all requests', 
    ['run']
)


if __name__ == "__main__":
    print("Start to run 🍓 Strawberry")

    prometheus_client.start_http_server(8000)

    while True:
        request_counter.labels(run="example_run_4").inc(random.randint(1, 5))
        time.sleep(1)
