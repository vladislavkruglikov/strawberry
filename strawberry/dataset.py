import os
import json
import random
import asyncio
import aioboto3

from pathlib import Path
from loguru import logger
from abc import ABC, abstractmethod
from aiofiles import open as aio_open



class InputDataset(ABC):
    @abstractmethod
    async def read_all_data(self, path: Path) -> list[dict]:
        ...


class OutputDataset(ABC):
    @abstractmethod
    async def get_processed_ids(self) -> list[int]:
        ...

    @abstractmethod
    async def write_single_response(self, dict) -> None:
        ...


class LocalInputDataset(InputDataset):
    def __init__(self, path):
        self._path = path
    
    async def read_all_data(self) -> list[dict]:
        with open(self._path, 'r', encoding='utf-8') as file:
            dataset = [json.loads(line.strip()) for line in file if line.strip()]
            return dataset


class DummyOutputDataset(OutputDataset):
    async def get_processed_ids(self) -> list[int]:
        return set()
    
    async def write_single_response(self, response: dict) -> None:
        ...


class LocalOutputDataset(OutputDataset):
    def __init__(self, save_path: Path) -> None:
        self._save_path = save_path
        if not self._save_path.exists():
            self._save_path.mkdir(parents=True, exist_ok=True)

    async def get_processed_ids(self) -> list[int]:
        processed = []
        for root, dirs, files in os.walk(self._save_path):
            for filename in files:
                name, ext = os.path.splitext(filename)
                processed.append(int(name))
        return set(processed)

    async def write_single_response(self, response: dict) -> None:
        custom_id = response.get("custom_id")
        file_path = self._save_path / f"{custom_id}.json"
        content = json.dumps(response, indent=4, ensure_ascii=False)
        async with aio_open(file_path, 'w') as file:
            await file.write(content)


class S3OutputDataset(OutputDataset):
    def __init__(self, aws_access_key: str, aws_secret_key: str, bucket: str, address: str, base_path: str, output_s3_region_name: str) -> None:
        self._aws_access_key = aws_access_key
        self._aws_secret_key = aws_secret_key
        self._bucket = bucket
        self._address = address
        self._base_path = base_path.rstrip('/')
        self._s3_client = aioboto3.Session()
        self._output_s3_region_name = output_s3_region_name
    
    async def get_processed_ids(self) -> list[int]:
        processed = set()
        async with self._s3_client.client(
            service_name="s3",
            aws_access_key_id=self._aws_access_key,
            aws_secret_access_key=self._aws_secret_key,
            endpoint_url=self._address,
            region_name=self._output_s3_region_name
        ) as s3_client:
            paginator = s3_client.get_paginator("list_objects_v2")
            async for page in paginator.paginate(Bucket=self._bucket, Prefix=self._base_path):
                for obj in page.get("Contents", []):
                    key = obj["Key"]
                    filename = os.path.basename(key)
                    name, ext = os.path.splitext(filename)
                    if ext == ".json":
                        try:
                            processed.add(int(name))
                        except ValueError:
                            pass
        return processed
    
    async def write_single_response(self, response: dict) -> None:
        custom_id = response.get("custom_id")
        if custom_id is None:
            raise ValueError("Response must contain a 'custom_id' field.")
        object_key = f"{self._base_path}/{custom_id}.json"
        content_str = json.dumps(response, indent=4, ensure_ascii=False)
        content_bytes = content_str.encode("utf-8")
        async with self._s3_client.client(
            service_name="s3",
            aws_access_key_id=self._aws_access_key,
            aws_secret_access_key=self._aws_secret_key,
            endpoint_url=self._address,
            region_name=self._output_s3_region_name
        ) as s3_client:
            await s3_client.put_object(
                Bucket=self._bucket,
                Key=object_key,
                Body=content_bytes
            )


class Sampler(ABC):
    def __aiter__(self):
        return self
    
    @abstractmethod
    async def __anext__(self):
        ...


class FiniteSampler(Sampler):
    def __init__(self, input_dataset: InputDataset, output_dataset: OutputDataset, overwrite: bool) -> None:
        self._input_dataset = input_dataset
        self._output_dataset = output_dataset
        self._overwrite = overwrite
    
    async def prepare_data(self) -> None:
        processed_ids = set()
        if not self._overwrite:
            processed_ids = await self._output_dataset.get_processed_ids()
            logger.info(f"Found {len(processed_ids)} processed examples")
        new_data = []
        for data in await self._input_dataset.read_all_data():
            if data["custom_id"] not in processed_ids:
                new_data.append(data)
        logger.info(f"Sampler will use {len(new_data)} examples")
        random.shuffle(new_data)
        self._queue: asyncio.Queue[typing.Any] = asyncio.Queue()
        for i, req in enumerate(new_data):
            is_last = bool(i == len(new_data) - 1)
            self._queue.put_nowait((req, is_last))
    
    async def __anext__(self):
        if self._queue.empty():
            raise StopAsyncIteration
        item = await self._queue.get()
        self._queue.task_done()
        return item


class InfiniteSampler(Sampler):
    def __init__(self, input_dataset: InputDataset, output_dataset: OutputDataset, overwrite: bool) -> None:
        self._input_dataset = input_dataset
        self._output_dataset = output_dataset
        self._overwrite = overwrite
    
    async def prepare_data(self) -> None:
        processed_ids = set()
        if not self._overwrite:
            processed_ids = await self._output_dataset.get_processed_ids()
            logger.info(f"Found {len(processed_ids)} processed examples")
        self._new_data = []
        for data in await self._input_dataset.read_all_data():
            if data["custom_id"] not in processed_ids:
                self._new_data.append(data)
        logger.info(f"Sampler will use {len(self._new_data)} examples")
    
    async def __anext__(self):
        return (random.choice(self._new_data), False) # neve last since infinite loop
