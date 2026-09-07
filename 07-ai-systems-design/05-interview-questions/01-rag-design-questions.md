## TL;DR
This file contains five common AI Engineering interview questions focused on RAG (Retrieval-Augmented Generation) system design, complete with model answers that demonstrate production-level architectural thinking.

---

## Question 1: Scale and Architecture
**"Design a RAG system for a 10-million document legal corpus. How do you ensure low latency and high relevance?"**

**Model Answer:**
A 10M document corpus (approx. 50-100M chunks) cannot rely on naive vector search. 
1. **Data Layer (Context Engineering):** I would implement structural chunking (by clause/section) rather than naive token chunking, and tag every chunk with rich metadata (document type, date, jurisdiction, entities).
2. **Retrieval Layer:** Standard dense vector search will return too many false positives at this scale. I would use a Hybrid Search approach: BM25 (keyword search) to find exact legal terms + Dense Vector Search for semantic meaning. 
3. **Routing/Filtering:** Before searching, a fast LLM router extracts metadata from the user's query ("Show me 2023 contracts in NY") and applies hard pre-filters to the vector database. This reduces the search space from 10M to maybe 50k documents instantly.
4. **Re-ranking:** I would retrieve the top 100 chunks and pass them through a Cross-Encoder Re-ranker to surface the absolute best 5 chunks.
5. **Generation:** Pass those top 5 chunks into the generation model. 

## Question 2: Multilingual Support
**"How would you handle a multilingual RAG system where documents are in Spanish, but users query in English?"**

**Model Answer:**
There are two primary architectural patterns for this:
1. **Translate on Ingestion (Pipeline Approach):** As Spanish documents are uploaded, use a translation API to translate them to English. Embed and store both versions. This costs more upfront and increases storage, but retrieval is fast and accurate because everything happens in one language space.
2. **Multilingual Embeddings (Model Approach):** Use a multilingual embedding model (like Cohere multilingual). These models map "Hello" and "Hola" to the exact same vector space. The user queries in English, the system retrieves the Spanish chunks, and we instruct the generation LLM (which is natively multilingual) to answer in English using the Spanish context.
*Recommendation:* I prefer Pattern 2 for cost-efficiency, but if precision is paramount, Pattern 1 avoids nuances lost in multilingual embedding spaces.

## Question 3: Debugging Relevance
**"Your RAG system is returning irrelevant results. Walk me through your debugging process."**

**Model Answer:**
Relevance issues are almost always retrieval failures, not generation failures. I investigate sequentially:
1. **Look at the chunks:** I inspect the actual raw text being passed to the LLM. If the chunks are garbage, the generation will be garbage.
2. **Check the Chunking Strategy:** Are the chunks too small? If a chunk just says "Therefore, it is approved," it has no semantic meaning. I would increase chunk size or implement overlap.
3. **Check the Embedding Model:** Is the embedding model domain-specific? If it's a general OpenAI model being used on highly technical medical data, it might fail. I'd evaluate fine-tuning the embedding model or switching to a domain-specific one.
4. **Check the Search Type:** Are users asking for specific IDs (e.g., "Invoice 4928A")? Vector search is terrible at exact string matching. I would need to add a BM25 hybrid search layer to catch exact keywords.

## Question 4: GraphRAG vs Standard RAG
**"When would you choose GraphRAG over Standard RAG?"**

**Model Answer:**
Standard RAG excels at "needle in a haystack" queries (e.g., "What is the capital of France?"). 
GraphRAG (Knowledge Graphs) is required for "connecting the dots" or global aggregation queries.
I would choose GraphRAG if the use case requires multi-hop entity relationships. For example, investigating financial fraud: "Who is the CEO of the company that acquired the startup founded by John Doe?" 
Standard RAG will fail because the relationship isn't explicitly stated in one chunk. GraphRAG extracts entities (John Doe, Startup, Acquirer, CEO) and their relationships into a graph database during ingestion, allowing the system to traverse the graph to answer complex relational queries.

## Question 5: Handling Scale and Latency
**"How does a RAG system scale to 1 million daily active users while maintaining sub-2-second latency?"**

**Model Answer:**
At that scale, LLM API costs and latency are the primary constraints.
1. **Semantic Caching:** I would implement a semantic cache (like RedisVL) in front of the LLM. If User B asks a question semantically identical (95% vector similarity) to a question User A asked 5 minutes ago, I serve the cached answer. This bypasses the LLM entirely, dropping latency to ~50ms and cost to zero for high-frequency queries.
2. **Tiered Routing:** Not all queries need GPT-4o. A fast intent classifier routes simple queries to a smaller, self-hosted model (Llama 3 8B) which generates responses in <1s. Only complex reasoning queries are routed to the expensive frontier models.
3. **Vector DB Scaling:** Ensure the vector database is distributed (e.g., Milvus, Qdrant cluster) with read replicas to handle the high QPS (Queries Per Second) of the retrieval step.
4. **Streaming:** Always stream the response back to the client so the Time To First Token (TTFT) feels instantaneous to the user, even if the full generation takes 2 seconds.
