import openai
import typing
import asyncio

from strawberry.user import User
from strawberry.dataset import Dataset
from strawberry.requester import Requester
from strawberry.prometheus import Prometheus


class Run:
    """
    Manages and executes an experiment by creating users, scheduling them, and handling
    user creation strategies and experiment termination.

    This class controls the lifecycle of an experiment, including user instantiation,
    managing concurrency, and stopping the experiment after a defined duration.

    Attributes:
        _prometheus (Prometheus): Instance to log and monitor experiment metrics.
        _max_users (int): Maximum number of users to create during the experiment.
        _wait (typing.Callable): Callable to determine the wait time between user actions.
        _users_per_second (int): Number of users to create per second.
        _run_time (int): Total runtime of the experiment in seconds.
        _dataset (Dataset): The dataset instance used to provide prompts for requests.
        _base_url (str): Base URL for the OpenAI API.
        _api_key (str): API key for authenticating with the OpenAI API.
        _model_name (str): Name of the OpenAI model to use for requests.
    """

    def __init__(
        self,
        prometheus: Prometheus,
        max_users: int,
        wait: typing.Callable,
        users_per_second: int,
        run_time: int,
        dataset: Dataset,
        base_url: str,
        api_key: str,
        model_name: str
    ) -> None:
        """
        Initializes the Run instance.

        Args:
            prometheus (Prometheus): Instance for logging metrics.
            max_users (int): Maximum number of users to create during the experiment.
            wait (typing.Callable): Function to determine wait time between user actions.
            users_per_second (int): Number of users to create per second.
            run_time (int): Total runtime of the experiment in seconds.
            dataset (Dataset): Dataset instance to provide prompts for user requests.
            base_url (str): Base URL for the OpenAI API.
            api_key (str): API key for authenticating with the OpenAI API.
            model_name (str): Name of the OpenAI model to use for requests.
        """
        self._prometheus = prometheus
        self._max_users = max_users
        self._wait = wait
        self._users_per_second = users_per_second
        self._run_time = run_time
        self._dataset = dataset
        self._base_url = base_url
        self._api_key = api_key
        self._model_name = model_name

    async def start(self) -> None:
        """
        Starts the experiment by creating users and managing their lifecycle.

        The method:
        - Creates a requester instance shared across all users.
        - Schedules user creation at a rate defined by `_users_per_second`.
        - Ensures the total number of users does not exceed `_max_users`.
        - Runs the experiment for `_run_time` seconds.
        - Cancels all running user tasks when the experiment ends.

        Raises:
            asyncio.CancelledError: If tasks are cancelled during experiment termination.
        """
        background_tasks = set()
        currect_active_users = 0

        requester = Requester(
            prometheus=self._prometheus,
            base_url=self._base_url,
            api_key=self._api_key,
            model_name=self._model_name
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
