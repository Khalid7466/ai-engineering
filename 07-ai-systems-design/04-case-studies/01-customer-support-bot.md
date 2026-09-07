<Use Case: Enterprise Customer Support Bot>
## Objective
An e-commerce company wants to replace their rules-based chatbot with an AI assistant. The bot must answer customer queries about shipping, returns, and product specs using a knowledge base of 500 FAQ documents and the user's specific order history. 

**Constraints:**
- Latency MUST be under 2 seconds (user abandonment skyrockets after 2s).
- Hallucinations regarding return policies are unacceptable (causes financial loss).
- Costs must remain under $0.01 per query.

## Why Standard RAG?
The team initially considered an Autonomous Agent that could query the knowledge base and the order database dynamically.
- **Why it failed:** An agentic loop (Thought -> Tool -> Observe -> Answer) takes 5-8 seconds. It also requires a more expensive model (GPT-4o) to reason about tool use, breaking the cost constraint.
- **The Pivot:** The execution path here is highly predictable. We know exactly what context is needed: the policy documents and the user's order state. We can use a **Standard RAG Pipeline** with deterministic API injection.

## Technical Decisions

### Decision 1: Model Selection
- **Chose:** Claude 3.5 Haiku (or Llama 3 8B).
- **Rejected:** GPT-4o / Claude 3.5 Sonnet.
- **Rationale:** We need sub-second generation time and extreme cost efficiency. Because the RAG pipeline will provide perfect context, we don't need the massive reasoning capabilities of frontier models. We just need a fast summarizer.

### Decision 2: Context Injection (Order Data)
- **Chose:** Upfront deterministic API fetch.
- **Rejected:** Giving the LLM a `check_order_status` tool.
- **Rationale:** Tools add latency. We already know who the user is when they open the chat. We can fetch their last 3 orders from the database using standard Python *before* the LLM is even invoked, and inject that JSON directly into the prompt.

### Decision 3: Retrieval Strategy
- **Chose:** Hybrid Search (Dense Vector + BM25 Keyword) with strict metadata filtering.
- **Rejected:** Cross-Encoder Re-ranking.
- **Rationale:** While re-ranking improves precision, it adds ~500ms of latency. To meet the 2s SLA, we rely on Hybrid Search and aggressively filter by category (e.g., only search "Shipping" docs if the intent classifier flags the query as shipping).

## Architecture Walkthrough

```python
# The Fixed Pipeline Architecture
async def handle_support_query(user_id: str, query: str) -> str:
    
    # STEP 1: Fast Intent Classification & Caching (Parallel)
    # Check Semantic Cache (RedisVL) to see if this exact question was asked recently
    cached_response = check_cache(query)
    if cached_response:
        return cached_response # Latency: 50ms

    # STEP 2: Deterministic Context Gathering
    # Fetch order data BEFORE invoking LLM
    order_data = db.get_recent_orders(user_id) 
    
    # STEP 3: Retrieval (Standard RAG)
    # Embed query and search vector DB
    relevant_faqs = vector_db.hybrid_search(
        query=query, 
        top_k=3
    )
    
    # STEP 4: Guardrail Evaluation (Deterministic)
    if not relevant_faqs and not order_data:
        return "I couldn't find information on that. Let me connect you to a human."
        
    # STEP 5: Generation
    prompt = build_prompt(query, order_data, relevant_faqs)
    
    # Stream response back to UI to improve perceived latency
    response_stream = fast_llm.stream(prompt)
    return response_stream
```

## Lessons Learned

1. **The Cache is King:** In customer support, 60% of questions are identical ("Where is my order?"). Implementing a Semantic Cache in front of the LLM pipeline absorbed the majority of traffic, driving average latency down to 200ms and slashing API costs.
2. **Metadata Filtering beats better Embeddings:** The vector search kept retrieving "International Shipping" policies for domestic users. Instead of upgrading the embedding model, we added user location as a metadata filter to the vector query, instantly solving the precision issue with zero latency penalty.
3. **Escalation > Hallucination:** By implementing a strict similarity threshold on the vector search (if top score < 0.75, abort), we prevented the fast, smaller LLM from trying to guess answers. Falling back to a human is always better than confidently lying about a refund policy.
</Use Case: Enterprise Customer Support Bot>
