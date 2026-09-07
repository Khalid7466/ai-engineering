# Module 01: LLM Fundamentals

## TL;DR
This module covers the core theoretical and practical foundations of Large Language Models (LLMs) needed by AI Engineers. It bridges the gap between high-level conceptual understanding and low-level engineering considerations, focusing heavily on how these concepts impact production applications.

---

## Learning Path

This module is designed to be read sequentially, building from basic concepts up to architectural components, and finally to practical application and common pitfalls. 

1. **Foundations**: We begin with [01-what-is-an-llm.md](01-what-is-an-llm.md) to establish the objective (next-token prediction) and move into how text becomes numbers through [02-tokenization.md](02-tokenization.md).
2. **Architecture**: We dive into the internal mechanics of the models. You will learn about internal representations ([03-embeddings.md](03-embeddings.md)), sequence order ([04-positional-encoding.md](04-positional-encoding.md)), the overarching structure ([05-transformer-architecture.md](05-transformer-architecture.md)), and its core components: [06-self-attention.md](06-self-attention.md) and [07-feed-forward-network.md](07-feed-forward-network.md).
3. **Execution & Lifecycle**: Understanding memory and output generation through [08-context-window.md](08-context-window.md) and [09-output-head-and-sampling.md](09-output-head-and-sampling.md). We then cover the model lifecycle: [10-training-pipeline.md](10-training-pipeline.md) and [11-inference-vs-training.md](11-inference-vs-training.md).
4. **Failure Modes**: Exploring why LLMs fail with [12-hallucination.md](12-hallucination.md) and [13-reasoning-failures.md](13-reasoning-failures.md).
5. **Practical Application**: We wrap up with applied topics: [14-prompt-engineering.md](14-prompt-engineering.md), [15-model-selection.md](15-model-selection.md), and [16-llm-apis-and-sdks.md](16-llm-apis-and-sdks.md).

Check out [use-case.md](use-case.md) for a real-world scenario of debugging an LLM system in production.

## Prerequisites
- Basic understanding of Python.
- Familiarity with the concept of an API.
- Basic linear algebra (vectors and matrices) is helpful but not strictly required.

## Production Implications
Understanding these fundamentals is not merely academic. It directly translates to cost optimization, latency reduction, and increased reliability in production. For instance, knowing how tokenization works explains why certain languages cost more to process, and understanding the context window limits prevents "lost in the middle" retrieval failures.

## Further Reading
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) - The original Transformer paper.
- [OpenAI Platform Docs](https://platform.openai.com/docs/) - Practical guidance on APIs and prompt engineering.
