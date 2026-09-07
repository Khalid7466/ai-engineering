# Semantic Caching

## TL;DR
Semantic caching stores the results of previous LLM generations based on the semantic meaning of the user query, rather than an exact string match. It drastically reduces API costs, cuts latency to milliseconds, and scales RAG systems for high traffic.

---

## The Inefficiency of Exact Caching

Traditional caching (e.g., Redis) uses exact string matching. 
If User A asks: *"How do I reset my password?"* and User B asks *"How can I change my password?"*, an exact-match cache treats these as a cache miss, triggering the entire RAG pipeline (embedding, vector search, LLM generation) twice for the exact same intent.

## How Semantic Caching Works

Semantic caching uses a fast vector database layer in front of the main RAG pipeline.
1. User asks a question.
2. The question is embedded.
3. The system searches the Semantic Cache (a vector DB containing previous questions and their LLM answers).
4. If a stored question is semantically identical (e.g., Cosine Similarity > 0.95), the system returns the cached answer instantly.
5. If no match is found, the system runs the full RAG pipeline, then stores the new question and answer in the cache.

## Popular Implementations

- **GPTCache:** An open-source library specifically designed for LLM caching.
- **Redis + Vector Similarity:** Using Redis Enterprise or Redis Stack to store strings with HNSW indices for rapid semantic lookup.

## Cache Invalidation Challenges

In traditional software, you invalidate the cache when the underlying data changes. In RAG, this is harder.
If the underlying document outlining the password reset policy is updated, the semantic cache still holds the old LLM answer.
- **TTL (Time to Live):** The simplest solution. Expire cached answers after 24 hours.
- **Dependency Tracking:** Complex systems map cached answers back to the specific chunk IDs they were generated from. If a chunk is updated, all cached answers citing that chunk are invalidated.

## Production Implications
LLM generation is the slowest and most expensive part of RAG. In customer support chatbots, the Pareto principle applies: 80% of users ask the same 20% of questions. Semantic caching intercepts these repetitive queries, reducing cloud compute costs by massive margins and delivering instant responses to end users.

## Common Mistakes
- **Threshold Too Low:** Setting the similarity threshold to 0.85, causing the cache to return answers to vaguely related but factually different questions.
- **Caching Personalized Data:** Accidentally caching an answer that includes User A's specific account details, and serving it to User B because their questions were semantically similar.

## Interview Questions
- **Q: What is the risk of using semantic caching in a highly dynamic RAG environment?**
  - *Answer:* Serving stale data. If the underlying knowledge base changes, the semantic cache will continue to serve outdated generated answers until the cache expires or is explicitly invalidated. 

## Further Reading
- [GPTCache Repository](https://github.com/zilliztech/GPTCache) — A library for creating semantic caches for LLMs.
