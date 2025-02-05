Predict

```bash
sudo docker build --tag strawberry . && sudo docker run -e LOGURU_LEVEL=INFO  --network strawberry   --rm   -e LOGURU_LEVEL=INFO   --name strawberry   -v $(pwd)/datasets:/mnt/datasets   strawberry     --run_name_prefix qwen05b_instruct     --openai_base_url http://server:8000     --model_name Qwen/Qwen2.5-0.5B-Instruct     --prometheus_port 8000     --max_users 1     --wait_start 0     --wait_end 0     --spawn_rate 10     --run_time 128     --input local     --input_local_path /mnt/datasets/dataset_sglang.jsonl     --sampler finite --overwrite --requester sglang --output local --output_local_path /mnt/datasets/batch_qwen_sglang_local_local
```

Benchmark

```bash
sudo docker build --tag strawberry . && sudo docker run -e LOGURU_LEVEL=INFO  --network strawberry   --rm   -e LOGURU_LEVEL=INFO   --name strawberry   -v $(pwd)/datasets:/mnt/datasets   strawberry     --run_name_prefix qwen05b_instruct     --openai_base_url http://server:8000     --model_name Qwen/Qwen2.5-0.5B-Instruct     --prometheus_port 8000     --max_users 16     --wait_start 0     --wait_end 0     --spawn_rate 1     --run_time 128     --input local     --input_local_path /mnt/datasets/dataset_sglang.jsonl     --sampler infinite --overwrite --requester sglang
```
