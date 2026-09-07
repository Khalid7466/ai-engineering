# Embedding Model Selection

## TL;DR
Selecting an embedding model requires balancing performance (accuracy), latency, cost, and language support. The MTEB benchmark is the standard for evaluating models, but domain-specific testing is essential before committing to a model for production.

---

## The MTEB Benchmark

The Massive Text Embedding Benchmark (MTEB) is the industry standard leaderboard for embedding models. It evaluates models across various tasks: retrieval, classification, clustering, and semantic textual similarity (STS). 
When building RAG, you should look specifically at the **Retrieval** tab on MTEB, not just the overall average.

## Model Ecosystem Overview

### API-Based Models
- **OpenAI (`text-embedding-3-large` / `small`):** The default choice. Excellent performance, native Matryoshka support (variable dimensions), and very cheap.
- **Cohere (`embed-v3-english` / `multilingual`):** Top-tier performance. Uniquely trained to measure the relevance of a document to a query, rather than just raw semantic similarity.

### Open-Source / Local Models
- **BGE (BAAI General Embedding, e.g., `bge-m3`):** State-of-the-art open-source models. The `M3` variant supports Multi-linguality, Multi-granularity (different chunk sizes), and Multi-Functionality (dense and sparse embeddings).
- **E5 (e.g., `e5-large-v2`):** Microsoft's open-source powerhouse. Requires specific prefixes (e.g., adding "query: " or "passage: ") to function correctly.

## Selection Criteria

1. **Domain Specificity:** If you are working in medical or legal domains, generic models might fail. You may need domain-adapted models (e.g., MedCPT).
2. **Multilingual Needs:** If your documents are in German but queries are in English, you must use a strong multilingual model (like `Cohere-multilingual` or `bge-m3`).
3. **Data Privacy:** If you cannot send data to cloud APIs, you must deploy an OSS model like BGE locally.

## Production Implications
Switching embedding models in production requires re-embedding your entire knowledge base. If you have 50 million documents, this will cost significant time and money. Choose your model carefully during the prototyping phase.

## Common Mistakes
- **Chasing the MTEB Leaderboard:** Switching models every time a new one tops the MTEB leaderboard, wasting resources on re-indexing for a 0.5% gain in accuracy.
- **Forgetting Prefixes:** Using E5 models without the required "query: " or "passage: " prefixes, destroying retrieval performance.

## Interview Questions
- **Q: Why might you choose a local, open-source embedding model over OpenAI's API?**
  - *Answer:* Data privacy compliance (keeping sensitive data on-premise), avoiding API latency, removing vendor lock-in, and the ability to fine-tune the model on domain-specific vocabulary.

## Further Reading
- [MTEB Leaderboard (HuggingFace)](https://huggingface.co/spaces/mteb/leaderboard) — The current rankings for embedding models.
