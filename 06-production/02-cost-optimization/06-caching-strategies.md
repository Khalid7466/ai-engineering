# Caching Strategies

## TL;DR
Caching in LLM systems prevents the application from making redundant, expensive API calls or wasting GPU cycles on queries it has already processed. Due to the infinite variability of natural language, traditional exact-match caching is insufficient. Production AI systems require a multi-layered approach involving Exact Match Caching, Semantic Caching, and Prefix (Prompt) Caching to maximize cost savings and minimize latency.

---

## 1. Exact Match Caching (Standard IT Caching)

The simplest form of caching. If the exact same string is passed to the system, it returns the stored result. 
- **Implementation:** Redis or Memcached using a hash of the prompt as the key.
- **Pros:** Zero compute required, microsecond latency.
- **Cons:** Extremely low hit rate in LLM applications. "What is your return policy?" and "what's the return policy?" hash to different keys, rendering exact match useless for end-user chat interfaces.
- **Best For:** Automated batch processes, CI/CD evaluations, or tightly constrained UI drop-downs where user input is perfectly uniform.

## 2. Semantic Caching (The AI Standard)

Semantic caching uses embeddings to determine if a new query has the same *meaning* as a previously answered query, even if the phrasing is different.

1. **User asks:** "How do I reset my password?"
2. **System action:** Embeds the query. Checks a fast Vector DB (like RedisVL or Qdrant) for a semantic match within a strict distance threshold (e.g., > 0.95 cosine similarity).
3. **If Miss:** The query goes to the LLM. The LLM generates the answer. The system stores the embedding of the query and the LLM's text response in the cache.
4. **User 2 asks:** "I forgot my password, help me reset it."
5. **System action:** Embeds the query. The vector similarity to the first query is 0.98. The system returns the cached answer instantly. No LLM generation occurs.

**Pros:** Massive cost savings on high-volume, repetitive queries (like Tier-1 customer support). Near-instant latency.
**Cons:** Risk of "False Positives" (returning a cached answer that is slightly wrong for the specific nuance of the new query).

## 3. Prefix Caching (Prompt Caching)

While Semantic Caching caches the *output*, Prefix Caching caches the *input state* (specifically the KV Cache) within the inference engine itself.

In many applications, the system prompt and the few-shot examples are massive (e.g., 5,000 tokens of instructions) and are identical for every single user. 
Without Prefix Caching, the GPU must recompute the attention matrices for those 5,000 tokens on *every request*. 

**How it works:**
Modern serving engines (like vLLM) or APIs (like Anthropic's Prompt Caching) allow you to cache the pre-computed KV tensors of a shared prefix. 
When a new request arrives, the engine loads the cached state of the system prompt directly into VRAM, and only computes the few tokens of the specific user's query.

**Pros:** Drastically reduces Time To First Token (TTFT) and input token costs. 
**Best For:** Long system prompts, multi-turn chat histories, and agents that repeatedly use the same massive context (like reading an entire codebase).

## Production Implications

Implementing caching requires careful lifecycle management. 
If an LLM relies on a tool to fetch dynamic data (e.g., `get_stock_price`), **you cannot semantic cache the final output**, because the answer changes every minute even if the semantic query is identical. 

In production, Semantic Caching is typically applied *before* tool execution (to answer static FAQs) or *to the tool results themselves*, with aggressive Time-To-Live (TTL) expirations.

## Common Mistakes

- **Caching dynamic or personalized data:** Semantic caching a response that says "Your account balance is $500" and accidentally serving it to a different user who asked the same question. Caches must be partitioned by `user_id` or restricted to generic intents.
- **Setting the semantic similarity threshold too low:** A threshold of 0.85 might treat "How do I start the server?" and "How do I stop the server?" as a match, returning the wrong instructions.
- **Not implementing TTL (Time To Live):** Storing cached answers indefinitely. If the underlying company policy changes, the bot will continue serving the old, cached policy until the cache is manually invalidated.

## Interview Questions

**Q: Explain the difference between Exact Match Caching and Semantic Caching.**
**A:** Exact match requires the input string to be character-for-character identical to a previous request. It has a low hit rate for human inputs. Semantic caching embeds the query and uses vector similarity to find inputs that mean the same thing, even if phrased differently, vastly increasing the cache hit rate for end-user applications.

**Q: What is Prefix Caching and what specific metric does it optimize?**
**A:** Prefix caching involves saving the computed internal state (the KV cache) of the early, shared portions of a prompt—usually the long system instructions or retrieved documents. It optimizes Time To First Token (TTFT) and reduces compute costs, because the GPU does not need to re-evaluate those identical thousands of tokens for every new request.

## Further Reading
- [GPTCache](https://github.com/zilliztech/GPTCache) — A popular open-source library for implementing semantic caching.
- [Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) — How API providers implement prefix caching.
