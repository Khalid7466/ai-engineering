# Batching Strategies

## TL;DR
Batching is the process of grouping multiple independent user requests together and processing them simultaneously on a GPU. Because GPUs are massively parallel processors, batching drastically increases the overall **throughput** (total tokens generated per second) of an LLM system, lowering costs. However, naïve batching hurts **latency** (time to process a single request). Advanced strategies like **Continuous Batching** (pioneered by vLLM) solve this tradeoff, making efficient self-hosted production LLMs possible.

---

## The Throughput vs. Latency Tradeoff

When deploying a self-hosted model, you have a GPU that is mostly memory-bandwidth bound during generation. If you process requests one at a time (batch size = 1), you get excellent latency for that specific user, but the GPU's massive compute cores sit mostly idle. 

To maximize ROI on expensive GPUs, you must increase the batch size.
- **Throughput:** How many total requests the system handles per minute. (Optimizes Cost).
- **Latency:** How long a single user waits for their response. (Optimizes User Experience).

Batching improves throughput at the expense of latency. The engineering challenge is managing this tradeoff.

## Types of Batching

### 1. Static Batching (The Naïve Approach)
The system waits for a fixed number of requests (e.g., 8) to arrive, groups them, and sends them to the model. 
- **The Problem:** If Request A asks for 10 tokens and Request B asks for 1000 tokens, Request A is finished almost immediately. However, it cannot be returned to the user until Request B finishes generating its 1000th token, because the GPU is locked processing the static batch.
- **Result:** Terrible latency for short requests, and wasted GPU memory holding onto finished sequences.

### 2. Dynamic Batching
The system groups requests as they arrive within a small time window (e.g., 50ms). If 4 requests arrive, it batches them. This avoids waiting endlessly for a batch to fill, but it still suffers from the "longest request wins" problem where short generations are held hostage by long ones.

### 3. Continuous Batching (Iteration-Level Scheduling)
Continuous Batching (also called in-flight batching) revolutionized LLM serving. It is the core technology behind frameworks like **vLLM** and **TGI**.

Instead of waiting for a batch to finish completely, the scheduler operates at the **token level** (iteration level). 
1. The GPU generates 1 token for all active requests in the batch.
2. If Request A finishes (it hit a `<stop>` token), it is immediately ejected from the batch and returned to the user.
3. In that exact same millisecond, a new request from the queue (Request C) is injected into the empty slot in the batch.
4. The GPU generates the next token.

**Why it matters:** 
- No request is ever held hostage by a longer request.
- The GPU batch size is always full, maximizing hardware utilization.
- It enables massive throughput improvements (often 10x-20x over static batching) while maintaining acceptable latency.

## PagedAttention (The Enabler)

Continuous batching requires dynamically swapping requests in and out of GPU memory. The bottleneck then becomes managing the **KV Cache** (the memory the model uses to remember the prompt and previously generated tokens for each request).

In static systems, memory is pre-allocated based on the maximum possible sequence length, leading to massive fragmentation and wasted VRAM. 
**PagedAttention** (introduced with vLLM) solves this by borrowing the concept of virtual memory and paging from operating systems. It breaks the KV cache into small, non-contiguous blocks (pages). This eliminates memory fragmentation, allowing the system to fit significantly more concurrent requests into a batch on the same GPU.

## Production Implications

If you are using managed APIs (OpenAI, Anthropic), you do not need to worry about batching; the provider handles it. 

If you are **self-hosting** models, your batching strategy dictates your unit economics. Without Continuous Batching and PagedAttention, a $30,000 GPU might only be able to serve 5 concurrent users. With them, that same GPU can serve 100+ concurrent users. This is the difference between a profitable product and a catastrophic cloud bill.

## Common Mistakes

- **Using naive HuggingFace `generate()` in production:** Standard Transformers library code uses static batching and is meant for research, not production serving. It will crash under concurrent load.
- **Pre-allocating too much max_length:** Setting the `max_sequence_length` artificially high in a non-PagedAttention system, which causes OOM (Out of Memory) errors even with small batches.
- **Ignoring TTFT:** Batching inherently increases Time To First Token because the model has to process the input prompts of multiple users simultaneously. You must tune the maximum batch size to ensure TTFT stays within acceptable SLOs (e.g., < 1 second).

## Interview Questions

**Q: Explain why Static Batching is inefficient for serving Large Language Models.**
**A:** In static batching, the entire batch must finish before any request can be returned. Because LLM generation lengths are highly variable, short requests (e.g., a 10-token answer) get trapped waiting for long requests (e.g., a 1000-token essay) to finish. This leads to poor latency for the short requests and wastes memory holding onto completed sequences.

**Q: How does Continuous Batching (or iteration-level scheduling) solve the problems of static batching?**
**A:** Continuous batching evaluates the state of the batch after *every single token generation*. When a request finishes, it is immediately ejected and its result is returned to the user. A new request from the queue is instantly slotted into that freed space. This ensures high GPU utilization and prevents short queries from being delayed by long ones.

## Further Reading
- [vLLM: Easy, Fast, and Cheap LLM Serving](https://vllm.ai/) — The official documentation for the industry-standard serving engine based on PagedAttention.
- → See [04-deployment/02-self-hosted-inference.md](../04-deployment/02-self-hosted-inference.md) for how to deploy engines that utilize these strategies.
