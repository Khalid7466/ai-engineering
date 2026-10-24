# Embeddings

## TL;DR
Embeddings are dense vector representations of text where semantic meaning is mapped to geometric space. They are the fundamental way language models translate discrete tokens into continuous numbers that neural networks can process. Words with similar meanings are located close to each other in this multidimensional space.

---

## Vector Space Geometry
When a token is passed into an LLM, the first step is an embedding lookup. A token like "king" is converted into a list of floating-point numbers (the length depends on the model, typically hundreds to a few thousand dimensions).

This first step is a **lookup table**: each token ID maps to one learned vector (see section 3.4 of [Attention Is All You Need](https://arxiv.org/abs/1706.03762)). The same token therefore gets the same vector regardless of the surrounding words. Context is added later by self-attention (see [06-self-attention.md](06-self-attention.md)), and word order is added separately (see [04-positional-encoding.md](04-positional-encoding.md)). The token IDs come from [02-tokenization.md](02-tokenization.md).

This vector represents the concept's location in a high-dimensional space. A well-known property of learned embeddings is that geometric relationships tend to reflect semantic relationships.

- **Similarity:** The vector for "cat" will have a high cosine similarity (it points in the same direction) to the vector for "dog" because they appear in similar contexts (pets, animals, feeding).
- **Relational Math (word2vec):** The classic example comes from static word2vec vectors (Mikolov et al., 2013): `Vector("King") - Vector("Man") + Vector("Woman")` lands closest to `Vector("Queen")`. Treat it as an illustration, not a law. The standard evaluation excludes the input words from the possible answers (Nissim et al., 2020), and the result was shown for static word vectors, not for the internals of LLMs.

## Internal LLM Embeddings vs. External RAG Embeddings
It is critical to distinguish between two ways the term "embeddings" is used in AI Engineering:

1. **Internal LLM Embeddings:** The very first layer of a model like Llama 3. It maps token IDs to vectors *before* they pass through the Transformer blocks. You generally do not interact with these directly when using APIs.
2. **External Embeddings (for RAG):** Specialized models (like `text-embedding-3-small` or BGE-M3) trained explicitly to map entire sentences or paragraphs into a single vector. We use these to index documents in a Vector Database for Retrieval-Augmented Generation (RAG) (see [01-embedding-fundamentals.md](../02-rag/03-embedding-models/01-embedding-fundamentals.md)).

While they use the same underlying concept, an LLM's internal token embeddings are optimized for predicting the next token, whereas external embedding models are optimized for semantic search (making a query vector close to the relevant document vector).

## Production Implications
- **Dimensionality Trade-off:** Storage and search cost grow with the number of dimensions. A float32 vector with 1,536 dimensions takes 6,144 bytes, so one million of them take about 6.1 GB, versus about 12.3 GB at 3,072 dimensions. Some APIs let you shorten embeddings: OpenAI's `text-embedding-3` models accept a `dimensions` parameter (default 1,536 for `text-embedding-3-small` and 3,072 for `text-embedding-3-large`), and OpenAI's documentation reports that a `text-embedding-3-large` embedding shortened to 256 dimensions still outperforms the older, unshortened `text-embedding-ada-002` on MTEB. (The strict meaning of "curse of dimensionality" is different: distances become less discriminative as dimensions grow, see Beyer et al., 1999.)
- **Out-of-Domain Jargon:** Subword tokenizers (see [02-tokenization.md](02-tokenization.md)) can represent any input, so the problem is not a missing word but poor coverage. Specialized jargon (internal acronyms, novel medical terms) is split into many small pieces the model rarely saw, and the resulting vectors represent it poorly, which leads to bad search results in RAG. Always evaluate on your own queries.
- **Asymmetric Search:** In production RAG, queries are short ("how do I reset password") and documents are long. Many retrieval models are trained for this and expect different inputs for the two sides. For example, E5 models expect a `query: ` prefix on queries and a `passage: ` prefix on documents, and BGE models expect an instruction prefix on queries only. Omitting a required prefix can noticeably reduce retrieval quality, so always check the model card.

## Common Mistakes
- **Confusing the two types of embeddings:** Thinking you can extract the first layer of GPT-4 and use it for a vector database. You need a dedicated embedding model for search.
- **Ignoring input limits and chunking:** Embedding models have a maximum input length (for example 8,192 tokens for OpenAI's `text-embedding-3` models; some open models accept far fewer), and embedding a whole 50-page PDF into one vector also dilutes its meaning. Chunk text before embedding. A few hundred tokens is a common starting point, so tune it per use case (see [03-chunking-strategies.md](../02-rag/02-data-ingestion/03-chunking-strategies.md)).
- **Mismatching the similarity metric:** Use the metric the model was trained for. For normalized embeddings (OpenAI's embeddings are normalized to length 1), cosine similarity, dot product and Euclidean distance give the same ranking, so the choice is mostly about speed. The real mistake is using dot product or Euclidean distance on *unnormalized* vectors, where vector length can skew the scores.

## Interview Questions
- **Q: Why are "cat" and "dog" close together in embedding space?**
  - *A:* Because embedding models learn representations based on the distributional hypothesis: words that occur in similar contexts tend to have similar meanings. Both appear near words like "pet", "feed", and "vet" in the training data.
- **Q: What is the difference between the embeddings used inside an LLM and the embeddings used in a Vector Database?**
  - *A:* Internal LLM embeddings map individual tokens to vectors for the purpose of next-token prediction. Vector Database embeddings use specialized models to map entire chunks of text into a single vector optimized for semantic similarity and retrieval.

## Further Reading
- [Word2Vec Paper](https://arxiv.org/abs/1301.3781) - The foundational paper on word embeddings.
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) - The Massive Text Embedding Benchmark, used to choose embedding models for RAG.
- [MTEB benchmark repository](https://github.com/embeddings-benchmark/mteb) - Code and tasks behind the benchmark.
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) - Section 3.4 describes the learned token embeddings.
- [Fair Is Better than Sensational: Man Is to Doctor as Woman Is to Doctor](https://aclanthology.org/2020.cl-2.7) - Why the king/queen analogy is less magical than it looks.

---
<!-- nav:start -->
[Previous: Tokenization](02-tokenization.md) | [Module Overview](README.md) | [Next: Positional Encoding](04-positional-encoding.md)
<!-- nav:end -->
