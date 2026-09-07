# Grounded Generation

## TL;DR
Grounded generation is the process of forcing the LLM to synthesize an answer strictly based on the retrieved context, suppressing its parametric (internal) memory. This is the final defense against hallucinations and requires strict system prompting and citation enforcement.

---

## Suppressing Parametric Memory

LLMs naturally want to use their training data to answer questions. If the retrieved context says "The sky is green," but the LLM knows the sky is blue, a poorly prompted model will answer "The sky is blue," violating the grounding principle.

### Strict System Prompting
You must explicitly command the model to defer to the context.
- **Bad:** "Answer the user's question based on the context."
- **Good:** "You are a strict data synthesizer. Answer the question using ONLY the provided text. Do not use outside knowledge. If the context contradicts your internal knowledge, use the context. If the context does not contain the answer, reply exactly with 'I cannot answer this based on the provided documents'."

## Forcing Citations

Citations are critical for user trust and verifiability. 
- **Inline Citations:** Prompt the model to append source tags to sentences (e.g., "The revenue grew by 10% [doc_1].").
- **Post-hoc verification:** By forcing the model to cite the exact chunk, you enable downstream validation scripts to check if `doc_1` actually contains the claim.

## Handling "No Context" Scenarios

If the retrieval pipeline fails to find relevant chunks, the LLM will often try to "be helpful" and guess the answer anyway.
- **Mitigation:** The prompt must define an explicit failure state. The LLM must be given permission to fail gracefully.

## Production Implications
An ungrounded RAG system is just an expensive hallucination engine. If users cannot verify *where* the model got its answer, they will not trust the application for high-stakes enterprise decisions. Citations transform a black-box LLM answer into an auditable research report.

## Common Mistakes
- **Weak System Prompts:** Not being aggressive enough in commanding the LLM to ignore its training data.
- **Fake Citations:** The model hallucinating a citation like `[doc_4]` when only 3 documents were provided (often fixed by formatting the context strictly and using lower temperature).
- **High Temperature:** Using a high temperature (e.g., 0.8) for RAG generation. Fact retrieval should use low temperatures (0.0 - 0.1) for deterministic synthesis.

## Interview Questions
- **Q: How do you prevent an LLM from answering a question when the retrieved documents do not contain the relevant information?**
  - *Answer:* Set the temperature to 0. Use strict system prompts explicitly stating "If the context does not contain the answer, output exactly 'Insufficient context'." Additionally, implement similarity score thresholds in the retrieval step to prevent irrelevant documents from reaching the prompt in the first place.

## Further Reading
- [Evaluating RAG Systems (RAGAS)](https://github.com/explodinggradients/ragas) — Metrics for measuring groundedness and faithfulness.
