# Chunking Strategies

## TL;DR
Chunking is the process of splitting long documents into smaller segments for embedding and retrieval. The goal is to maximize semantic density—ensuring each chunk contains a complete, self-contained thought. The choice of strategy heavily impacts both retrieval accuracy and generation context.

---

## Why Chunking Matters

Embedding models have finite context windows (e.g., 512 or 8192 tokens). You cannot embed a 100-page book as a single vector. Even if you could, a single vector representing an entire book would be so semantically diluted that it would be useless for answering specific queries. 

### Strategy 1: Fixed-Size Chunking
- **Mechanism:** Split text every N characters or tokens.
- **Pros:** Simple, fast to implement.
- **Cons:** "Dumb." It routinely cuts sentences or paragraphs in half, destroying context. 

### Strategy 2: Recursive Character Splitting (The Standard)
- **Mechanism:** Tries to split on logical boundaries (paragraphs `\n\n`, then sentences `\n`, then words) until the chunks are below the maximum size. It uses a sliding window (overlap) to ensure context isn't lost at the edges.
- **Pros:** Preserves sentence boundaries, good default choice.
- **Cons:** Still fundamentally structural, not semantic.

### Strategy 3: Semantic Chunking
- **Mechanism:** Uses a small embedding model or statistical method to calculate the similarity between sequential sentences. It creates a chunk boundary only when there is a significant shift in topic (a drop in similarity score).
- **Pros:** Highly coherent chunks.
- **Cons:** Computationally expensive during ingestion.

### Strategy 4: Parent-Child Chunking (Auto-merging)
- **Mechanism:** Document is split into large parent chunks, which are further split into small child chunks. Only the child chunks are embedded and indexed. When a child chunk is matched during retrieval, the system returns the larger parent chunk to the LLM.
- **Pros:** Optimizes for both high-precision retrieval (small chunks) and rich context for generation (large chunks).

## Production Implications
Choosing the wrong chunking strategy leads to the "context fragmentation" problem. If a chunk contains the answer, but the subject of the sentence was in the previous chunk, the LLM cannot answer the question. Overlap helps, but Parent-Child chunking is often required in production to ensure the LLM has enough surrounding context to formulate a robust answer.

## Common Mistakes
- **No Overlap:** Using fixed-size chunks without overlap, guaranteeing broken sentences.
- **Chunks Too Small:** Creating 50-token chunks. They retrieve well but lack enough context for the LLM to generate a coherent answer.
- **Chunks Too Large:** Creating 2000-token chunks. The embedding becomes diluted, making retrieval imprecise.

## Interview Questions
- **Q: Explain the Parent-Child chunking strategy and why it is useful.**
  - *Answer:* It embeds small child chunks for precise vector search, but retrieves the larger parent chunk for the LLM prompt. This solves the tradeoff between needing small chunks for high retrieval accuracy and large chunks for sufficient generation context.

## Further Reading
- [LlamaIndex: Node Parsers & Chunking](https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/) — Excellent overview of advanced chunking implementations.
