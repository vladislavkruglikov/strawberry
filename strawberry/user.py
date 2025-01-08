import time
import typing
import asyncio

from strawberry.dataset import Dataset
from strawberry.requester import Requester


class User:
    """
    Handles user interactions by managing request logic, waiting between requests, and sampling input data.

    This class simulates a user that sends requests to a server using a provided requester instance.
    The user logic includes programmable waiting times between requests and sampling prompts from a dataset.

    Attributes:
        _wait (typing.Callable): A callable function to determine wait time between requests.
        _dataset (Dataset): The dataset from which input prompts are sampled.
        _requester (Requester): The requester instance used to send requests.
    """

    def __init__(self, requester: Requester, wait: typing.Callable, dataset: Dataset) -> None:
        """
        Initializes the User instance.

        Args:
            requester (Requester): The requester instance to handle API requests.
            wait (typing.Callable): A callable function that returns the wait time between requests in seconds.
            dataset (Dataset): The dataset instance used to provide random prompts for requests.
        """
        self._wait = wait
        self._dataset = dataset
        self._requester = requester

    async def start(self) -> None:
        """
        Starts the user simulation loop.

        The user continuously sends requests using the requester instance with prompts sampled
        from the dataset. Between requests, the user waits for a time determined by the `_wait` function.

        The loop runs indefinitely.

        Raises:
            Exception: If an error occurs during a request or dataset sampling.
        """
        while True:
            await self._requester.request(messages=[{"role": "user", "content": self._dataset.get_random_prompt()}])
            await asyncio.sleep(self._wait())
