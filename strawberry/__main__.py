import time
import random
import asyncio

from strawberry.user import User
from strawberry.prometheus import Prometheus


async def program() -> None:
    print("Start to run 🍓 Strawberry")

    prometheus = Prometheus(run="example_7")
    user = User(prometheus=prometheus)

    while True:
        await user.request()
        time.sleep(1)


if __name__ == "__main__":
    asyncio.run(program())
