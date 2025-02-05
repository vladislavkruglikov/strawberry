import time
import json
import httpx
import openai
from loguru import logger
from strawberry.prometheus import Prometheus


class Requester:
    def __init__(self, prometheus: Prometheus, base_url: str, api_key: str, model_name: str) -> None:
        self._client = openai.AsyncOpenAI(base_url=base_url, api_key=api_key)
        self._model_name = model_name
        self._prometheus = prometheus

    async def request(self, request: dict) -> dict:
        self._prometheus.requests_count_metric()
        start_time = time.time()
        prefill_start_time = start_time
        decode_start_time = None
        role = None
        output_text = None
        error = None
        status_code = 200
        chunks = []
        is_first_chunk = True
        previous_chunk_end_time = None

        try:
            logger.debug("Start to send request for request {}", request)
            stream = await self._client.chat.completions.create(
                model=self._model_name,
                stream=True,
                stream_options={"include_usage": True},
                **request["body"],
            )

            async for chunk in stream:
                if len(chunk.choices) == 0:
                    self._prometheus.prefill_tokens(chunk.usage.prompt_tokens)
                    self._prometheus.decode_tokens(chunk.usage.completion_tokens)
                    if decode_start_time is not None:
                        decode_time = time.time() - decode_start_time
                        self._prometheus.decode_time_metric(decode_time)
                    logger.debug("Get last chunk {} for request {}", chunk, request)
                else:
                    if is_first_chunk:
                        logger.debug("Get first chunk {} for request {}", chunk, request)
                        role = chunk.choices[0].delta.role
                        time_to_first_token = time.time() - start_time
                        logger.debug("time_to_first_token={}", time_to_first_token)
                        self._prometheus.request_time_to_first_token_latency_metric(time_to_first_token)
                        prefill_time = time.time() - prefill_start_time
                        self._prometheus.prefill_time_metric(prefill_time)
                        decode_start_time = time.time()
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

        self._prometheus.response_code_count_metric(code=str(status_code))
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


class SglangRequester:
    def __init__(self, prometheus: Prometheus, base_url: str, api_key: str, model_name: str) -> None:
        self._model_name = model_name
        self._prometheus = prometheus
        self._base_url = base_url

    async def request(self, request: dict) -> dict:
        self._prometheus.requests_count_metric()
        start_time = time.time()
        prefill_start_time = start_time
        decode_start_time = None

        status_code = 200
        is_first_chunk = True
        previous_chunk_end_time = None
        error = None
        role = None

        completion_tokens = None # sglang streaming returns running completion tokens

        try:
            payload = request["body"]
            payload["stream"] = True

            headers = {
                # "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient() as client:
                url = f"{self._base_url}/generate"
                logger.info("Sending request to {} with payload {}", url, payload)
                async with client.stream("POST", url, json=payload, headers=headers) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line and line.startswith("data:"):
                            data_str = line[5:].strip()
                            if data_str == "[DONE]":
                                break                            
                            try:
                                data = json.loads(data_str)
                            except json.JSONDecodeError as e:
                                logger.info("Skipping invalid JSON chunk: {}", e)
                                continue

                            # logger.info(f"\n\n{data}\n\n")
                            chunk_text = data.get("text", "")
                            
                            if "meta_info" in data and "completion_tokens" in data["meta_info"]:
                                completion_tokens = data["meta_info"]["completion_tokens"]

                            if is_first_chunk:
                                prompt_tokens = data["meta_info"]["prompt_tokens"]
                                self._prometheus.prefill_tokens(prompt_tokens)
                                logger.debug(f"log prompt_tokens = {prompt_tokens}")

                                time_to_first_token = time.time() - start_time
                                self._prometheus.request_time_to_first_token_latency_metric(time_to_first_token)
                                prefill_time = time.time() - prefill_start_time
                                self._prometheus.prefill_time_metric(prefill_time)
                                decode_start_time = time.time()
                                is_first_chunk = False
                            else:
                                if previous_chunk_end_time is not None:
                                    time_per_output_token = time.time() - previous_chunk_end_time
                                    self._prometheus.request_time_per_output_token_latency_metric(time_per_output_token)

                            previous_chunk_end_time = time.time()

                if decode_start_time is not None:
                    decode_time = time.time() - decode_start_time
                    self._prometheus.decode_time_metric(decode_time)
            
            if completion_tokens is not None:
                logger.debug(f"log decode_tokens = {completion_tokens}")
                self._prometheus.decode_tokens(completion_tokens)

            total_latency = time.time() - start_time
            self._prometheus.request_latency_metric(total_latency)
            logger.info("total_latency={}", total_latency)

        except httpx.ConnectError as e:
            logger.error("❌ Could not connect to server: {}", e)
            status_code = 503
        except httpx.HTTPStatusError as e:
            logger.error("❌ Non-200 status code: {}", e)
            status_code = e.response.status_code
        except Exception as e:
            logger.error("❌ Got exception {}, {}", type(e), e)
            status_code = 400

        self._prometheus.response_code_count_metric(code=str(status_code))
        response_data = {
            "custom_id": request.get("custom_id"),
            "status_code": status_code,
            "response": {
                "data": data
            },
            "error": error
        }
        # logger.info("response is {}", str(response_data)[:10])
        return response_data
