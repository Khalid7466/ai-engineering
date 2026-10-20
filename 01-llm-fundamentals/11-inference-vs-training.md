# Inference vs. Training

## TL;DR
Training is the computationally massive process of updating the model's neural weights to learn patterns. Inference is the process of using that trained, frozen model to generate text. The most critical realization for AI Engineers is that models *do not learn* during inference.

---

## Frozen Weights
When you send an API call to GPT-4, or run Llama 3 locally, you are performing **inference**. 
During inference, the model's weights (the billions of parameters) are strictly read-only. 

If you tell a model, "My name is Alice," the model generates a response based on its context window. However, this interaction *does not change the model*. If you open a new session and ask, "What is my name?", it will not know, because the weights were never updated.

## The Illusion of Learning
ChatGPT feels like it learns because of the **Context Window** (→ See [08-context-window.md](08-context-window.md)). 
When you have a long conversation, the application layer (the OpenAI website) is silently appending your entire past conversation into the hidden prompt for every new message you send.

The model isn't "remembering" you; it is just reading a massive transcript of your conversation *from scratch* every single time you hit enter.

## External Memory as the Solution
Because weights are frozen, AI Engineers must build external memory systems.
1. **Short-term memory:** Passing the conversation history in the API call.
2. **Long-term memory:** Vector Databases (RAG). When the user asks a question, the application searches a database for past relevant interactions, and injects them into the prompt before inference.

## Training Cost vs. Inference Cost
**Training (Pre-training / Fine-Tuning):**
- Requires calculating gradients and doing backpropagation.
- Massive VRAM requirements (must store weights, gradients, optimizer states).
- Costs millions (pre-training) or hundreds (fine-tuning).

**Inference:**
- Only the forward pass is calculated. No gradients.
- Lower VRAM requirements (only weights and KV cache).
- Costs fractions of a cent per request.

## When to Fine-Tune (Training) vs. Use RAG (Inference)
The biggest debate in AI Engineering. 
- **Use RAG (Inference-time injection):** When you need the model to know *new facts* (e.g., proprietary company docs, live stock prices). It is cheaper, faster, and you can instantly update the database.
- **Use Fine-Tuning (Training):** When you need the model to learn a *new behavior, tone, or format* (e.g., responding exactly in a complex JSON schema, or speaking in the style of Shakespeare). 

**Never fine-tune a model just to teach it a list of facts.** The model will likely hallucinate or forget them. Use RAG.

## Production Implications
- **Stateless APIs:** LLM APIs are stateless by design. You are entirely responsible for managing state/memory in your application database.
- **Quantization:** Because inference only requires forward passes, we can heavily compress the model weights (e.g., from 16-bit floats to 4-bit integers) using techniques like AWQ or GGUF. This dramatically reduces inference VRAM and increases speed with minimal accuracy loss. You generally cannot heavily quantize during training.

## Common Mistakes
- **"I corrected the model, but it made the same mistake tomorrow."** Expecting an LLM to learn from user corrections permanently without an external database or fine-tuning pipeline.
- **Fine-tuning for knowledge injection.** Wasting thousands of dollars fine-tuning an LLM on an internal wiki, only to find it still hallucinates company policies.

## Interview Questions
- **Q: Does an LLM learn from the conversations it has with users?**
  - *A:* Not during inference. The weights are frozen. It appears to learn within a session because the conversation history is appended to the prompt, but it retains no permanent memory between isolated sessions unless the developers log that data and use it for a future training run.
- **Q: If I want an LLM to answer questions about my company's private HR policies, should I fine-tune it or use RAG?**
  - *A:* You should use RAG. Fine-tuning is for teaching behavior or format. RAG is for providing dynamic, factual context. RAG is cheaper, more accurate, and allows you to easily update policies without retraining a model.

## Further Reading
- [Hugging Face: Quantization](https://huggingface.co/docs/optimum/concept_guides/quantization) - How weights are compressed for inference.

---
<!-- nav:start -->
[Previous: Training Pipeline](10-training-pipeline.md) | [Module Overview](README.md) | [Next: Hallucination](12-hallucination.md)
<!-- nav:end -->
