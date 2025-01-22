import time
import openai

from strawberry.prometheus import Prometheus


class Requester:
    def __init__(self, prometheus: Prometheus, base_url: str, api_key: str, model_name: str) -> None:
        self._client = openai.AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        self._model_name = model_name
        self._prometheus = prometheus

    async def request(self, request: dict) -> None:
        self._prometheus.requests_count_metric()
        start_time = time.time()
        role = None
        output_text = None
        error = None
        status_code = 200
        try:
            stream = await self._client.chat.completions.create(
                model=self._model_name,
                stream=True,
                stream_options={"include_usage": True},
                **request["body"],
            )
            chunks = []
            is_first_chunk = True
            previous_chunk_end_time = None
            async for chunk in stream:
                if len(chunk.choices) == 0:
                    # Last chunk contains usage info and no output info.
                    # See: https://platform.openai.com/docs/api-reference/chat/streaming
                    self._prometheus.prefill_tokens(chunk.usage.prompt_tokens)
                    self._prometheus.decode_tokens(chunk.usage.completion_tokens)
                else:
                    if is_first_chunk:
                        role = chunk.choices[0].delta.role
                        time_to_first_token = time.time() - start_time
                        self._prometheus.request_time_to_first_token_latency_metric(time_to_first_token)
                        is_first_chunk = False
                    else:
                        time_per_output_token = time.time() - previous_chunk_end_time
                        self._prometheus.request_time_per_output_token_latency_metric(time_per_output_token)
                    previous_chunk_end_time = time.time()
                    chunks.append(chunk.choices[0].delta.content)
            total_latency = time.time() - start_time
            self._prometheus.request_latency_metric(total_latency)
            output_text = "".join(chunks)
        except Exception as e:
            status_code = e.status_code
            error = e.response.json()["message"]
        self._prometheus.response_code_count_metric(code=status_code)
        return {
            "custom_id": request["custom_id"],
            "status_code": status_code,
            "response": {
                "role": role,
                "content": output_text
            },
            "error": error
        }
