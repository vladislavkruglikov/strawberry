import typing
import asyncio

from strawberry.user import User
from strawberry.prometheus import Prometheus


class Run:
    def __init__(self, prometheus: Prometheus, max_users: int, wait: typing.Callable, users_per_second: int, run_time: int) -> None:
        self._prometheus = prometheus
        self._max_users = max_users
        self._wait = wait
        self._users_per_second = users_per_second
        self._run_time = run_time
    
    async def start(self) -> None:
        background_tasks = set()
        currect_active_users = 0

        while currect_active_users < self._max_users:
            if currect_active_users > 0 and currect_active_users % self._users_per_second == 0:
                await asyncio.sleep(1)

            user = User(prometheus=self._prometheus, wait=self._wait)
            task = asyncio.create_task(user.start())
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)
            currect_active_users += 1
        
        await asyncio.sleep(self._run_time)

        for task in background_tasks:
            task.cancel()
