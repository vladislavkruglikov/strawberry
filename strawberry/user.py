import time
import typing
import asyncio

from strawberry.dataset import Dataset
from strawberry.requester import Requester


class User:
    # program some waiting between requests logic and sampling input data for requests
    # probably user might have some memory or stuff
    def __init__(self, requester: Requester, wait: typing.Callable, dataset: Dataset) -> None:
        self._wait = wait
        self._dataset = dataset
        self._requester = requester
    
    async def start(self) -> None:
        while True:
            await self._requester.request(messages=[{"role": "user", "content":  self._dataset.get_random_prompt()}])
            await asyncio.sleep(self._wait())
