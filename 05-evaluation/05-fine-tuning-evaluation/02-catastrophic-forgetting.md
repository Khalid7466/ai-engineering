</Agent System Instructions>
<Catastrophic Forgetting>
## TL;DR
Catastrophic forgetting occurs when a neural network is fine-tuned on a new task and abruptly forgets the knowledge or capabilities it learned during pre-training. In LLMs, this manifests as a model that excels at a narrow fine-tuned task but loses its ability to hold a normal conversation, follow general instructions, or reason.

---

## The Mechanism of Forgetting

During pre-training, an LLM's weights are carefully balanced across billions of parameters to encode a vast array of concepts. When you fine-tune the model on a narrow dataset (e.g., 10,000 examples of translating English to SQL), the gradient updates forcefully shift those weights to optimize for SQL generation. 
Because the model has finite capacity, the weights that previously encoded French translation or historical facts get overwritten.

## How to Detect It

You cannot detect catastrophic forgetting by evaluating the task you fine-tuned on. You must detect it by evaluating the tasks you *didn't* fine-tune on.
- **Baseline Check:** Run standard benchmarks (e.g., MMLU, MT-Bench) on the base model.
- **Post-FT Check:** Run the exact same benchmarks on the fine-tuned model.
- If the MMLU score drops from 70 to 45, catastrophic forgetting has occurred.

## Mitigation Strategies

### 1. Parameter-Efficient Fine-Tuning (PEFT / LoRA)
Instead of updating all billions of parameters (Full Fine-Tuning), techniques like LoRA (Low-Rank Adaptation) freeze the base model and only train a small, separate set of adapter weights.
- **Why it helps:** The base model's knowledge remains perfectly intact. The model is less likely to forget general capabilities because the foundational weights are physically locked.

### 2. Replay Buffers (Data Mixing)
When constructing your fine-tuning dataset, mix in a percentage (e.g., 10-20%) of general instruction-tuning data or data from previous tasks.
- **Why it helps:** It forces the model to calculate gradients that optimize for both the new task (SQL generation) and the old tasks (general conversation) simultaneously, preserving both.

### 3. Lower Learning Rates and Early Stopping
Aggressive learning rates cause massive weight updates, accelerating forgetting. Using a small learning rate and stopping the training process before the validation loss fully plateaus can preserve general knowledge.

### 4. Elastic Weight Consolidation (EWC)
A more advanced algorithmic approach that adds a penalty to the loss function if the model tries to heavily alter weights that were deemed "important" for previous tasks. (Less common in standard LLM fine-tuning, but foundational in continual learning).

## Production Implications
If you deploy a model suffering from catastrophic forgetting to a user-facing chatbot, it might answer domain-specific questions perfectly, but respond with gibberish or SQL code when the user says "Hello" or asks an off-topic question. It destroys the illusion of intelligence.

## Common Mistakes
- Doing full-parameter fine-tuning on a tiny dataset with a high learning rate.
- Only evaluating the fine-tuned model on the target task, hiding the fact that the model is now lobotomized for everything else.
- Assuming PEFT entirely eliminates forgetting (it reduces it significantly, but severe overfitting on the adapter can still hijack the model's outputs).

## Interview Questions
- **What is catastrophic forgetting, and how do you detect it in an LLM?**
  *Answer:* It is the loss of previously learned capabilities when training on new data. You detect it by running general benchmarks (like MMLU or conversational evals) before and after fine-tuning and measuring the degradation.
- **How does mixing data (replay) mitigate catastrophic forgetting?**
  *Answer:* By including examples of general tasks alongside the new domain-specific data, the loss function forces the model to update weights in a way that accommodates both, rather than completely overwriting old knowledge.

## Further Reading
- [Overcoming catastrophic forgetting in neural networks](https://arxiv.org/abs/1612.00796) — The foundational paper on the phenomenon in deep learning.
