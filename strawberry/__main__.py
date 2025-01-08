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
    parser = argparse.ArgumentParser()

    parser.add_argument("--run_name", type=str, required=False, default=''.join(random.choices(string.ascii_letters, k=8)))
    parser.add_argument("--max_users", type=int, required=False, default=8)
    parser.add_argument("--wait_start", type=int, required=False, default=1)
    parser.add_argument("--wait_end", type=int, required=False, default=4)
    parser.add_argument("--users_per_second", type=int, required=False, default=1)
    parser.add_argument("--run_time", type=int, required=False, default=128)

    arguments = parser.parse_args()
    
    print(f"Start run {arguments.run_name} with 🍓 Strawberry")
    
    prometheus = Prometheus(run=arguments.run_name)

    dataset = Dataset(file_path="/mnt/datsets/dataset.txt")

    run = Run(
        prometheus=prometheus, 
        max_users=arguments.max_users, 
        wait=lambda: random.uniform(arguments.wait_start, arguments.wait_end), 
        users_per_second=arguments.users_per_second, 
        run_time=arguments.run_time,
        dataset=dataset
    )

    await run.start()


if __name__ == "__main__":
    asyncio.run(program())
