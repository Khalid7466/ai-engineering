# Hybrid Search

## TL;DR
Hybrid search combines the semantic understanding of dense vector embeddings with the exact keyword matching of sparse retrieval (like BM25). It bridges the gap where pure vector search fails: acronyms, unique identifiers, names, and highly specific industry jargon.

---

## The Two Retrieval Paradigms

### Dense Retrieval (Vector Search)
- **Mechanism:** Neural embeddings (e.g., `text-embedding-3`).
- **Strengths:** Understands concepts, synonyms, and context. (e.g., maps "automobile" to "car").
- **Weaknesses:** Terrible at exact string matching. Will struggle to distinguish between "Model X-412" and "Model Y-412" because the semantic meaning is identical.

### Sparse Retrieval (Keyword Search / BM25)
- **Mechanism:** TF-IDF variants like BM25 count the frequency of exact tokens in a document relative to the whole corpus.
- **Strengths:** Perfect for exact matches, names, error codes, and IDs.
- **Weaknesses:** No semantic understanding. Fails if the user queries "car" but the document uses "automobile".

## How Hybrid Search Works

Hybrid search executes both dense and sparse queries simultaneously, then merges and re-ranks the results.

### Reciprocal Rank Fusion (RRF)
Because dense scores (Cosine similarity: 0.0 to 1.0) and sparse scores (BM25: 0 to arbitrary high numbers) are mathematically incompatible, you cannot simply add them together.
RRF merges the lists based on *rank* rather than *score*. 
Formula: `RRF Score = 1 / (k + Rank)` 
(where `k` is a smoothing constant, usually 60).
If a document is ranked #1 in BM25 and #3 in Vector Search, it gets a high combined RRF score.

## Production Implications
Pure vector search is rarely sufficient for production enterprise applications. Users instinctively search using keywords (e.g., "Invoice #49281"). If your system only uses dense embeddings, it will fail to retrieve the exact invoice, destroying user trust. Hybrid search is mandatory for most real-world RAG systems.

## Common Mistakes
- **Normalizing Incompatible Scores:** Trying to manually normalize and add BM25 scores to Cosine scores instead of using rank-based fusion (RRF).
- **Ignoring Tokenization for Sparse Search:** Failing to configure the BM25 tokenizer for domain-specific jargon, ruining the keyword search aspect.

## Interview Questions
- **Q: Why is Reciprocal Rank Fusion (RRF) used in hybrid search?**
  - *Answer:* Dense vector scores and sparse BM25 scores are on completely different, non-comparable scales. RRF ignores the raw scores and instead assigns a new score based on the item's rank in both respective lists, allowing for safe and effective merging of the results.

## Further Reading
- [Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) — The foundational RRF paper.
