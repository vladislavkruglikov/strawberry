## SGLang

How to benchmark SGLang. Start server with

```bash
docker run \
    --rm \
    --gpus all \
    --name server \
    --network strawberry \
    -v $(pwd)/models:/root/.cache/huggingface \
    --shm-size 32g \
    --ipc=host \
    lmsysorg/sglang:latest \
    python3 -m sglang.launch_server --model-path Qwen/Qwen2.5-0.5B-Instruct --host 0.0.0.0 --port 8000
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
docker run --network strawberry --rm --name strawberry strawberry
```
