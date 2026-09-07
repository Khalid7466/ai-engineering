# Reranking

## TL;DR
Reranking is a secondary filtering stage. A vector database retrieves a broad set of candidates (e.g., Top 20) very quickly using bi-encoders, and then a heavy, highly accurate cross-encoder scores and reorders them, sending only the absolute best (e.g., Top 5) to the LLM.

---

## Bi-Encoders vs Cross-Encoders

### Bi-Encoders (The Vector Database)
- **How it works:** The query and the document are embedded separately. Their similarity is computed using a simple dot product or cosine distance.
- **Pros:** Incredibly fast. Document embeddings can be pre-computed and indexed.
- **Cons:** Shallow understanding. The model never looks at the query and the document at the same time.

### Cross-Encoders (The Reranker)
- **How it works:** The query and the document are concatenated (e.g., `[CLS] Query [SEP] Document [SEP]`) and passed through a Transformer model *together*. The model outputs a relevance score from 0 to 1.
- **Pros:** Deep, highly accurate understanding of the relationship between the exact query and the document text.
- **Cons:** Too slow to run on millions of documents. Cannot be pre-computed.

## The Two-Stage Retrieval Pipeline

To get the best of both worlds, modern RAG systems use a two-stage pipeline:
1. **Stage 1 (Retrieval):** The Vector DB uses Bi-Encoders to instantly retrieve the Top 20-50 candidates from millions of records.
2. **Stage 2 (Reranking):** A Cross-Encoder model (like Cohere Rerank or BGE-Reranker) scores those 20-50 candidates against the specific query. 
3. **Selection:** The system discards the lowest scorers and passes only the Top 3-5 to the LLM context window.

## Production Implications
Reranking is arguably the highest ROI addition to a standard RAG pipeline. Dense vector search is noisy. A document might rank #1 in vector search because it shares vocabulary, but rank #15 in actual usefulness. A cross-encoder fixes this alignment. The latency cost (typically 50-200ms) is well worth the dramatic increase in prompt context quality.

## Common Mistakes
- **Reranking Too Many Docs:** Passing 1,000 documents to a cross-encoder will cause massive latency spikes and API costs.
- **Skipping Reranking:** Relying solely on the raw Cosine Similarity score from the vector database to order context for the LLM.

## Interview Questions
- **Q: Why can't we use Cross-Encoders for the initial database search?**
  - *Answer:* Cross-encoders must process the query and the document simultaneously. You cannot pre-compute cross-encoder scores. Running a heavy transformer model in real-time against millions of documents for every user query would take hours and immense compute.

## Further Reading
- [Cohere Rerank Documentation](https://docs.cohere.com/docs/reranking) — Excellent explanation of the two-stage pipeline.
