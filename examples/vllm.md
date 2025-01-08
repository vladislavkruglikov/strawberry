## vLLM

How to benchmark vLLM. Start server with

```bash
docker run \
  --rm \
  --gpus all \
  --name server \
  --network strawberry \
  -v $(pwd)/models:/root/.cache/huggingface \
  vllm/vllm-openai:v0.6.5 \
  --model Qwen/Qwen2.5-0.5B-Instruct \
  --gpu-memory-utilization 0.1
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
  strawberry
```
