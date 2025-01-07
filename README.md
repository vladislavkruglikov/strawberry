## 🍓 Strawberry

Strawberry is a tool that allows you to conveniently benchmark large language model inference servers that provide OpenAI like chat completion API. Strawberry uses Prometheus for metric collection and Grafana for visualization while our custom code is used to send requests to the server. Strawberry provides a convenient way to run benchmarks and record your metrics into remote storage. It is very flexible since you can connect it to your custom Prometheus instance or Grafana if you want to keep your data private with minimal changes to the configuration files. You can use one of our templates for Grafana dashboards that cover the most popular metrics or you can extend them and build your own from the data collected during benchmarking. You can also record your own metrics and use them

Additionally this repository contains notes about metrics and everything I find interesting and that might be helpful for anyone interested in benchmarking LLMs

The core idea behind Strawberry is that it is not attached to any particular library or framework. Instead it works with the abstraction provided by the OpenAI API. Any library or framework that provides an OpenAI API most of which already do such as **vLLM** or **SGLang** can be benchmarked with this tool right now with no additional code writing or modifications. This way Strawberry has no information about the internals of the framework. All it cares about is the common protocol which is the OpenAI API chat completions

## Storage

Despite the fact that this section might be seen hard it only needs to be done once and then can be used with any other framework such as **vLLM** or **SGLang**

In this section you will create Grafana Cloud workspace with Cloud Prometheus that will allow you to store and visualize your data. If you are not familiar with that technologies they are very popular so it might be helpful anyway

First you need to create [Grana Cloud](https://grafana.com/products/cloud) that will be used to store and visualize load test results

Then we need to setup single configuration file where we will put information about our workspace that we have created. You can find template in `prometheus.yaml`

Start with remote write configuration. In order to find needed information about your workspace go to your [Grafana Account](https://grafana.com/auth/sign-in) where you are likely to have single Grafana Cloud Stack which you will need to select and click Launch. Then you will see manage your stack page where you can see Prometheus stack. You need to click details in the Prometheus stack. Scroll down to Sending metrics with Prometheus and you will find remote write configuration for your workspace. You can generate API token which is your password by clicking Generate now in the same page

After you have updated `prometheus.yaml` with provided information you are left with targets parameter where you need to specify url that will expose metrics. You can leave it unchanged since we will run code in docker and it is already programmed to use that particular host and port

Create common network that will be used for all containers

```bash
docker network create strawberry
```

Now you are ready to start prometheus

```bash
docker run \
  --name prometheus \
  --rm \
  --network strawberry \
  -v $(pwd)/prometheus.yaml:/etc/prometheus/prometheus.yaml \
  prom/prometheus \
  --config.file=/etc/prometheus/prometheus.yaml
```

## Server

In this section you will run Open AI like inference server chat completions API

```bash
docker run \
  --gpus all \
  --rm \
  --name server \
  -v $(pwd)/models:/root/.cache/huggingface \
  --network strawberry \
  vllm/vllm-openai:v0.6.5 \
  --model Qwen/Qwen2.5-0.5B-Instruct \
  --gpu-memory-utilization 0.1
```

## Benchmark

Now you have got your storage set up and inference server running and the only left part is to send requests to the server and record metrics. This is what we are going to do now

```bash
docker run --network strawberry --rm --name strawberry strawberry
```

Parameters

`--address` specify prefix open ai like api url

## Plots

Now you are ready to visualize your results in Grafana. Grab this dashboard template and install it into your grafana template. Select source for data your cloud instance

## Notes

If you want you can build benchmark image from scrach you can do

```bash
docker build --tag strawberry .
```

## References

Good articles

* https://hao-ai-lab.github.io/blogs/distserve
