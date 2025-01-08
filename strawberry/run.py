import openai
import typing
import asyncio

from strawberry.user import User
from strawberry.dataset import Dataset
from strawberry.requester import Requester
from strawberry.prometheus import Prometheus


class Run:
    # experiment instances. Creates users and schedules them. responsible for strategy of user creation and experiment
    # termination
    def __init__(self, prometheus: Prometheus, max_users: int, wait: typing.Callable, users_per_second: int, run_time: int, dataset: Dataset) -> None:
        self._prometheus = prometheus
        self._max_users = max_users
        self._wait = wait
        self._users_per_second = users_per_second
        self._run_time = run_time
        self._dataset = dataset
    
    async def start(self) -> None:
        background_tasks = set()
        currect_active_users = 0

        requester = Requester(
            prometheus=self._prometheus,
            base_url="http://server:8000/v1",
            api_key="token",
            model_name="Qwen/Qwen2.5-0.5B-Instruct"
        )

        while currect_active_users < self._max_users:
            if currect_active_users > 0 and currect_active_users % self._users_per_second == 0:
                await asyncio.sleep(1)

            user = User(requester=requester, wait=self._wait, dataset=self._dataset)
            self._prometheus.increase_users_count()
            task = asyncio.create_task(user.start())
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)
            currect_active_users += 1
        
        await asyncio.sleep(self._run_time)

        for task in background_tasks:
            task.cancel()
