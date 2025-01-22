## Run preemprible prediction batch job using Qwen/Qwen2.5-0.5B-Instruct with TGI with aws S3 storage

It is now supposed that prometheus and sglang are running. In this example you will get predictions for your input dataset saved to s3 file system but additionaly to that strawberry will automatically check if there are some processed ids and it will skip them. You can force 🍓 strawberry to process them all usign --overwrite flag

Let us first run with --overwrite

```bash
docker run \
  --network strawberry \
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
    --users_per_second 1 \
    --run_time 256 \
    --input local \
    --input_local_path /mnt/datasets/dataset.jsonl \
    --output s3 \
    --output_s3_path ... \
    --output_s3_bucket ... \
    --output_s3_aws_access_key_id ... \
    --output_s3_aws_secret_access_key ... \
    --output_s3_endpoint_url ... \
    --output_s3_region_name ... \
    --sampler finite \
    --overwrite
```

Now manually delete some processed examples from path u specified and run same command without overwrite flag. You will
see that 🍓 strawberry will process only thoose deleted files

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
    --max_users 8 \
    --wait_start 1 \
    --wait_end 4 \
    --users_per_second 1 \
    --run_time 256 \
    --input local \
    --input_local_path /mnt/datasets/dataset.jsonl \
    --output s3 \
    --output_s3_path ... \
    --output_s3_bucket ... \
    --output_s3_aws_access_key_id ... \
    --output_s3_aws_secret_access_key ... \
    --output_s3_endpoint_url ... \
    --output_s3_region_name ... \
    --sampler finite
```
