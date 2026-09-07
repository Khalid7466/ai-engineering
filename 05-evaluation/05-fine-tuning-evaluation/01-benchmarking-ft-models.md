</Agent System Instructions>
<Benchmarking Fine-Tuned Models>
## TL;DR
Evaluating a fine-tuned model requires comparing it against its base model to prove that the fine-tuning actually improved task performance without degrading general capabilities. This is achieved using held-out test sets from the fine-tuning distribution and cross-distribution evaluation to test for generalization.

---

## The Baseline Comparison

Never evaluate a fine-tuned model in isolation. You must always run the exact same evaluation suite on the **base model** (e.g., Llama-3-8B) and the **fine-tuned model**. 
If the base model achieves 80% accuracy on your task with a 5-shot prompt, and your fine-tuned model achieves 82%, the expensive fine-tuning process was likely not worth the operational overhead.

## Evaluation Distributions

### 1. In-Distribution Evaluation (Held-out Test Set)
When creating a fine-tuning dataset, randomly hold out 10-20% of the data. 
- **Purpose:** Measures how well the model learned the specific format, tone, or task it was trained on.
- **Risk:** High scores here do not prove the model is good; they only prove the model memorized the specific style of the training data.

### 2. Out-of-Distribution Evaluation (Cross-Distribution)
Test the model on data that is related to the task but formatted differently or drawn from a different source.
- **Example:** If fine-tuned on Python code summarization, evaluate it on JavaScript code summarization.
- **Purpose:** Measures *generalization*. Did the model learn the underlying concept, or did it just overfit to the exact syntax of your training set?

### 3. General Capability Benchmarks (Regression Testing)
Run standard benchmarks (e.g., MMLU, standard conversational evals).
- **Purpose:** Checks for capability regression. Fine-tuning forcefully pushes model weights in a specific direction. You need to ensure you haven't destroyed the model's fundamental ability to speak English or reason logically. 
- *(Reference: → See [02-catastrophic-forgetting.md](./02-catastrophic-forgetting.md))*

## The "Tax" of Fine-Tuning
Fine-tuning often introduces an "alignment tax." A base model that is highly creative might become overly rigid and repetitive after being fine-tuned on a strict JSON-output task. Evaluation must capture whether this tradeoff is acceptable for your specific use case.

## Production Implications
Deploying a fine-tuned model without evaluating cross-distribution performance often leads to brittle systems. The model will perform flawlessly in demos (using data similar to the training set) but fail completely in production when users phrase their queries slightly differently than the training examples.

## Common Mistakes
- Evaluating the fine-tuned model on the training data (data leakage).
- Failing to establish a baseline with the base model, masking the fact that few-shot prompting might have been sufficient.
- Only measuring in-distribution performance and ignoring general capability regression.

## Interview Questions
- **Why is it critical to evaluate a fine-tuned model on an out-of-distribution dataset?**
  *Answer:* To ensure the model has actually generalized the task concepts rather than just overfitting to the specific format and phrasing of the training dataset.
- **What is capability regression in the context of fine-tuning?**
  *Answer:* It is when fine-tuning a model on a specific narrow task degrades its general reasoning, knowledge, or conversational abilities that were present in the base model.

## Further Reading
- [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685) — Understanding how parameter-efficient methods impact performance.
