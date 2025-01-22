import time
import typing
import asyncio

from loguru import logger
from strawberry.requester import Requester
from strawberry.dataset import Sampler, OutputDataset


class User:
    def __init__(self, requester: Requester, wait: typing.Callable, dataset: Sampler, output_dataset_writer: OutputDataset) -> None:
        self._wait = wait
        self._dataset = dataset
        self._requester = requester
        self._output_dataset_writer = output_dataset_writer

    async def start(self) -> None:
        async for request, is_last in self._dataset:
            res = await self._requester.request(request)            
            await self._output_dataset_writer.write_single_response(res)
            if not is_last:
                await asyncio.sleep(self._wait())
        
        logger.info("User finished processing")
