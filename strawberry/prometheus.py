import math
import prometheus_client


class Prometheus:
    """
    Wrapper class for Prometheus metrics collection and exposure.

    This class provides methods to track and expose various metrics related to 
    request latency, token processing, and user activity in a Prometheus-compatible format.

    Attributes:
        _run (str): The identifier for the current run, used as a label in all metrics.
        _request_latency_metric (prometheus_client.Histogram): Histogram tracking total request latency in seconds.
        _request_time_to_first_token_latency_metric (prometheus_client.Histogram): Histogram tracking time to first token latency in seconds.
        _request_time_per_output_token_latency_metric (prometheus_client.Histogram): Histogram tracking latency per output token in seconds.
        _requests_count_metric (prometheus_client.Counter): Counter for the total number of incoming requests.
        _users_count (prometheus_client.Counter): Counter for the total number of users sending requests.
        _prefill_tokens (prometheus_client.Histogram): Histogram tracking the number of prefill tokens processed.
        _decode_tokens (prometheus_client.Histogram): Histogram tracking the number of decode tokens processed.
    """

    def __init__(self, run: str, prometheus_port: int) -> None:
        """
        Initializes the Prometheus instance and starts the HTTP server to expose metrics.

        Args:
            run (str): The identifier for the current run, used as a label in all metrics.
        """
        self._run = run

        prometheus_client.start_http_server(prometheus_port)

        self._request_latency_metric = prometheus_client.Histogram(
            name="request_total_latency_seconds",
            documentation="Total latency of request in seconds",
            labelnames=["run"],
            buckets=[
                0.005, 0.01, 0.025, 0.05, 0.075, 0.1,
                0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, math.inf,
            ],
        )

        self._request_time_to_first_token_latency_metric = prometheus_client.Histogram(
            name="request_time_to_first_token_latency_seconds",
            documentation="Time to first token latency in seconds",
            labelnames=["run"],
            buckets=[
                0.005, 0.01, 0.025, 0.05, 0.075, 0.1,
                0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, math.inf,
            ],
        )

        self._request_time_per_output_token_latency_metric = prometheus_client.Histogram(
            name="request_time_per_output_token_latency_seconds",
            documentation="Time per output token latency in seconds",
            labelnames=["run"],
            buckets=[
                0.005, 0.01, 0.025, 0.05, 0.075, 0.1,
                0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, math.inf,
            ],
        )

        self._requests_count_metric = prometheus_client.Counter(
            name="requests_count",
            documentation="Total number of requests that are coming to server",
            labelnames=["run"]
        )

        self._users_count = prometheus_client.Counter(
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

    def request_latency_metric(self, latency: float) -> None:
        """
        Observes the total latency of a request.

        Args:
            latency (float): The total latency of the request in seconds.
        """
        self._request_latency_metric.labels(run=self._run).observe(latency)

    def request_time_to_first_token_latency_metric(self, latency: float) -> None:
        """
        Observes the latency to the first token of a request.

        Args:
            latency (float): The latency to the first token in seconds.
        """
        self._request_time_to_first_token_latency_metric.labels(run=self._run).observe(latency)

    def request_time_per_output_token_latency_metric(self, latency: float) -> None:
        """
        Observes the latency per output token.

        Args:
            latency (float): The latency per output token in seconds.
        """
        self._request_time_per_output_token_latency_metric.labels(run=self._run).observe(latency)

    def requests_count_metric(self) -> None:
        """
        Increments the counter for the total number of requests.
        """
        self._requests_count_metric.labels(run=self._run).inc()

    def increase_users_count(self) -> None:
        """
        Increments the counter for the total number of users.
        """
        self._users_count.labels(run=self._run).inc()

    def prefill_tokens(self, tokens: int) -> None:
        """
        Observes the number of prefill tokens processed.

        Args:
            tokens (int): The number of prefill tokens processed.
        """
        self._prefill_tokens.labels(run=self._run).observe(tokens)

    def decode_tokens(self, tokens: int) -> None:
        """
        Observes the number of decode tokens processed.

        Args:
            tokens (int): The number of decode tokens processed.
        """
        self._decode_tokens.labels(run=self._run).observe(tokens)
