</Agent System Instructions>
<Dataset Construction>
## TL;DR
A model is only as good as the dataset used to evaluate it. Constructing a "golden dataset" requires balancing statistical significance, domain coverage, and real-world noise. While synthetic data generation can bootstrap the process, datasets must be continuously updated to prevent distribution drift and overfitting.

---

## The Golden Dataset

The golden dataset is the immutable ground-truth benchmark for your system. For a RAG or QA system, a single row typically contains:
- `query`: The input from the user.
- `context`: The optimal documents required to answer the query.
- `expected_output`: The ideal response.
- `metadata`: Difficulty level, topic category, or required tools.

## How Many Examples Do You Need?

A common mistake is evaluating on 10 examples. This lacks **statistical significance**. 
- If you have 10 examples, a change in 1 answer swings your score by 10%. You cannot measure incremental progress.
- **Rule of Thumb:** A robust eval set requires a minimum of 100-300 diverse examples. At 300 examples, a 2% improvement is statistically meaningful, indicating systemic progress rather than random variance.

## Synthetic Data Generation

Manually writing 300 highly complex, accurate QA pairs is exhausting. Synthetic generation uses powerful LLMs to bootstrap the dataset.
1. Feed the LLM your raw documents.
2. Prompt it to generate 5 queries of varying difficulty (e.g., factual, comparative, reasoning) based on those documents.
3. Have humans review, edit, and filter the synthetic queries.

*Warning:* If you rely 100% on synthetic data, your eval set will lack the messy reality of human users (typos, slang, ambiguous phrasing). It evaluates how well your model talks to another AI, not to humans.

## Distribution Coverage and Adversarial Examples

A robust dataset must deliberately cover the entire input distribution:
- **Happy Path:** Standard queries that should easily succeed.
- **Edge Cases:** Queries requiring information spread across multiple documents.
- **Adversarial / Out of Bounds:** Queries trying to jailbreak the prompt, or asking questions entirely outside the system's knowledge base. (The correct behavior here is a graceful refusal, which must be evaluated).

## Dataset Drift

In production, user behavior changes over time. If your evaluation dataset is completely static, you will optimize for yesterday's problems.
- **Continuous Updating:** Every week, sample 10 queries from production that the model failed on (e.g., queries that received a thumbs-down from users). Manually write the expected optimal answer and add them to the golden dataset. This ensures the eval suite evolves alongside user behavior.

## Production Implications
Optimizing a prompt to achieve 100% on a poorly constructed, unrepresentative golden dataset guarantees production failure. This is classic "overfitting to the eval." The team celebrates high metrics internally, while users experience a broken product.

## Common Mistakes
- Using the exact same dataset for few-shot prompting and for evaluation (data leakage).
- Focusing only on "happy path" queries and ignoring adversarial or ambiguous inputs.
- Never updating the golden dataset after the initial launch.

## Interview Questions
- **Why is a golden dataset of 10 examples insufficient for evaluating an AI system?**
  *Answer:* It lacks statistical significance. A single random failure or success causes a 10% swing in metrics, making it impossible to confidently measure small, incremental improvements or detect minor regressions.
- **What is the risk of using purely synthetic data to construct an evaluation dataset?**
  *Answer:* Synthetic data often lacks the nuance, ambiguity, and messy formatting of real human queries. It tests how well the system responds to perfectly phrased AI prompts rather than real-world users.

## Further Reading
- [Building a Golden Dataset for Evaluation](https://huggingface.co/blog/evaluation-golden-dataset) — Practical guides on data curation.
