## Benchmark Qwen/Qwen2.5-0.5B-Instruct with vLLM

It is now supposed that prometheus and vllm are running

Here we will not save predictions for our inputs. Intead strawberry will just send bunch of requests
and log metrics to the promtehus such that you can visualize it in grafana. We will use infinite sampler which means
that we will iterate over provded dataset for infinite time where each request will be sent to server with equal probability. This
code will spawn 1 user every second untill users count become 8. Each user will sample request from input dataet with equal probability
and send to server then sleep random time between 1 second and 4 seconds. Experiment will last for 128 seconds

```bash
docker run \
  --network strawberry \
  --rm \
  -e LOGURU_LEVEL=INFO \
  --name strawberry \
  -v $(pwd)/datasets:/mnt/datasets \
  vladislavkruglikov/strawberry \
    --run_name_prefix qwen05b_instruct \
    --openai_base_url http://server:8000/v1 \
    --model_name Qwen/Qwen2.5-0.5B-Instruct \
    --prometheus_port 8000 \
    --max_users 8 \
    --wait_start 1 \
    --wait_end 4 \
    --users_per_second 1 \
    --run_time 128 \
    --input local \
    --input_local_path /mnt/datasets/dataset.jsonl \
    --sampler infinite
```
