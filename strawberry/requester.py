import time
import openai
from loguru import logger
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
            logger.debug("Start to send request for request {}", request)
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
                    logger.debug("Get last chunk {} for request {}", chunk, request)
                else:
                    if is_first_chunk:
                        logger.debug("Get first chunk {} for request {}", chunk, request)
                        role = chunk.choices[0].delta.role
                        time_to_first_token = time.time() - start_time
                        logger.debug("time_to_first_token={}", time_to_first_token)
                        self._prometheus.request_time_to_first_token_latency_metric(time_to_first_token)
                        is_first_chunk = False
                    else:
                        logger.debug("Get next chunk {} for request {}", chunk, request)
                        time_per_output_token = time.time() - previous_chunk_end_time
                        logger.debug("time_per_output_token={}", time_per_output_token)
                        self._prometheus.request_time_per_output_token_latency_metric(time_per_output_token)
                    previous_chunk_end_time = time.time()
                    chunks.append(chunk.choices[0].delta.content)
            total_latency = time.time() - start_time
            logger.debug("total_latency={}, output_text={}", total_latency, output_text)
            self._prometheus.request_latency_metric(total_latency)
            output_text = "".join(chunks)
        except openai.APIConnectionError as e:
            logger.debug("The server could not be reached")
            logger.debug("Exception: {}", e.__cause__)
            status_code = 503
        except openai.RateLimitError as e:
            logger.debug("A 429 status code was received; we should back off a bit.")
            status_code = e.status_code
        except openai.APIStatusError as e:
            logger.debug("Another non-200-range status code was received")
            logger.debug("Status code: {}", e.status_code)
            logger.debug("Response: {}", e.response)
            status_code = e.status_code
        except Exception as e:
            logger.debug("Got exception {}, {}", type(e), e)
            status_code = 400
        self._prometheus.response_code_count_metric(code=status_code)
        response = {
            "custom_id": request["custom_id"],
            "status_code": status_code,
            "response": {
                "role": role,
                "content": output_text
            },
            "error": error
        }

        logger.debug("response is {}", response)
        return response
