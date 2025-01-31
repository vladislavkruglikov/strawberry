import time
import string
import random
import asyncio
import argparse

from pathlib import Path
from strawberry.run import Run
from strawberry.user import User
from strawberry.dataset import LocalInputDataset, LocalOutputDataset, S3OutputDataset, DummyOutputDataset, FiniteSampler, InfiniteSampler
from strawberry.prometheus import Prometheus


def local_input_output_factory(arguments):
    input_dataset = None
    output_dataset = None
    sampler = None

    if arguments.input == "local":
        if arguments.input_local_path is not None:
            input_dataset = LocalInputDataset(arguments.input_local_path)
        else:
            raise ValueError("If using local input, --input_local_path must be specified")
    else:
        raise ValueError("Unknown type for input, support local")

    if arguments.output is None:
        output_dataset = DummyOutputDataset()
    elif arguments.output == "local":
        if arguments.output_local_path is not None:
            output_dataset = LocalOutputDataset(arguments.output_local_path)
        else:
            raise ValueError("If using local output, --output_local_path must be specified")
    elif arguments.output == "s3":
        if arguments.output_s3_path is None:
            raise ValueError("output_s3_path must be specified if using s3")
        if arguments.output_s3_bucket is None:
            raise ValueError("output_s3_bucket if use s3")
        if arguments.output_s3_aws_access_key_id is None:
            raise ValueError("output_s3_aws_access_key_id if use s3")
        if arguments.output_s3_aws_secret_access_key is None:
            raise ValueError("output_s3_aws_secret_access_key if use s3")
        if arguments.output_s3_endpoint_url is None:
            raise ValueError("output_s3_endpoint_url if use s3")
        if arguments.output_s3_region_name is None:
            raise ValueError("output_s3_region_name is use s3")
        
        output_dataset = S3OutputDataset(
            aws_access_key=arguments.output_s3_aws_access_key_id,
            aws_secret_key=arguments.output_s3_aws_secret_access_key,
            bucket=arguments.output_s3_bucket,
            address=arguments.output_s3_endpoint_url,
            base_path=arguments.output_s3_path,
            output_s3_region_name=arguments.output_s3_region_name
        )
    else:
        raise ValueError("Unknown type for output, local, s3 are supported")
    
    if arguments.sampler == "finite":
        sampler = FiniteSampler(input_dataset=input_dataset, output_dataset=output_dataset, overwrite=arguments.overwrite)
    elif arguments.sampler == "infinite":
        sampler = InfiniteSampler(input_dataset=input_dataset, output_dataset=output_dataset, overwrite=arguments.overwrite)
    else:
        raise ValueError("sampler finite, infinite")
        
    return input_dataset, output_dataset, sampler


async def program() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--run_name_prefix", type=str, required=True)

    parser.add_argument("--max_users", type=int, required=False, default=8)
    parser.add_argument("--wait_start", type=int, required=False, default=1)
    parser.add_argument("--wait_end", type=int, required=False, default=4)
    parser.add_argument("--spawn_rate", type=float, required=False, default=1) # rate to spawn, users per second. 0.1 means 0.1 user per second, 1 user once in 10 seconds
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

    parser.add_argument("--input", type=str, required=True)

    parser.add_argument("--input_local_path", type=Path, required=False)

    parser.add_argument("--output", type=str, required=False)

    parser.add_argument("--output_local_path", type=Path, required=False)

    parser.add_argument("--output_s3_path", type=str, required=False)
    parser.add_argument("--output_s3_bucket", type=str, required=False)
    parser.add_argument("--output_s3_aws_access_key_id", type=str, required=False)
    parser.add_argument("--output_s3_aws_secret_access_key", type=str, required=False)
    parser.add_argument("--output_s3_endpoint_url", type=str, required=False)
    parser.add_argument("--output_s3_region_name", type=str, required=False)

    parser.add_argument("--sampler", type=str, required=False)
    parser.add_argument("--overwrite", action="store_true", required=False, default=False)

    arguments = parser.parse_args()

    RED = "\033[31m"
    RESET = "\033[0m"

    def bold_text(text):
        return f"\033[1m{text}\033[0m"

    run_name = arguments.run_name_prefix + "_" + "".join(random.choices(string.ascii_lowercase, k=8))
    
    print(f"Start run {RED}{bold_text(run_name)}{RESET} with 🍓 {RED}{bold_text("Strawberry")}{RESET}")
    
    prometheus = Prometheus(run=run_name, prometheus_port=arguments.prometheus_port)

    input_dataset, output_dataset, sampler = local_input_output_factory(arguments)

    run = Run(
        prometheus=prometheus, 
        max_users=arguments.max_users, 
        wait=lambda: random.uniform(arguments.wait_start, arguments.wait_end), 
        spawn_rate=arguments.spawn_rate, 
        run_time=arguments.run_time,
        dataset=sampler,
        base_url=arguments.openai_base_url,
        api_key=arguments.token,
        model_name=arguments.model_name,
        output_dataset=output_dataset
    )

    await run.start()

if __name__ == "__main__":
    asyncio.run(program())
