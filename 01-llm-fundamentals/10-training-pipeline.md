# Training Pipeline

## TL;DR
Creating an LLM like GPT-4 or Llama 3 is not a single step. It is a multi-stage pipeline: Pre-training builds world knowledge, Supervised Fine-Tuning (SFT) teaches it to act like an assistant, and RLHF/DPO aligns it with human preferences (making it safe and helpful).

---

## 1. Pre-training (Base Model)
**Objective:** Next-token prediction at massive scale.
**Data:** Trillions of tokens (the entire internet, books, Wikipedia, GitHub).
**Compute:** Requires thousands of GPUs running for months (costing tens of millions of dollars).
**Output:** A "Base Model" (e.g., Llama-3-8B). 

A base model is incredibly smart but practically useless as a chatbot. If you prompt it with "What is the capital of France?", it might respond with "What is the capital of Germany? What is the capital of Italy?" because it is trying to complete a pattern (a list of trivia questions) rather than answer you.

## 2. Supervised Fine-Tuning (SFT)
**Objective:** Teach the model instruction following and formatting.
**Data:** Tens of thousands of high-quality, human-written Q&A pairs (Prompt + Ideal Response).
**Compute:** Much cheaper, often requiring a few GPUs for a few days.
**Output:** An "Instruct" model.

During SFT, the model learns the ChatML or system-prompt format. It learns that when it sees `<|user|>`, it should wait for `<|assistant|>` and then generate a helpful answer instead of continuing the user's thought.

## 3. Human Preference Alignment (RLHF / DPO)
**Objective:** Make the model's tone helpful, harmless, and honest. SFT models can sometimes be abrasive, overly verbose, or willing to generate dangerous code.
**Data:** Human preference rankings (e.g., Output A is better than Output B).

### RLHF (Reinforcement Learning from Human Feedback)
1. Train a separate "Reward Model" on human preference data to score outputs.
2. Use Reinforcement Learning (PPO) to update the LLM to generate outputs that score highly on the Reward Model.
RLHF is highly complex and unstable to train.

### DPO (Direct Preference Optimization)
A modern alternative that bypassed the need for a separate Reward Model and complex PPO. DPO directly updates the LLM weights by increasing the probability of the "Good" human response and decreasing the probability of the "Bad" human response. It has largely replaced RLHF for open-source model alignment due to its simplicity and stability.

## Production Implications
- **Choosing the right model:** Never deploy a "Base" model for an API chatbot application. Always look for `-Instruct` or `-Chat` variants.
- **When to fine-tune:** If prompt engineering fails, you might need to do your own SFT using LoRA (Low-Rank Adaptation) on your proprietary data. However, you generally *cannot* do Pre-training or RLHF yourself.
- **Alignment Tax:** Sometimes the RLHF phase makes a model *too* safe, causing it to refuse harmless prompts (e.g., refusing to write code for a hacking tutorial meant for defense). This is known as the alignment tax.

## Common Mistakes
- **Confusing Fine-Tuning with RAG:** Thinking that fine-tuning a model on company PDFs is the best way to make it answer questions about those PDFs. (Use RAG instead; fine-tuning is for teaching *behavior/format*, RAG is for *knowledge*). (→ See [11-inference-vs-training.md](11-inference-vs-training.md))
- **Underestimating data quality:** In SFT, data *quality* vastly outweighs data *quantity*. 1,000 perfect, human-verified examples are better than 100,000 scraped, messy examples. "Garbage in, garbage out."

## Interview Questions
- **Q: Why can't you just use a base model like Llama-3-Base for a customer support chatbot?**
  - *A:* Base models are trained solely for next-token prediction on web text. They tend to continue patterns rather than follow instructions or answer questions. They must undergo Supervised Fine-Tuning (SFT) to learn the Q&A format.
- **Q: What is DPO and why is it popular?**
  - *A:* Direct Preference Optimization is a method for aligning LLMs to human preferences. It is popular because it achieves similar results to RLHF but is mathematically simpler, more stable to train, and doesn't require maintaining a separate reward model.

## Further Reading
- [InstructGPT Paper](https://arxiv.org/abs/2203.02155) - The paper that popularized RLHF (the foundation of ChatGPT).
- [DPO Paper](https://arxiv.org/abs/2305.18290) - The paper introducing Direct Preference Optimization.
