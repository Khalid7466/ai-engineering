# Context Assembly

## TL;DR
Context assembly is the art of combining retrieved chunks, user queries, system instructions, and formatting into the final prompt sent to the LLM. Poor assembly leads to the "Lost in the Middle" phenomenon, where the model ignores critical facts, causing hallucinations despite perfect retrieval.

---

## Prompt Structure

A robust RAG prompt must clearly demarcate instructions from context. Use XML tags or Markdown to separate them, preventing prompt injection and confusion.

```text
You are a factual assistant. Answer the question using ONLY the provided <context>. 
If the context does not contain the answer, say "I don't know."

<context>
[Document 1: ...]
[Document 2: ...]
</context>

Question: {user_query}
```

## The "Lost in the Middle" Problem

LLMs have an attention distribution problem. Research shows that models exhibit a "U-shaped" attention curve:
- They perfectly recall information at the **very beginning** of the prompt.
- They perfectly recall information at the **very end** of the prompt.
- They severely degrade at recalling information stuck in the **middle** of the prompt.

### Ordering Strategies
Because of this phenomenon, chronological or arbitrary ordering of chunks is dangerous.
- **Optimal Ordering:** Place the highest-scoring (most relevant) chunks at the extreme ends of the context window.
  - Chunk #1 (Highest score) -> Placed at the very top.
  - Chunk #2 -> Placed at the very bottom.
  - Chunks #3, #4, #5 -> Placed in the middle.

## Context Window Budgeting

Just because a model has a 128k token context window doesn't mean you should fill it.
- **Cost:** API costs scale linearly with tokens.
- **Latency:** Time-to-first-token (TTFT) degrades as prompt length increases.
- **Distraction:** More chunks mean more irrelevant noise, increasing hallucination rates.
- **Rule of Thumb:** Cap your context to the Top 3-5 highly relevant, reranked chunks unless synthesizing across a massive dataset is explicitly required.

## Production Implications
Failing to structure the prompt with clear delimiters allows the LLM to confuse user input with retrieved context. If a retrieved document contains a hypothetical question, the LLM might answer the document's question instead of the user's question.

## Common Mistakes
- **Blind Concatenation:** Smushing chunks together without document boundaries (e.g., `Doc 1`, `Doc 2`), preventing the model from citing sources.
- **Context Stuffing:** Passing 50 chunks into GPT-4 just because it fits, leading to slow, expensive, and degraded responses.
- **Ignoring Attention Curves:** Putting the best document in the middle of a 20k token prompt.

## Interview Questions
- **Q: What is the "Lost in the Middle" phenomenon in LLMs, and how do you mitigate it in RAG?**
  - *Answer:* It's the tendency of LLMs to ignore or forget information located in the center of a long prompt, focusing instead on the beginning and end. To mitigate this, RAG systems should place the most highly relevant retrieved chunks at the very beginning and very end of the context section.

## Further Reading
- [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)
