import math
import prometheus_client


class Prometheus:
    def __init__(self, run: str, prometheus_port: int) -> None:
        self._run = run

        prometheus_client.start_http_server(prometheus_port)

        self._request_latency_metric = prometheus_client.Histogram(
            name="request_total_latency_seconds",
            documentation="Total latency of request in seconds",
            labelnames=["run"],
            buckets=[
                0.005, 0.01, 0.025, 0.05, 0.075, 0.1,
                0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0,
                15.0, 20.0, 25.0, 30.0, 40.0, 80.0, 160.0,
                320.0, 640.0, math.inf,
            ],
        )

        self._request_time_to_first_token_latency_metric = prometheus_client.Histogram(
            name="request_time_to_first_token_latency_seconds",
            documentation="Time to first token latency in seconds",
            labelnames=["run"],
            buckets=[
                0.005, 0.01, 0.025, 0.05, 0.075, 0.1,
                0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0,
                15.0, 20.0, 25.0, 30.0, 40.0, 80.0, 160.0,
                320.0, 640.0, math.inf,
            ],
        )

        self._request_time_per_output_token_latency_metric = prometheus_client.Histogram(
            name="request_time_per_output_token_latency_seconds",
            documentation="Time per output token latency in seconds",
            labelnames=["run"],
            buckets=[
                0.005, 0.01, 0.025, 0.05, 0.075, 0.1,
                0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0,
                15.0, 20.0, 25.0, 30.0, 40.0, 80.0, 160.0,
                320.0, 640.0, math.inf,
            ],
        )

        self._requests_count_metric = prometheus_client.Counter(
            name="requests_count",
            documentation="Total number of requests that are coming to server",
            labelnames=["run"]
        )

        self._users_count = prometheus_client.Gauge(
            name="users",
            documentation="Number of users sending requests",
            labelnames=["run"]
        )

        self._prefill_tokens = prometheus_client.Histogram(
            name="prefill_tokens",
            documentation="Number of prefill tokens processed",
            labelnames=["run"],
            buckets=[
                1, 2, 4, 8, 16, 32, 64, 128, 256, 512,
                1024, 2048, 4096, 8192, 16384, 32768,
                65536, 131072, 262144, 524288, 1048576, math.inf
            ]
        )

        self._decode_tokens = prometheus_client.Histogram(
            name="decode_tokens",
            documentation="Number of decode tokens processed",
            labelnames=["run"],
            buckets=[
                1, 2, 4, 8, 16, 32, 64, 128, 256, 512,
                1024, 2048, 4096, 8192, 16384, 32768,
                65536, 131072, 262144, 524288, 1048576, math.inf
            ]
        )

        self._response_code_count_metric = prometheus_client.Counter(
            name="response_code",
            documentation="Total number of errors",
            labelnames=["run", "code"]
        )

    def request_latency_metric(self, latency: float) -> None:
        self._request_latency_metric.labels(run=self._run).observe(latency)

    def request_time_to_first_token_latency_metric(self, latency: float) -> None:
        self._request_time_to_first_token_latency_metric.labels(run=self._run).observe(latency)

    def request_time_per_output_token_latency_metric(self, latency: float) -> None:
        self._request_time_per_output_token_latency_metric.labels(run=self._run).observe(latency)

    def requests_count_metric(self) -> None:
        self._requests_count_metric.labels(run=self._run).inc()

    def increase_users_count(self) -> None:
        self._users_count.labels(run=self._run).inc()

    def decrease_users_count(self) -> None:
        self._users_count.labels(run=self._run).dec()

    def prefill_tokens(self, tokens: int) -> None:
        self._prefill_tokens.labels(run=self._run).observe(tokens)

    def decode_tokens(self, tokens: int) -> None:
        self._decode_tokens.labels(run=self._run).observe(tokens)

    def response_code_count_metric(self, code: str) -> None:
        self._response_code_count_metric.labels(run=self._run, code=code).inc()
