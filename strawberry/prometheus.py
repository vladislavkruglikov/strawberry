import math
import prometheus_client


class Prometheus:
    def __init__(self, run: str) -> None:
        self._run = run

        prometheus_client.start_http_server(8000)
        
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
    
    def request_latency_metric(self, latency: float) -> None:
        self._request_latency_metric.labels(run=self._run).observe(latency)
    
    def request_time_to_first_token_latency_metric(self, latency: float) -> None:
        self._request_time_to_first_token_latency_metric.labels(run=self._run).observe(latency)
    
    def request_time_per_output_token_latency_metric(self, latency: float) -> None:
        self._request_time_per_output_token_latency_metric.labels(run=self._run).observe(latency)
