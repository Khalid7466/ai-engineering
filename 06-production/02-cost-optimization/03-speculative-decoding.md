# Speculative Decoding

## TL;DR
Speculative Decoding is an advanced inference optimization technique that significantly speeds up text generation for Large Language Models (LLMs) without degrading output quality. It works by using a small, fast "draft" model to generate multiple tokens sequentially, and then using the large, slow "target" model to verify those tokens in a single parallel step. When successful, it can increase token throughput by 2x to 3x, directly reducing latency and operational costs for self-hosted models.

---

## The Bottleneck: Auto-regressive Generation

To understand why Speculative Decoding exists, you must understand the primary bottleneck of LLM inference: **autoregression**.

LLMs generate text one token at a time. To generate token 50, the model must process tokens 1 through 49. This sequential nature means that generation is primarily **memory-bandwidth bound**. The GPU spends most of its time loading the massive weights of the model from VRAM into the compute cores for *every single token*. 

However, modern GPUs possess massive parallel compute capabilities. Processing a prompt of 10 tokens takes roughly the same amount of time as processing a prompt of 1 token, because the GPU can process them all simultaneously in a single forward pass.

## How Speculative Decoding Works

Speculative Decoding exploits this parallel processing capability to bypass the sequential bottleneck. It requires two models:
1. **Target Model:** The massive model you actually want to use (e.g., Llama-3-70B). High quality, but slow.
2. **Draft Model:** A tiny, highly compressed version of the target model (e.g., a 1B parameter model). Lower quality, but blazingly fast.

### The Algorithm Step-by-Step
1. **Drafting:** The small Draft Model auto-regressively generates a short sequence of tokens (e.g., 4 tokens: "The", "cat", "sat", "on"). Because the model is tiny, this happens almost instantly.
2. **Verification (Speculation):** These 4 tokens are appended to the prompt. The massive Target Model is then run *once*, in parallel, to process all 4 tokens simultaneously. 
3. **Acceptance/Rejection:** The Target Model calculates what it *would* have generated at each step. 
   - If the Target Model agrees with the Draft Model ("Yes, I also would have generated 'The cat sat on'"), all 4 tokens are accepted. We just generated 4 tokens in the time it usually takes to generate 1!
   - If the Target Model disagrees at token 3 ("I would have generated 'The cat *slept*'"), it rejects token 3 and 4, accepts 1 and 2, and outputs its own token 3. The process then restarts.

Because the verification step uses exact mathematical probability matching, **Speculative Decoding guarantees the exact same output as if you had run the Target Model normally.** It is mathematically lossless.

## When It Works (And When It Doesn't)

The effectiveness of Speculative Decoding depends entirely on the **Acceptance Rate**—how often the Target model agrees with the Draft model.

**Ideal Scenarios (High Acceptance):**
- **Code Generation:** Code is highly structured. A small model can easily guess `def __init__(self):` or `import pandas as pd`, allowing the large model to verify chunks of boilerplate instantly.
- **RAG Summarization:** If the answer is verbatim in the retrieved context, the small model can easily copy it, and the large model will agree.
- **Common Phrases:** Idioms and standard grammatical structures.

**Poor Scenarios (Low Acceptance):**
- **Complex Reasoning / Math:** The draft model will guess the wrong numbers or logic steps. The target model will reject everything, meaning you wasted compute running both models. In these cases, Speculative Decoding can actually *slow down* inference.
- **Mismatched Models:** If the draft model was trained on different data than the target model, their probability distributions won't align, leading to constant rejections.

## Production Implications

Speculative Decoding is primarily used in **self-hosted infrastructure** (like vLLM or TGI). It is a highly technical optimization that requires carefully pairing models. 
For API consumers (using OpenAI or Anthropic), you cannot explicitly control speculative decoding, though the providers use variations of it under the hood to speed up their services.

When implemented correctly, the 2x-3x speedup in throughput means you can serve twice as many users on the same GPU hardware, drastically improving unit economics.

## Common Mistakes

- **Using a draft model that is too large:** If the draft model is too slow, the time spent drafting outweighs the time saved during parallel verification.
- **Using misaligned models:** Trying to use a tiny Llama model to draft for a massive Mistral model. The vocabularies and training distributions must be aligned (usually, the draft is a smaller checkpoint from the same training run).
- **Ignoring the compute overhead:** Speculative Decoding increases the total FLOPs (compute operations) performed by the GPU. If your GPU is already at 100% compute utilization (e.g., under massive concurrent load), Speculative Decoding will hurt performance. It only helps when the GPU is memory-bandwidth bound.

## Interview Questions

**Q: Explain how Speculative Decoding achieves faster generation without reducing the quality of the final output.**
**A:** It uses a small, fast model to guess a sequence of future tokens. The large target model then evaluates these guessed tokens in parallel in a single forward pass. Because the target model's probability distribution is used as the final judge to accept or reject the drafted tokens, the resulting text is mathematically identical to what the target model would have generated sequentially, just computed faster.

**Q: In what specific use case would Speculative Decoding provide the highest performance boost?**
**A:** Code generation or data extraction. In these tasks, large chunks of the output are predictable boilerplate, syntax, or verbatim copies from the prompt. The small draft model can predict these sequences highly accurately, leading to a high acceptance rate by the target model.

## Further Reading
- [Accelerating Large Language Model Decoding with Speculative Sampling](https://arxiv.org/abs/2302.01318) — The foundational research paper detailing the mathematics of acceptance criteria.
- → See [04-batching-strategies.md](04-batching-strategies.md) for another major inference optimization technique.
