## TensorRT-LLM

How to benchmark TensorRT-LLM. Prepare engine first

```bash
docker run \
  -it \
  --gpus all \
  -v $(pwd)/engines:/mnt/engines \
  nvidia/cuda:12.4.1-devel-ubuntu22.04 bash

apt-get update
apt install python3-pip
apt-get -y install libopenmpi-dev
apt-get install vim
pip3 install tensorrt_llm==0.13.0
```

```bash
vi build_engine.py
```

```bash
from tensorrt_llm import LLM, SamplingParams


llm = LLM(model="TinyLlama/TinyLlama-1.1B-Chat-v1.0")
llm.save("/mnt/engines/tiny_llama_engine")
```

```bash
python3 ./build_engine.py
```

Start server with

```bash
docker run \
  --rm \
  --gpus all \
  --name server \
  --network strawberry \
  -v $(pwd)/tiny_llama_engine:/mnt/tiny_llama_engine \
  nvidia/cuda:12.4.1-devel-ubuntu22.04 trtllm-serve \
    --host 0.0.0.0 \
    --port 8000 \
    /mnt/tiny_llama_engine
```

Optionally make sure it works

```bash
docker exec -it server curl -X 'POST' \
  'http://localhost:8000/v1/chat/completions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "model": "/mnt/tiny_llama_engine",
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
