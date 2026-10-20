# Embeddings

## TL;DR
Embeddings are dense vector representations of text where semantic meaning is mapped to geometric space. They are the fundamental way language models translate discrete tokens into continuous numbers that neural networks can process. Words with similar meanings are located close to each other in this multidimensional space.

---

## Vector Space Geometry
When a token is passed into an LLM, the first step is an embedding lookup. A token like "king" is converted into a list of floating-point numbers (e.g., a vector of 4096 dimensions).

This vector represents the concept's location in a high-dimensional space. The remarkable property of embeddings learned through massive pre-training is that geometric relationships encode semantic relationships.

- **Similarity:** The vector for "cat" will have a high cosine similarity (it points in the same direction) to the vector for "dog" because they appear in similar contexts (pets, animals, feeding).
- **Relational Math:** The classic example is vector arithmetic: `Vector("King") - Vector("Man") + Vector("Woman") ≈ Vector("Queen")`.

## Internal LLM Embeddings vs. External RAG Embeddings
It is critical to distinguish between two ways the term "embeddings" is used in AI Engineering:

1. **Internal LLM Embeddings:** The very first layer of a model like Llama 3 or GPT-4. It maps token IDs to vectors *before* they pass through the Transformer blocks. You generally do not interact with these directly when using APIs.
2. **External Embeddings (for RAG):** Specialized models (like `text-embedding-3-small` or BGE-M3) trained explicitly to map entire sentences or paragraphs into a single vector. We use these to index documents in a Vector Database for Retrieval-Augmented Generation (RAG).

While they use the same underlying concept, an LLM's internal token embeddings are optimized for predicting the next token, whereas external embedding models are optimized for semantic search (making a query vector close to the relevant document vector).

## Production Implications
- **Curse of Dimensionality:** Higher-dimensional embeddings (e.g., 3072 dims) capture more nuance but require significantly more RAM and compute to store and search in a vector database compared to smaller embeddings (e.g., 768 dims).
- **Out of Vocabulary/Domain:** If your data contains highly specific jargon (e.g., internal company acronyms or novel medical terms) that the embedding model wasn't trained on, the resulting vectors will be poor representations, leading to bad search results in RAG.
- **Asymmetric Search:** In production RAG, queries are short ("how do I reset password") and documents are long. Some embedding models struggle with this asymmetry.

## Common Mistakes
- **Confusing the two types of embeddings:** Thinking you can extract the first layer of GPT-4 and use it for a vector database. You need a dedicated embedding model for search.
- **Ignoring chunking strategies:** Embedding a whole 50-page PDF into a single vector dilutes the semantic meaning to noise. You must chunk text (e.g., 500 tokens) before embedding.
- **Using Euclidean distance instead of Cosine Similarity:** While often correlated, Cosine Similarity (angle between vectors) is generally preferred over Euclidean distance (magnitude) for text embeddings, as document length shouldn't wildly shift semantic meaning.

## Interview Questions
- **Q: Why are "cat" and "dog" close together in embedding space?**
  - *A:* Because embedding models learn representations based on the distributional hypothesis: words that occur in similar contexts tend to have similar meanings. Both appear near words like "pet", "feed", and "vet" in the training data.
- **Q: What is the difference between the embeddings used inside an LLM and the embeddings used in a Vector Database?**
  - *A:* Internal LLM embeddings map individual tokens to vectors for the purpose of next-token prediction. Vector Database embeddings use specialized models to map entire chunks of text into a single vector optimized for semantic similarity and retrieval.

## Further Reading
- [Word2Vec Paper](https://arxiv.org/abs/1301.3781) - The foundational paper on word embeddings.
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) - The Massive Text Embedding Benchmark, used to choose embedding models for RAG.

---
<!-- nav:start -->
[Previous: Tokenization](02-tokenization.md) | [Module Overview](README.md) | [Next: Positional Encoding](04-positional-encoding.md)
<!-- nav:end -->
