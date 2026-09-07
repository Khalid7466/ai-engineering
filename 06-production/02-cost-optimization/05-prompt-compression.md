# Prompt Compression

## TL;DR
Prompt compression is the process of algorithmically reducing the size of an input prompt (specifically, large retrieved contexts in RAG systems) before sending it to the LLM. By removing redundant, irrelevant, or grammatically unnecessary tokens, teams can dramatically reduce API costs and improve latency (TTFT) while maintaining the semantic integrity required for the LLM to generate an accurate answer.

---

## The Problem: Context Bloat in RAG

In standard Retrieval-Augmented Generation (RAG), a user's query fetches multiple documents from a vector database. To ensure the answer is found, developers often retrieve the "Top K" chunks, which might total 3,000 to 10,000 tokens. 

This introduces three problems:
1. **Cost:** Input tokens cost money. Sending 10,000 tokens per query at scale destroys margins.
2. **Latency:** Processing massive prompts increases Time to First Token (TTFT).
3. **Lost in the Middle:** LLMs struggle to extract relevant facts hidden deep within massive contexts, often degrading performance compared to a shorter, highly-focused prompt.

Prompt compression acts as a filter *between* the retrieval step and the final LLM call.

## Compression Strategies

### 1. Extractive Compression (Selective Context)
Instead of manipulating the text at the word level, extractive compression identifies the *sentences* or *paragraphs* within the retrieved chunks that actually answer the user's query, and discards the rest.
- **Mechanism:** Often uses a Cross-Encoder (Reranker) model. 
- **Example:** A retrieved 500-token chunk from an HR manual contains 400 tokens of company history and 100 tokens about the maternity leave policy. The compressor extracts only the 100 relevant tokens.

### 2. Summarization Compression
Using a smaller, cheaper LLM (like GPT-3.5 or a local model) to summarize the retrieved documents before passing them to the expensive frontier model.
- **Pros:** Highly coherent output.
- **Cons:** Adds the latency of a full LLM generation cycle before the main generation can even begin. Usually too slow for real-time chat, but effective for offline batch processing.

### 3. Token-Level Pruning (LLMLingua)
The most advanced programmatic approach. Frameworks like [LLMLingua](https://github.com/microsoft/LLMLingua) use a small, fast model (like LLaMA-2-7B or even smaller DistilBERT variants) to calculate the **perplexity** (predictability) of every token in the prompt. 
If a token is highly predictable (e.g., stop words like "the", "a", "is", or redundant adjectives), it is mathematically removed from the prompt. 

- **Original text:** "The company was founded in the year 1999 by a group of engineers." (13 tokens)
- **LLMLingua compressed:** "company founded 1999 group engineers." (5 tokens)

To a human, the compressed text sounds like caveman speak. However, LLMs process semantic relationships mathematically; they can easily read the compressed prompt and output perfectly fluent, accurate answers based on the preserved core entities.

## When to Use Compression (The Trade-offs)

Prompt compression is not free. It requires compute (running a small LLM or cross-encoder) which adds its own latency and cost. 

**It is worth it when:**
- The retrieved context is massive (>5,000 tokens).
- You are routing the final query to a very expensive frontier model (like GPT-4). The cost saved on GPT-4 input tokens vastly outweighs the cost of running a small local compressor.

**It is NOT worth it when:**
- The prompt is already short (<1,000 tokens). The overhead of compression will slow down the system without providing meaningful cost savings.
- The task requires strict verbatim extraction (e.g., "Find the exact legal clause"). Token pruning might accidentally remove a critical legal caveat.

## Production Implications

Integrating prompt compression, specifically token pruning, introduces a risk of **quality degradation**. If the compressor removes a critical negative word (e.g., changing "is not covered" to "is covered"), the final LLM will hallucinate a dangerously incorrect response. 

Production deployments require rigorous evaluations (using frameworks like Ragas or TruLens) to ensure the compressed prompts yield the exact same final answers as the uncompressed prompts across a golden dataset.

## Common Mistakes

- **Compressing the system instructions:** You should only compress the *retrieved data*. Compressing the system prompt (the rules of engagement) often leads to guardrail failures and erratic behavior.
- **Ignoring the latency overhead:** Deploying an LLM-based summarization compressor in a real-time chatbot, causing the user to wait 8 seconds before the first token appears.
- **Over-compression:** Setting the pruning ratio too high (e.g., removing 80% of tokens), which destroys the semantic meaning and confuses the target LLM.

## Interview Questions

**Q: Explain how token-level pruning works and why an LLM can understand the compressed text even if it looks grammatically incorrect to a human.**
**A:** Token pruning uses a smaller model to calculate the perplexity of each token in the prompt. It removes highly predictable tokens (like stop words). Because LLMs operate on semantic embeddings and self-attention, they don't require perfect grammar to understand relationships between entities. As long as the core nouns, verbs, and numerical values remain, the LLM can reconstruct the intent and answer accurately.

**Q: In a RAG pipeline, at what point does prompt compression occur?**
**A:** It occurs after retrieval (and usually after reranking) but before the final generation call. The system fetches the chunks from the vector database, the compressor reduces their token footprint, and the compressed chunks are injected into the final prompt sent to the LLM.

## Further Reading
- [LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models](https://arxiv.org/abs/2310.05736) — Microsoft's paper on token pruning.
- → See [01-token-cost-fundamentals.md](01-token-cost-fundamentals.md) to understand why reducing input tokens is critical for scaling.
