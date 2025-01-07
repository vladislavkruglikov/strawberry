import time
import random
import asyncio

from strawberry.run import Run
from strawberry.user import User
from strawberry.prometheus import Prometheus


async def program() -> None:
    print("Start to run 🍓 Strawberry")

    max_users = 8
    wait = lambda: random.uniform(1, 4)
    users_per_second = 1
    run_time = 128
    
    prometheus = Prometheus(run="example_9")

    run = Run(
        prometheus=prometheus, 
        max_users=max_users, 
        wait=wait, 
        users_per_second=users_per_second, 
        run_time=run_time
    )

    await run.start()


if __name__ == "__main__":
    asyncio.run(program())
