# The Fine-Tuning Decision Ladder

## TL;DR
Fine-tuning is the process of updating a pre-trained language model's weights on a specific dataset to alter its behavior, style, or task performance. Because it is computationally expensive, requires curated data, and risks destroying the model's general capabilities, it should never be your first solution. You must follow the "Decision Ladder," exhausting prompting and RAG before touching model weights.

---

## The Decision Ladder

When faced with an AI engineering problem (e.g., "Make the model extract structured data from these medical PDFs"), engineers must navigate a strict hierarchy of approaches, balancing cost, complexity, and performance.

### 1. Zero-Shot Prompting
- **What it is:** Asking the base or instruct-tuned model directly, relying purely on its pre-trained knowledge.
- **Cost:** Near zero (just API/inference costs).
- **When to use:** Always start here to establish a baseline. If it works, stop.

### 2. Few-Shot Prompting (In-Context Learning)
- **What it is:** Providing 2-10 examples of inputs and desired outputs within the prompt itself.
- **Cost:** Low to Medium (increased token usage per API call).
- **When to use:** When the model needs to understand a specific format (e.g., JSON structure) or a nuanced task that is hard to describe purely in instructions.

### 3. Retrieval-Augmented Generation (RAG)
- **What it is:** Dynamically injecting relevant knowledge into the prompt context at runtime. → See [03-rag-architecture](../03-rag/01-rag-overview.md).
- **Cost:** Medium (requires vector database infrastructure, embedding models, and orchestration).
- **When to use:** When the model lacks specific, private, or up-to-date **knowledge** (e.g., company policies, current news, user data). RAG solves knowledge deficits; it does not solve behavior/style deficits.

### 4. Parameter-Efficient Fine-Tuning (PEFT / LoRA)
- **What it is:** Freezing the massive base model and only training a tiny adapter network (e.g., LoRA) on thousands of examples.
- **Cost:** High (requires curated training datasets, GPU instances for training, evaluation pipelines).
- **When to use:** When the model needs to learn a specific **behavior, style, or syntax** that few-shot prompting cannot reliably enforce, or when few-shot examples consume too much context window/cost.

### 5. Full Supervised Fine-Tuning (SFT)
- **What it is:** Updating all the weights (parameters) of the model.
- **Cost:** Very High (requires massive GPU memory, multi-node clusters for larger models).
- **When to use:** Rarely. Usually reserved for creating foundational instruct models (like turning Llama-3-base into Llama-3-Instruct) or highly specialized domain models (e.g., MedLM).

### 6. Pre-training
- **What it is:** Training a model from scratch on trillions of tokens.
- **Cost:** Astronomical (millions of dollars in compute).
- **When to use:** When creating a new foundational model (e.g., OpenAI, Anthropic, Meta). Not applicable for 99.9% of AI engineering.

---

## RAG vs. Fine-Tuning: The Golden Rule

The most common point of confusion is deciding between RAG and Fine-Tuning. Memorize this distinction:

**RAG is for KNOWLEDGE. Fine-Tuning is for SKILL/BEHAVIOR.**

- **Scenario A:** You want an AI to answer HR questions based on your company's 500-page employee handbook.
  - **Correct Choice:** RAG. The model needs facts. If you fine-tune the model on the handbook, it will likely hallucinate specific details and you cannot easily update it when policies change.
- **Scenario B:** You want an AI to take customer support transcripts and summarize them into a highly specific, proprietary JSON schema with strict tonal guidelines.
  - **Correct Choice:** Fine-Tuning. The model already knows English; it needs to deeply internalize a specific structural format and tone that is too complex for a prompt.

## Production Implications

Jumping straight to fine-tuning often results in a massive waste of engineering resources. 

1. **The Iteration Trap:** Prompting allows you to iterate in seconds. Fine-tuning requires hours or days to prepare data, run training, and evaluate. If you haven't validated the product idea with prompting, you will spend weeks optimizing a fine-tuned model for a feature no one wants.
2. **Maintenance Burden:** A prompt is text in a codebase. A fine-tuned model is a massive artifact that requires hosting (vLLM, TGI), version control, and monitoring for drift. 
3. **Lock-in:** If you heavily fine-tune Llama-2, and Llama-3 comes out, you have to start over. If you rely on prompting, you just swap the API endpoint.

## Common Mistakes

- **Using fine-tuning to update facts:** Thinking fine-tuning on a document will make the model reliably recite it. (It won't; LLMs are not databases).
- **Ignoring the prompt engineering baseline:** Assuming a model "can't do it" after trying a single, poorly written zero-shot prompt.
- **Underestimating data requirements:** Assuming you can fine-tune successfully with just a few dozen examples. Fine-tuning requires hundreds or thousands of highly consistent, high-quality examples.

## Interview Questions

- **Q: A client wants an AI to write marketing copy in their exact brand voice. They provide a PDF of their brand guidelines. Would you use RAG or Fine-Tuning?**
  - **A:** Neither to start. First, try few-shot prompting by putting the guidelines and 3-5 examples of good copy in the context window. If that fails consistently, use PEFT (LoRA) fine-tuning on a curated dataset of 500+ examples of perfect marketing copy. RAG is incorrect because we aren't fetching facts; we are enforcing a style.
- **Q: What is the primary disadvantage of full fine-tuning compared to prompt engineering?**
  - **A:** It is vastly more expensive, drastically slows down the iteration cycle (hours/days instead of seconds), risks catastrophic forgetting, and creates a massive infrastructure burden to host custom weights.

## Further Reading
- [RAG vs Fine-Tuning: A Comparative Analysis](https://arxiv.org/abs/2401.08406) — Academic analysis of when to use which method.
