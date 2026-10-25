# Embedding in Production

## TL;DR
Deploying embedding models in production involves managing throughput for batch ingestion, optimizing vector dimensions for storage costs, and implementing caching layers to reduce latency and API usage.

---

## Batch Ingestion at Scale

When indexing millions of documents, calling an embedding API synchronously one-by-one is unacceptably slow.
- **Batching:** Send requests in batches (for example, OpenAI allows up to 2048 inputs per API call) to maximize throughput.
- **Concurrency & Rate Limiting:** Implement robust retry logic with exponential backoff. Cloud APIs (like OpenAI) enforce strict tokens-per-minute (TPM) limits. You must orchestrate ingestion workers to stay just below these limits to prevent `429 Too Many Requests` errors.

## Dimensionality Reduction and Matryoshka Embeddings

High-dimensional vectors (e.g., 3072 dimensions) are highly accurate but incredibly expensive to store and slow to search in memory.
- **Shortenable embeddings:** OpenAI's `text-embedding-3` models are trained with a technique that lets you shorten the vectors without losing most of their quality. This idea is commonly called Matryoshka representation learning.
- **Truncation:** You can shorten a 3072-dimensional vector to 256 dimensions by keeping the first 256 values and then re-normalizing the result to length 1 (L2 normalization). Without re-normalizing, the vector is no longer unit length, so dot-product and cosine scores will differ. This cuts storage and memory by 12x at the cost of some accuracy. OpenAI's `text-embedding-3` models also accept a `dimensions` API parameter that does the shortening for you.

## Caching Strategies

Re-embedding unchanged text with the same model is wasted cost, so key your cache on a hash of the text plus the model name and version.
- **Ingestion Caching:** Hash the raw text chunk. Before sending it to the API, check if the hash exists in your cache. This prevents re-embedding the entire knowledge base if you tweak your vector DB schema.
- **Query Caching:** Cache the exact user queries. If a user asks the same question twice, bypass the embedding API and vector search entirely.

## Production Implications
Vector databases hold indices in RAM for fast search. Storing 1 billion 1,536-dimensional float32 vectors takes about 6.1 TB before index overhead, and the same vectors at 256 dimensions take about 1.0 TB. Reducing dimensions before indexing can lower infrastructure cost substantially, but verify the retrieval quality on your own data.

## Common Mistakes
- **No Rate Limiting:** Crashing ingestion pipelines against API rate limits.
- **Overpaying for Storage:** Using maximum-dimension vectors by default. Shorter embeddings are often good enough: OpenAI reports that a `text-embedding-3-large` embedding shortened to 256 dimensions still outperforms the older, unshortened 1,536-dimension `text-embedding-ada-002` on MTEB. Always measure retrieval quality on your own queries before shrinking.

## Interview Questions
- **Q: What are Matryoshka embeddings and how do they save costs?**
  - *Answer:* They are embeddings trained to store the most critical semantic information in the earliest dimensions. This allows engineers to truncate the vectors (e.g., from 1536 to 256 dimensions) while retaining most of the accuracy, drastically reducing the memory required by the vector database.

## Further Reading
- [Matryoshka Representation Learning](https://arxiv.org/abs/2205.13147) — The research behind variable-dimension embeddings.
