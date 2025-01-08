import time
import string
import random
import asyncio
import argparse

from strawberry.run import Run
from strawberry.user import User
from strawberry.dataset import Dataset
from strawberry.prometheus import Prometheus


async def program() -> None:
    """
    Entry point for the Strawberry program.

    This function parses command-line arguments, initializes necessary components such as Prometheus, Dataset,
    and Run instances, and starts the experiment.

    Command-Line Arguments:
        --run_name_prefix (str): Prefix for the run name, required.
        --max_users (int, optional): Maximum number of users to create during the run (default: 8).
        --wait_start (int, optional): Minimum wait time between user actions in seconds (default: 1).
        --wait_end (int, optional): Maximum wait time between user actions in seconds (default: 4).
        --users_per_second (int, optional): Number of users to create per second (default: 1).
        --run_time (int, optional): Total runtime of the experiment in seconds (default: 128).
        --prometheus_port (int): Port to expose Prometheus metrics, required.
        --openai_base_url (str): OpenAI API base URL (e.g., http://localhost:8000/v1), required.
        --token (str, optional): API token for authentication (default: "token").
        --model_name (str): Name of the model to use for requests, required.
        --dataset_path (str): Path to the dataset file, required.

    Raises:
        SystemExit: If required arguments are not provided or invalid values are passed.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--run_name_prefix", type=str, required=True)

    parser.add_argument("--max_users", type=int, required=False, default=8)
    parser.add_argument("--wait_start", type=int, required=False, default=1)
    parser.add_argument("--wait_end", type=int, required=False, default=4)
    parser.add_argument("--users_per_second", type=int, required=False, default=1)
    parser.add_argument("--run_time", type=int, required=False, default=128)
    parser.add_argument("--prometheus_port", type=int, required=True)

    parser.add_argument(
        "--openai_base_url",
        type=str,
        required=True,
        help="OpenAI base url for example http://localhost:8000/v1"
    )

    parser.add_argument(
        "--token",
        type=str,
        required=False,
        default="token",
        help="Token if not set will be set to token"
    )
    
    parser.add_argument(
        "--model_name",
        type=str,
        required=True,
        help="Model name to be used while sending requests"
    )

    parser.add_argument(
        "--dataset_path",
        type=str,
        required=True,
        help="Path to dataset to be used for sampling"
    )

    arguments = parser.parse_args()

    RED = "\033[31m"
    RESET = "\033[0m"

    def bold_text(text):
        """
        Formats the given text as bold.

        Args:
            text (str): The text to format.

        Returns:
            str: The formatted text with bold ANSI escape codes.
        """
        return f"\033[1m{text}\033[0m"

    run_name = arguments.run_name_prefix + "_" + "".join(random.choices(string.ascii_lowercase, k=8))
    
    print(f"Start run {RED}{bold_text(run_name)}{RESET} with 🍓 {RED}{bold_text("Strawberry")}{RESET}")
    
    prometheus = Prometheus(run=run_name, prometheus_port=arguments.prometheus_port)

    dataset = Dataset(file_path=arguments.dataset_path)

    run = Run(
        prometheus=prometheus, 
        max_users=arguments.max_users, 
        wait=lambda: random.uniform(arguments.wait_start, arguments.wait_end), 
        users_per_second=arguments.users_per_second, 
        run_time=arguments.run_time,
        dataset=dataset,
        base_url=arguments.openai_base_url,
        api_key=arguments.token,
        model_name=arguments.model_name
    )

    await run.start()

if __name__ == "__main__":
    """
    Main entry point for the Strawberry program.

    Uses asyncio to run the asynchronous `program` function.
    """
    asyncio.run(program())
