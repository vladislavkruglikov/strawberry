import time
import openai
import typing
import asyncio

from strawberry.dataset import Dataset
from strawberry.prometheus import Prometheus


class User:
    def __init__(self, prometheus: Prometheus, wait: typing.Callable, dataset: Dataset) -> None:
        self._prometheus = prometheus
        self._client = openai.AsyncOpenAI(
            base_url="http://server:8000/v1",
            api_key="token",
        )
        self._wait = wait
        self._dataset = dataset
    
    async def start(self) -> None:
        while True:
            await self.request()
            await asyncio.sleep(self._wait())

    async def request(self) -> None:
        self._prometheus.requests_count_metric()

        start_time = time.time()
        stream = await self._client.chat.completions.create(
            model="Qwen/Qwen2.5-0.5B-Instruct",
            messages=[
                {"role": "user", "content": self._dataset.get_random_prompt()}
            ],
            stream=True,
            stream_options={"include_usage": True}
        )

        is_first_chunk = True
        previous_chunk_end_time = None
        async for chunk in stream:
            if len(chunk.choices) == 0:
                # last chunk contains usage info https://platform.openai.com/docs/api-reference/chat/streaming
                # and no output info
                self._prometheus.prefill_tokens(chunk.usage.prompt_tokens)
                self._prometheus.decode_tokens(chunk.usage.completion_tokens)
            else:
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
