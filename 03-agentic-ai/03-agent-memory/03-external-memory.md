# External Memory and Vector DBs

## TL;DR
External memory allows agents to persist information across sessions and scale beyond their context window limits. By storing episodic logs in vector databases and semantic facts in structured stores, agents can retrieve relevant context dynamically at query time using RAG techniques.

---

## Vector DB for Long-Term Episodic Memory
To give an agent a memory of past interactions, you cannot inject every past chat into the prompt. Instead, you chunk past conversations, embed them, and store them in a Vector Database (like Pinecone, Milvus, or pgvector).

**Retrieval at Query Time:**
When the user asks, "Can you run that report we did last Tuesday?", the orchestration layer:
1. Embeds the user query.
2. Performs a similarity search against the Vector DB.
3. Retrieves the top-K relevant past conversation snippets.
4. Injects them into the current Working Memory (context window).

## Semantic Memory Management (e.g., Mem0)
Vector DBs are great for finding *similar* text, but poor at resolving *facts*. If the user says "I live in New York," and later says "I moved to London," a vector search might return both, confusing the agent.

Frameworks like Mem0 or Zep manage semantic memory. They use LLMs asynchronously to extract, update, and delete facts from a structured knowledge graph or JSON document based on the conversation stream. 

## Memory Write vs. Read Operations
Memory is not just for reading. An autonomous agent must be able to *write* to its own memory.
- **Implicit Writing:** The orchestration layer automatically embeds and saves every user-agent turn into the Vector DB.
- **Explicit Writing (Tool-based):** The agent is provided with `save_memory(key, value)` and `search_memory(query)` tools. The agent actively decides when a fact is important enough to save for the future.

## Production Implications
Relying heavily on external memory introduces significant latency. If every agent step requires a vector search to fetch context, the loop slows down. Furthermore, bad memory management creates "poisoned context." If the agent hallucinates a fact and writes it to semantic memory, it will treat that hallucination as absolute truth in all future sessions. You need tools for users to view and edit the agent's memory.

## Common Mistakes
- **Over-retrieving:** Pulling in too many past memories, which dilutes the current context and confuses the agent.
- **No Conflict Resolution:** Storing conflicting episodic memories without a semantic layer to determine which fact is currently true.
- **Synchronous Writes:** Blocking the agent's response to the user while waiting for the LLM to extract facts and write to the vector DB. (Writes should be asynchronous).

## Interview Questions
- **Q: Why use a dedicated semantic memory manager instead of just a raw vector database for agent memory?**
  - A: Vector databases only do similarity matching and cannot resolve conflicts or update outdated facts (e.g., a user changing their address). Semantic memory managers actively update a single source of truth based on new information.
- **Q: What is the difference between implicit and explicit memory writing in agents?**
  - A: Implicit writing happens automatically in the background by the orchestrator (saving all chat logs). Explicit writing is when the agent itself decides to call a `save_memory` tool to store a specific fact.

## Further Reading
- [Mem0 Documentation](https://github.com/mem0ai/mem0) — The memory layer for personalized AI.
