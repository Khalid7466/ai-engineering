# Hallucination

## TL;DR
Hallucinations occur when an LLM generates information that is factually incorrect, nonsensical, or ungrounded in the provided context. Because LLMs are probabilistic prediction engines rather than databases of truth, they are mathematically designed to generate "plausible" text, even if that text is a complete fabrication.

---

## Root Cause: Probability ≠ Truth
An LLM's core objective is to predict the next most statistically likely token (→ See [01-what-is-an-llm.md](01-what-is-an-llm.md)). 
If you ask it for the biography of a real but obscure person, the model doesn't have enough parameter-weight memory of that person. Instead of saying "I don't know", the engine's mechanics kick in: it predicts the likely sequence of a biography (born in X, attended Y university, worked at Z). It confidently fills in those blanks with highly probable, but entirely fictional, tokens.

## Types of Hallucination
1. **Factual Fabrication:** Inventing people, historical events, or academic papers (e.g., citing a non-existent paper by a real researcher).
2. **Contextual (Ungrounded) Hallucination:** The model ignores the prompt's instructions or the provided RAG context and relies on its pre-trained weights instead.
3. **Logical/Mathematical:** Failing to carry numbers correctly in a calculation, or failing a basic syllogism despite generating fluent text about it.
4. **Temporal:** Assuming the current year is the year its training data cut off.

## Architecture-Level Solutions
You cannot fully "solve" hallucinations inside the model's weights. You must solve it at the system architecture level:

1. **Retrieval-Augmented Generation (RAG):** Provide the exact facts in the prompt and instruct the model: "Answer ONLY using the provided text. If the answer is not present, say 'I don't know'." This shifts the task from *recall* to *reading comprehension*.
2. **Tool Calling:** Give the model access to external tools (e.g., a calculator API, a web search tool). If it needs to do math, it writes a Python script instead of guessing the next token.
3. **Structured Outputs:** Force the model to output a specific JSON schema with citations (e.g., `{"fact": "...", "source_paragraph": "..."}`). Forcing it to cite its source heavily reduces fabrication.
4. **Low Temperature:** Set `temperature=0` to prevent the model from taking low-probability creative leaps when strict factual accuracy is required (→ See [09-output-head-and-sampling.md](09-output-head-and-sampling.md)).

## The Law Firm Case Study
In 2023, lawyers used ChatGPT to write a legal brief. The model fabricated several case citations, including quotes and docket numbers. The lawyers submitted it to the court and were heavily sanctioned. 
**Why it happened:** Legal language is highly structured. The model learned the exact pattern of legal citations perfectly. It generated a statistically flawless sequence of a legal citation; it just happened to map to a reality that didn't exist.

## Production Implications
- **Trust but Verify:** In high-stakes environments (medical, legal, financial), LLM outputs must be treated as drafts requiring human review, or cross-checked by secondary deterministic systems.
- **Escape Hatches:** You must explicitly prompt the model to admit ignorance. Without an "escape hatch" (e.g., "If unsure, output UNKNOWN"), the model will always attempt to guess.

## Common Mistakes
- **Assuming confidence equals accuracy:** LLMs do not have a concept of doubt unless explicitly trained to express it. A hallucination will sound just as authoritative as a true fact.
- **Trying to prompt away hallucinations entirely:** Adding "DO NOT HALLUCINATE" to a system prompt is rarely effective. You must provide grounded context.

## Interview Questions
- **Q: Why do LLMs hallucinate?**
  - *A:* Because they are designed to predict the most probable sequence of tokens based on their training distribution, not to query a database of absolute truth. When they lack specific factual knowledge, they still generate statistically plausible filler.
- **Q: How would you architect a system to minimize hallucinations in a customer support bot?**
  - *A:* I would implement a strict RAG pipeline. I would set the temperature to 0, retrieve only highly relevant help-center articles, and use a strict system prompt instructing the model to answer solely based on the retrieved articles and to fallback to human escalation if the answer isn't in the text.

## Further Reading
- [Survey of Hallucination in Natural Language Generation](https://arxiv.org/abs/2202.03629) - Academic overview of why models hallucinate.

---
<!-- nav:start -->
[Previous: Inference vs. Training](11-inference-vs-training.md) | [Module Overview](README.md) | [Next: Reasoning Failures](13-reasoning-failures.md)
<!-- nav:end -->
