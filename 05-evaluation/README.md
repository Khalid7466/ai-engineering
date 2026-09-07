</Agent System Instructions>
<Evaluation>
## TL;DR
Evaluation is the hardest and most critical part of AI engineering. Relying on vibes—"it feels better"—is a trap that prevents systematic improvement and introduces regressions into production. This module covers the foundational principles and infrastructure required to measure LLM, RAG, and agent performance effectively. The key principle: you cannot improve what you cannot measure.

---

## The Vibes-Based Development Trap

In traditional software engineering, code changes are validated by unit tests, integration tests, and static analysis. In AI engineering, the non-deterministic nature of language models makes traditional testing insufficient. 

Early in an AI project, teams often fall into the **vibes-based development trap**. They tweak a prompt, run a handful of queries manually, and declare the change a success if the output "looks better." This approach scales poorly. 

When you optimize for a small set of ad-hoc queries, you inevitably degrade performance on others. Without a systematic evaluation framework, these regressions go unnoticed until they hit production. You cannot confidently deploy a new model, prompt, or retrieval strategy if you cannot quantitatively prove it is better than the previous version.

## What This Module Covers

This module breaks down the evaluation of AI systems into five core areas:

1. **LLM Evaluation (`02-llm-evaluation/`)**: How to measure the performance of base and fine-tuned models using automated metrics, human evaluation, and LLM-as-a-judge frameworks.
2. **RAG Evaluation (`03-rag-evaluation/`)**: Frameworks like RAGAS for assessing the faithfulness, answer relevance, and context precision/recall of retrieval-augmented generation systems.
3. **Agent Evaluation (`04-agent-evaluation/`)**: The unique challenges of evaluating non-deterministic, multi-step agents, including trajectory evaluation and the credit assignment problem.
4. **Fine-Tuning Evaluation (`05-fine-tuning-evaluation/`)**: Techniques for benchmarking fine-tuned models, checking for capability regression, and mitigating catastrophic forgetting.
5. **Evaluation Infrastructure (`06-evaluation-infrastructure/`)**: How to build robust evaluation pipelines, integrate them into CI/CD, construct golden datasets, and track results over time.

## Production Implications

If you ignore evaluation, you are flying blind. In production, this manifests as:
- **Silent Regressions**: A prompt update improves edge cases but breaks core functionality.
- **Wasted Effort**: Engineering time spent on optimizations that don't actually improve user outcomes.
- **Lack of Confidence**: Inability to roll out new models (e.g., upgrading from GPT-3.5 to GPT-4o) because you don't know how it will impact the system.

## Common Mistakes
- Relying entirely on manual testing and "vibes."
- Evaluating only the final output of a multi-step agent or RAG system, ignoring the intermediate steps (e.g., retrieval quality, tool selection).
- Using reference-based metrics (e.g., BLEU, ROUGE) for open-ended generative tasks.
- Failing to build a robust, representative "golden dataset" for evaluation.

## Interview Questions
- **Why is evaluation harder for LLMs than for traditional software?** 
  *Answer:* LLMs are non-deterministic and output natural language, making exact-match string comparisons ineffective. Evaluation often requires subjective judgment or proxy metrics.
- **What is the risk of "vibes-based" evaluation?** 
  *Answer:* It leads to silent regressions, overfitting to small, non-representative test sets, and prevents confident iterations.

## Further Reading
- [Evaluating LLMs is a double-edged sword](https://huyenchip.com/2023/10/11/llm-evaluation.html) — Chip Huyen's comprehensive guide to LLM evaluation.
