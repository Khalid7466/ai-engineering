## TL;DR
Standard RAG (Retrieval-Augmented Generation) is the foundational architectural pattern for grounding LLMs in external knowledge. It is a fixed-path pipeline characterized by a single, definitive retrieval step followed by a generation step. It is the correct choice when a user's query can be mapped directly to relevant documents in a single search operation.

---

## The System Design Perspective

Module 02 covered the mechanics of RAG (chunking, embeddings, vector databases). In this module, we view RAG as a system design pattern. 

Standard RAG is fundamentally a **predictable pipeline**. 
1. **Query Transformation:** (Optional) Clean or rewrite the user query.
2. **Retrieval:** Execute a search (Vector/Hybrid) against a database.
3. **Augmentation:** Inject the retrieved text into a prompt template.
4. **Generation:** The LLM produces an answer.

The critical assumption of Standard RAG is the **Single-Pass Assumption**: The system assumes that one query to the database will return all necessary information required to answer the prompt.

## When Standard RAG is the Right Choice

Standard RAG is ideal for **needle-in-a-haystack** retrieval and straightforward factual inquiries where the vocabulary of the query closely matches the vocabulary of the documents.

**Perfect Use Cases:**
- "What is the company policy on remote work?"
- "How do I reset my router according to the manual?"
- "What did the CEO say about Q3 earnings in the transcript?"

**When it fails (and requires Agentic RAG):**
- **Multi-hop reasoning:** "Who is the manager of the person who wrote the Q3 report?" (Requires finding the author, then finding their manager).
- **Aggregation:** "What are the common themes across all 500 support tickets?" (A vector search will just return the 5 most similar tickets, missing the global context).

## Production Implications

### Context Window Stuffing
In production, engineers often try to solve poor retrieval by simply returning *more* chunks (e.g., top-K = 50). 
**The Failure:** LLMs suffer from "Lost in the Middle" syndrome. If you stuff 30,000 tokens of retrieved chunks into the prompt, the model will often ignore the context in the middle and hallucinate, while your API costs skyrocket and latency balloons to 10+ seconds.
**The Fix:** Rely on better retrieval (hybrid search, re-ranking) to return fewer, higher-quality chunks (top-K = 5 to 10), keeping the context tight and relevant.

### The "No Results" Trap
If the vector search returns chunks with low similarity scores, Standard RAG will often still try to answer the question using its parametric memory (hallucinating), or it will awkwardly state it doesn't know based on the context.
**The Fix:** Implement a deterministic threshold. If the top retrieved chunk has a similarity score below 0.75 (depending on the embedding model), short-circuit the pipeline and return a canned response ("I don't have information on that in my knowledge base") without even calling the LLM generation step. This saves money and prevents hallucinations.

## Common Mistakes
- **Treating RAG as a magic bullet for all data tasks:** Standard RAG is terrible at structured data (SQL). Don't put tabular data into a vector database; use Text-to-SQL prompt chaining instead.
- **Ignoring metadata:** Relying purely on semantic search is a mistake. In a multi-tenant SaaS app, if you don't aggressively filter by `tenant_id` before doing the vector search, you will leak data between customers.
- **Over-engineering early:** Teams often jump to GraphRAG or Agentic RAG before optimizing their chunking strategy or adding a Cross-Encoder Re-ranker to Standard RAG. Fix the basics first.

## Interview Questions
- **Q: Your Standard RAG system works locally, but in production, responses take 8 seconds. Users are abandoning the chat. How do you re-architect it?**
  - *Answer:* RAG latency is dominated by the LLM generation step, which scales with input context length and output token count. First, implement a Semantic Cache (e.g., RedisVL) to serve repeat queries instantly. Second, reduce the `top_k` retrieved chunks to shrink the input context. Third, switch the generation model to a faster tier (e.g., from GPT-4o to GPT-4o-mini). Finally, stream the output to the UI so perceived latency is lower.
- **Q: Explain the "Lost in the Middle" phenomenon and how it affects RAG design.**
  - *Answer:* Research shows LLMs attend well to the very beginning and very end of their context window, but degrade in the middle. In RAG, if you inject 20 documents, the answer might be missed if it's in document 10. System design mitigations include strict chunk limits, using a Re-ranker to ensure the most relevant chunks are placed at the very top or bottom of the prompt, or using prompt chaining to evaluate chunks in smaller batches.

## Further Reading
- [Advanced RAG Techniques](https://pub.towardsai.net/advanced-rag-techniques-an-illustrated-overview-04d193d8fec6) — Comprehensive overview of moving beyond basic RAG.

→ See [03-agentic-rag.md](03-agentic-rag.md) for what to do when the Single-Pass Assumption fails.
