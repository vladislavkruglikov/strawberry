import time
import openai
import typing
import asyncio

from strawberry.prometheus import Prometheus


class User:
    def __init__(self, prometheus: Prometheus, wait: typing.Callable) -> None:
        self._prometheus = prometheus
        self._client = openai.AsyncOpenAI(
            base_url="http://server:8000/v1",
            api_key="token",
        )
        self._wait = wait
    
    async def start(self) -> None:
        while True:
            await self.request()
            await asyncio.sleep(self._wait())

    async def request(self) -> None:
        start_time = time.time()
        stream = await self._client.chat.completions.create(
            model="Qwen/Qwen2.5-0.5B-Instruct",
            messages=[
                {"role": "user", "content": "Hello!"}
            ],
            stream=True
        )

        is_first_chunk = True
        previous_chunk_end_time = None
        async for chunk in stream:
            if is_first_chunk:
                time_to_first_token = time.time() - start_time
                self._prometheus.request_time_to_first_token_latency_metric(time_to_first_token)
                is_first_chunk = False
            else:
                time_per_output_token = time.time() - previous_chunk_end_time
                self._prometheus.request_time_per_output_token_latency_metric(time_per_output_token)
            
            previous_chunk_end_time = time.time()
            
        total_latency = time.time() - start_time
        self._prometheus.request_latency_metric(total_latency)
