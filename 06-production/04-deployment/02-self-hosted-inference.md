# Self-Hosted Inference

## TL;DR
Self-hosting involves running open-weights models (like Llama-3 or Mistral) on your own infrastructure (AWS EC2, on-premise clusters, etc.) rather than relying on managed APIs like OpenAI. It is required for strict data privacy compliance and becomes highly cost-effective at massive scale, but it demands significant engineering overhead to manage GPU orchestration, batching strategies, and memory optimization using frameworks like vLLM.

---

## When to Self-Host

Self-hosting is generally a bad idea for early-stage startups searching for product-market fit due to high upfront costs and DevOps complexity. However, it becomes mandatory in two scenarios:

1. **Compliance and Privacy:** Healthcare (HIPAA), Defense, and strict financial institutions often prohibit sending sensitive data to third-party cloud APIs. Self-hosting ensures data never leaves the corporate VPC.
2. **Massive Scale Economics:** Managed APIs charge per token. At billions of tokens per month, the variable cost of an API vastly exceeds the fixed cost of renting bare-metal GPUs, provided you can keep GPU utilization high.

## The Standard Frameworks

You do not run a production LLM using HuggingFace's standard `transformers` python library. That library is optimized for research, not concurrent serving. Production requires specialized inference engines.

### 1. vLLM (The Industry Standard)
An open-source, high-throughput inference engine. 
- **Key Feature:** Introduces **PagedAttention**, which manages the KV Cache like an operating system manages virtual memory. This prevents memory fragmentation and allows for massive batch sizes.
- **Use Case:** High-concurrency production deployments. It is the backbone of many enterprise deployments.

### 2. TGI (Text Generation Inference)
Developed by HuggingFace. 
- **Key Feature:** Deeply integrated with the HuggingFace ecosystem, excellent support for a wide variety of architectures and quantization methods (like bitsandbytes). Includes Continuous Batching.
- **Use Case:** Enterprise deployments, particularly when tightly coupled with HuggingFace Hub.

### 3. Ollama / Llama.cpp
- **Key Feature:** Optimized for CPU and edge inference (Apple Silicon, consumer GPUs). Uses the GGUF quantization format.
- **Use Case:** Local development, testing models on laptops, or edge deployments (e.g., running an LLM inside a medical device or a user's desktop application). Not typically used for high-concurrency cloud deployments.

## Hardware Requirements and Sizing

Sizing a GPU cluster requires understanding VRAM math. You need VRAM for the model weights + the KV cache for concurrent users.

*Rule of Thumb for FP16 (16-bit precision):* `1B parameters ≈ 2GB VRAM`

- **Small Models (e.g., Llama-3-8B):** ~16GB VRAM for weights. Can run on a single consumer GPU (RTX 4090) or a single cheap cloud GPU (NVIDIA A10g or L4).
- **Medium Models (e.g., Mixtral 8x7B):** Requires ~90GB VRAM. Cannot fit on a single 80GB GPU. Requires **Tensor Parallelism** (splitting the model across two A100/H100 GPUs).
- **Massive Models (e.g., Llama-3-70B):** ~140GB VRAM for weights. Requires at least two 80GB A100s just to load, and likely four A100s to handle a production batch size of KV cache. 

*(Note: These requirements drop significantly if using Quantization. See → [07-model-quantization.md](../02-cost-optimization/07-model-quantization.md))*

## Infrastructure Deployment

Self-hosted models are typically deployed using Kubernetes (K8s) or managed container services. 
The inference engine (e.g., vLLM) runs in a Docker container exposing an OpenAI-compatible HTTP interface.

**The Auto-Scaling Challenge:**
Scaling an LLM is not like scaling a NodeJS app (which boots in 2 seconds). Loading a 70B model into GPU VRAM can take minutes. Therefore, auto-scaling rules must be predictive or based on queue length, not just immediate CPU/GPU utilization, to prevent traffic spikes from overwhelming the system before new nodes can boot.

## Common Mistakes

- **Using standard HTTP load balancers:** Round-robin load balancing is fatal for LLMs. If Node A is processing a 2000-token request and Node B is empty, a naive load balancer might still send the next request to Node A. You must use **Least Outstanding Requests** routing.
- **Ignoring Continuous Batching:** Trying to serve multiple users using basic PyTorch scripts, resulting in terrible latency and GPU memory crashes under load.
- **Underestimating the KV cache size:** Securing a GPU with exactly enough VRAM for the model weights, and then getting Out of Memory (OOM) errors the moment the 5th concurrent user connects because there is no RAM left for the context window.

## Interview Questions

**Q: What is the primary difference between using the HuggingFace `transformers` library and an engine like `vLLM` in a production environment?**
**A:** `transformers` uses static batching and allocates memory sequentially, making it incredibly inefficient for concurrent requests (resulting in OOM errors or low throughput). `vLLM` is a dedicated inference server that uses Continuous Batching and PagedAttention to dynamically manage memory token-by-token, drastically increasing the number of concurrent users a single GPU can support.

**Q: If you need to deploy a 70B parameter model at FP16 precision, why can't you deploy it on a single top-tier NVIDIA H100 80GB GPU?**
**A:** Because at 16-bit precision, 1 billion parameters requires roughly 2GB of VRAM. A 70B model requires ~140GB of VRAM just to load the weights into memory, completely ignoring the additional VRAM needed for the KV cache to actually process prompts. Therefore, you must use Tensor Parallelism to split the model across at least two 80GB GPUs.

## Further Reading
- [vLLM Documentation](https://vllm.ai/) — Understanding PagedAttention and deployment.
