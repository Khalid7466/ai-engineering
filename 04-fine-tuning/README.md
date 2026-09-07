# Module 04: Fine-Tuning

## TL;DR
Fine-tuning adapts a pre-trained large language model (LLM) to specific tasks, domains, or styles that cannot be adequately learned through in-context learning (prompting or RAG). While highly effective for style transfer, behavior alignment, and niche domains, it is expensive and complex, making it the highest-effort rung on the AI engineering cost ladder.

---

## The Fine-Tuning Decision
The fundamental question in applied AI engineering is: **When does fine-tuning beat prompting and RAG?**

Fine-tuning is rarely the first answer. The cost hierarchy of LLM adaptation is strict:
1. **Zero-shot prompting:** Cheapest, fastest.
2. **Few-shot prompting:** Slightly more token cost, better results.
3. **Retrieval-Augmented Generation (RAG):** Adds external knowledge.
4. **Parameter-Efficient Fine-Tuning (PEFT/LoRA):** Modifies weights efficiently, moderate cost.
5. **Full Fine-Tuning:** High compute cost, modifies all weights.
6. **Pre-training from scratch:** Astronomically expensive, rarely necessary.

You should fine-tune when:
- **Style and Tone:** You need the model to output a very specific brand voice or format (e.g., JSON schema adherence) that it struggles to maintain consistently with prompting. RAG injects knowledge; fine-tuning injects style and behavior.
- **Task Specificity:** The task is highly specialized (e.g., medical diagnosis parsing) and requires deep pattern recognition across thousands of examples.
- **Latency and Cost:** You want to distill the performance of a large model (like GPT-4) into a smaller, cheaper, faster model (like Llama 3 8B) to run in production at scale.

## What This Module Covers
This module provides a comprehensive guide to modern fine-tuning in production environments, covering everything from fundamental concepts to advanced infrastructure.

1. [01-fine-tuning-overview.md](01-fine-tuning-overview.md) - The decision ladder and when to fine-tune.
2. [02-supervised-fine-tuning.md](02-supervised-fine-tuning.md) - SFT mechanics, data formats, and overfitting.
3. [03-peft-and-lora.md](03-peft-and-lora.md) - Making fine-tuning affordable with Low-Rank Adaptation.
4. [04-alignment/01-rlhf.md](04-alignment/01-rlhf.md) - Reinforcement Learning from Human Feedback.
5. [04-alignment/02-dpo.md](04-alignment/02-dpo.md) - Direct Preference Optimization.
6. [04-alignment/03-rlaif.md](04-alignment/03-rlaif.md) - Constitutional AI and AI Feedback.
7. [05-fine-tuning-data.md](05-fine-tuning-data.md) - Data quality, synthetic data, and the data flywheel.
8. [06-fine-tuning-infrastructure.md](06-fine-tuning-infrastructure.md) - GPU math, mixed precision, and DeepSpeed/FSDP.

## Production Implications
The most common production failure in fine-tuning is **catastrophic forgetting**, where adapting a model to a new task destroys its general capabilities. A fine-tuned model might become excellent at outputting JSON but lose its ability to reason logically or speak grammatically. Understanding evaluation, learning rates, and dataset composition is critical to preventing this.

## Common Mistakes
- **Fine-tuning for knowledge:** Using fine-tuning to teach a model *facts* instead of using RAG. The model will likely hallucinate the facts anyway.
- **Ignoring data quality:** Believing that 100,000 mediocre examples are better than 1,000 pristine examples.
- **Overfitting:** Training for too many epochs without a validation set, resulting in a model that memorizes the training data but fails on new inputs.
- **Underestimating infrastructure:** Starting full fine-tuning on a massive model without understanding memory requirements or gradient checkpointing.

## Interview Questions
- **Q: When would you use RAG versus Fine-tuning?**
  - **A:** Use RAG when the model needs to access external, dynamic, or proprietary knowledge (facts). Use fine-tuning when the model needs to learn a specific style, behavior, tone, or complex structural format (skills).
- **Q: What is the purpose of Parameter-Efficient Fine-Tuning (PEFT)?**
  - **A:** PEFT methods like LoRA freeze the base model weights and train a small number of new parameters. This drastically reduces the GPU memory required for optimizer states and gradients, making fine-tuning feasible on consumer or mid-tier hardware.

## Further Reading
- [LIMA: Less Is More for Alignment](https://arxiv.org/abs/2305.11206) — The foundational paper proving that data quality matters far more than quantity.
- [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685) — The original LoRA paper.
