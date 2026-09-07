# Semantic Search at Query Time

## TL;DR
Semantic search is the process of executing the transformed query against the vector database. It involves calculating similarity, setting dynamic thresholds, and retrieving the top-K chunks. Understanding how to filter and bound these results is critical to preventing irrelevant context from poisoning the LLM.

---

## The Search Execution

Once the user's query is embedded into a dense vector, the system queries the vector database using the Approximate Nearest Neighbor (ANN) index (like HNSW).

### Top-K Selection
- **Definition:** `K` is the number of results to return. 
- **The Tradeoff:** If `K` is too low (e.g., K=2), you might miss the critical document. If `K` is too high (e.g., K=20), you bloat the context window, increase latency/cost, and risk the LLM getting confused by irrelevant "distractor" chunks.

### Similarity Score Thresholds
Vector databases will always return `K` results, even if the documents are completely irrelevant to the query. They just return the *closest* vectors, even if the closest vector is still very far away.
- **Implementation:** Set a similarity threshold (e.g., Cosine Similarity > 0.75). If the top results fall below this threshold, the system should intercept and return "I don't have enough information to answer that," rather than passing garbage to the LLM.

## Pre-Filtering vs Post-Filtering

When combining metadata filters (e.g., `department = 'HR'`) with semantic search:
- **Pre-filtering:** The database filters down to only HR documents first, then runs the vector search. (Preferred, guarantees K results, but can be slow if the filter yields a very small subset and the index isn't optimized).
- **Post-filtering:** The database runs a vector search for the top 100 results, then removes those that aren't in the HR department. (Dangerous: if only 2 of the top 100 are HR, you return K=2 instead of K=10, degrading quality).

## Production Implications
Never blindly trust the Top-1 result. Semantic similarity does not equal factual relevance. The vector representing "User login failed" is almost identical to "User login succeeded". If the system relies purely on similarity without thresholds, it will confidently hallucinate using the wrong context.

## Common Mistakes
- **No Thresholds:** Passing retrieved chunks to the LLM even when the similarity score is extremely low.
- **Static K Values:** Always returning exactly 5 documents, regardless of whether 1 or 10 documents are actually highly relevant.

## Interview Questions
- **Q: Why will a vector database always return results, even if the user asks a completely irrelevant question?**
  - *Answer:* Vector databases perform nearest-neighbor searches. There is always a "nearest" vector in the geometric space, even if the absolute distance is large. Without setting a similarity threshold, the system will return the least irrelevant chunks and treat them as fact.

## Further Reading
- [Nearest Neighbor Search (Wikipedia)](https://en.wikipedia.org/wiki/Nearest_neighbor_search)
