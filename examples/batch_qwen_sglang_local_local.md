## Run prediction batch job using Qwen/Qwen2.5-0.5B-Instruct with SGLang

It is now supposed that prometheus and sglang are running. In this example you will get predictions for your input dataset saved to local file system 


```bash
docker run -e LOGURU_LEVEL=INFO --network strawberry \
  --rm \
  --name strawberry \
  -v $(pwd)/datasets:/mnt/datasets \
  strawberry \
    --run_name_prefix qwen05b_instruct \
    --openai_base_url http://server:8000/v1 \
    --model_name Qwen/Qwen2.5-0.5B-Instruct \
    --prometheus_port 8000 \
    --max_users 8 \
    --wait_start 1 \
    --wait_end 4 \
    --spawn_rate 1  \
    --run_time 8192 \
    --input local \
    --input_local_path /mnt/datasets/dataset.jsonl \
    --output local \
    --output_local_path /mnt/datasets/batch_qwen_sglang_local_local \
    --sampler finite \
    --overwrite
```
