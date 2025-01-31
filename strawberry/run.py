import openai
import typing
import asyncio

from loguru import logger
from strawberry.user import User
from strawberry.dataset import Sampler, OutputDataset
from strawberry.requester import Requester
from strawberry.prometheus import Prometheus


class Run:
    def __init__(
        self,
        prometheus: Prometheus,
        max_users: int,
        wait: typing.Callable,
        # changed parameter name from users_per_second to spawn_rate
        spawn_rate: float,
        run_time: int,
        dataset: Sampler,
        base_url: str,
        api_key: str,
        model_name: str,
        output_dataset: OutputDataset,
    ) -> None:
        self._prometheus = prometheus
        self._max_users = max_users
        self._wait = wait
        # use spawn_rate instead of users_per_second
        self._spawn_rate = spawn_rate
        self._run_time = run_time
        self._dataset = dataset
        self._base_url = base_url
        self._api_key = api_key
        self._model_name = model_name
        self._output_dataset = output_dataset
        self._requester = Requester(
            prometheus=self._prometheus,
            base_url=self._base_url,
            api_key=self._api_key,
            model_name=self._model_name
        )


    async def start(self) -> None:
        logger.info("Start to load dataset")
        
        await self._dataset.prepare_data()
        
        logger.info("Dataset is ready")

        self._background_tasks = set()

        # keeps number of started users. only goes up
        self.started_users = 0
        
        # keeps active number of users for log. Can go down or up
        self.active_users_gauge = 0 

        # keeps finished number of users for log. Only goes up
        self._finished_users = 0

        # loop until we reach max_users
        while self.started_users < self._max_users:
            self._create_user()
            logger.info(f"Add user, currently active {self.active_users_gauge} / {self._max_users} users")
            
            # changed logic: spawn_rate of 0.1 => 1 user every 10s
            # spawn_rate of 2.0 => 2 users per second => 1 user every 0.5s
            if self._spawn_rate > 0:
                await asyncio.sleep(1.0 / self._spawn_rate)

        try:
            logger.info(f"All users are spawned. Start to wait untill all users will finish or timeout {self._run_time} seconds")
            done, pending = await asyncio.wait(
                self._background_tasks, 
                timeout=self._run_time, 
                return_when=asyncio.ALL_COMPLETED
            )
        except asyncio.CancelledError:
            pass
        finally:
            for t in self._background_tasks:
                if not t.done():
                    t.cancel()
    
    def _create_user(self) -> None:
        user = User(
            requester=self._requester,
            wait=self._wait,
            dataset=self._dataset,
            output_dataset_writer=self._output_dataset
        )
        self._prometheus.increase_users_count()
        task = asyncio.create_task(user.start())
        self._background_tasks.add(task)
        task.add_done_callback(self._on_user_finish)
        self.started_users += 1
        self.active_users_gauge += 1
    
    def _on_user_finish(self, task) -> None:
        self._prometheus.decrease_users_count()
        self.active_users_gauge -= 1
        self._finished_users += 1
        logger.info(
            f"Remove user, currently active {self.active_users_gauge} / {self._max_users} users. "
            f"Finished users {self._finished_users} / {self._max_users}"
        )
