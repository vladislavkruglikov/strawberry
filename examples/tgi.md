## TGI

How to benchmark TGI. Start server with

```bash
docker run \
    --rm \
    --gpus all \
    --name server \
    --network strawberry \
    -v $(pwd)/models:/root/.cache/huggingface \
    --shm-size 64g \
    ghcr.io/huggingface/text-generation-inference:3.0.1 \
    --model-id Qwen/Qwen2.5-0.5B-Instruct \
    --port 8000
```

Optionally make sure it works for debug purposes

```bash
docker exec -it server curl -X 'POST' \
  'http://localhost:8000/v1/chat/completions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "model": "Qwen/Qwen2.5-0.5B-Instruct",
  "messages": [
        {"role": "user", "content": "What is 2 + 2?"}
    ]
}'
```

Start prometheus

```bash
docker run \
  --name prometheus \
  --rm \
  --network strawberry \
  -v $(pwd)/prometheus.yaml:/etc/prometheus/prometheus.yaml \
  prom/prometheus \
  --config.file=/etc/prometheus/prometheus.yaml
```

Start benchmark tool

```bash
docker run \
  --network strawberry \
  --rm \
  --name strawberry \
  -v $(pwd)/datasets:/mnt/datasets \
  vladislavkruglikov/strawberry \
    --run_name_prefix qwen05b_instruct \
    --openai_base_url http://server:8000/v1 \
    --model_name Qwen/Qwen2.5-0.5B-Instruct \
    --prometheus_port 8000 \
    --dataset_path /mnt/datasets/dataset.txt \
    --max_users 8 \
    --wait_start 1 \
    --wait_end 4 \
    --users_per_second 1 \
    --run_time 200000
```
