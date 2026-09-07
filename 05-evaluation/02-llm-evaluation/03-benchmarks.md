</Agent System Instructions>
<Benchmarks>
## TL;DR
Public benchmarks like MMLU, HumanEval, and HELM provide standardized tests to compare base and fine-tuned models. The `lm-evaluation-harness` makes running these accessible. However, benchmarks must be interpreted with extreme skepticism due to data contamination, task-specific overfitting, and the disconnect between benchmark scores and real-world utility.

---

## Key Benchmarks

### MMLU (Massive Multitask Language Understanding)
Tests knowledge breadth across 57 subjects (math, history, law, medicine) using multiple-choice questions. It is the standard proxy for general knowledge capability.

### HumanEval
Created by OpenAI, it evaluates coding capabilities by prompting the model to complete Python functions based on docstrings. Evaluated using `pass@k` (does at least one of *k* generated samples pass the hidden unit tests?).

### HellaSwag & ARC
- **HellaSwag:** Tests commonsense natural language inference (picking the most logical completion to a sentence).
- **ARC (AI2 Reasoning Challenge):** Grade-school science questions, split into Easy and Challenge sets.

### HELM (Holistic Evaluation of Language Models)
A comprehensive framework by Stanford that evaluates models across diverse scenarios and metrics (accuracy, fairness, bias, toxicity), rather than just raw performance.

## Running Benchmarks: lm-evaluation-harness
EleutherAI's `lm-evaluation-harness` is the industry standard for evaluating open-source models. It provides a unified interface to run hundreds of benchmarks locally against Hugging Face, vLLM, or API-based models.

```bash
# Running MMLU against a local model
lm_eval --model hf \
    --model_args pretrained=meta-llama/Llama-3-8B \
    --tasks mmlu \
    --device cuda:0 \
    --batch_size 8
```

## The Contamination Problem
Because LLMs are trained on massive scrapes of the internet, benchmark test sets (which are public) inevitably leak into the training data.
- **Data Contamination:** The model isn't "reasoning" through the MMLU question; it simply memorized the answer during pre-training.
- **Mitigation:** De-contamination checks (searching training data for benchmark n-grams) are standard, but newer methods rely on creating private, held-out eval sets that are never published.

## Production Implications
Optimizing a fine-tune purely to increase MMLU or HumanEval scores often leads to catastrophic forgetting or degradation in the specific tasks your users actually care about. A model that scores 85 on MMLU might still fail completely at your proprietary data extraction task. 

## Common Mistakes
- Assuming a model with a higher MMLU score will perform better on a domain-specific RAG task.
- Fine-tuning on data that unintentionally includes benchmark test sets, leading to artificially inflated performance.
- Using 0-shot evaluation for one model and 5-shot evaluation for another, then comparing the scores.

## Interview Questions
- **What does data contamination mean in the context of LLM benchmarks?**
  *Answer:* It occurs when the questions and answers from a benchmark test set are accidentally included in the model's training data, allowing the model to memorize the answers and artificially inflating its score.
- **What does the HumanEval benchmark measure, and how is it evaluated?**
  *Answer:* It measures Python coding capability. It is evaluated using the pass@k metric, where the model generates k code completions, and the test is passed if at least one completion successfully passes a suite of hidden unit tests.

## Further Reading
- [Language Model Evaluation Harness](https://github.com/EleutherAI/lm-evaluation-harness) — EleutherAI's GitHub repository.
