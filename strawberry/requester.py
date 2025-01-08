import time
import openai

from strawberry.prometheus import Prometheus


class Requester:
    """
    Wrapper around OpenAI client that updates Prometheus metrics.

    This class provides functionality to interact with the OpenAI API while logging
    metrics to Prometheus for monitoring and performance evaluation.

    Attributes:
        _client (openai.AsyncOpenAI): The OpenAI client used to send requests.
        _model_name (str): The name of the model used for requests.
        _prometheus (Prometheus): The Prometheus instance used for logging metrics.
    """

    def __init__(self, prometheus: Prometheus, base_url: str, api_key: str, model_name: str) -> None:
        """
        Initializes the Requester instance.

        Args:
            prometheus (Prometheus): The Prometheus instance used for logging metrics.
            base_url (str): The base URL for the OpenAI API.
            api_key (str): The API key for authenticating with the OpenAI API.
            model_name (str): The name of the OpenAI model to use for requests.
        """
        self._client = openai.AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        self._model_name = model_name
        self._prometheus = prometheus

    async def request(self, messages: list) -> None:
        """
        Sends a request to the OpenAI API and logs metrics to Prometheus.

        Args:
            messages (list): A list of message dictionaries to be sent to the OpenAI API.

        The method tracks and logs the following metrics:
        - Total request count.
        - Time to the first token from the API.
        - Time per output token received.
        - Total latency for the request.
        - Prefill and decode token counts from the last chunk.

        Raises:
            openai.error.OpenAIError: If there is an error during the API request.
        """
        self._prometheus.requests_count_metric()

        start_time = time.time()
        stream = await self._client.chat.completions.create(
            model=self._model_name,
            messages=messages,
            stream=True,
            stream_options={"include_usage": True}
        )

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
                    time_to_first_token = time.time() - start_time
                    self._prometheus.request_time_to_first_token_latency_metric(time_to_first_token)
                    is_first_chunk = False
                else:
                    time_per_output_token = time.time() - previous_chunk_end_time
                    self._prometheus.request_time_per_output_token_latency_metric(time_per_output_token)

                previous_chunk_end_time = time.time()

        total_latency = time.time() - start_time
        self._prometheus.request_latency_metric(total_latency)
