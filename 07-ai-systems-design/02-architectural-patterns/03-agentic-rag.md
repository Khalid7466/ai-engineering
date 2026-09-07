## TL;DR
Agentic RAG transitions retrieval from a fixed pipeline to a dynamic execution path. Instead of doing a single semantic search, the LLM is given tools to search, filter, and read documents, deciding for itself when it has enough information to answer the user's query. This pattern is necessary when queries require multi-hop reasoning or synthesis across disparate documents.

---

## When Standard RAG Breaks

Standard RAG assumes the answer exists neatly in one or two chunks that can be found with a single query. It completely fails on **Multi-hop Queries**.

*Example Query:* "What is the difference in revenue growth between the company acquired in Q2 and our main competitor?"

To answer this, the system must:
1. Find out which company was acquired in Q2. (Query 1)
2. Look up the revenue growth for that acquired company. (Query 2)
3. Look up our main competitor. (Query 3)
4. Look up the revenue growth for the competitor. (Query 4)
5. Compare them.

A Standard RAG vector search will fail completely; it might retrieve chunks containing the words "revenue growth" and "competitor," but it cannot execute this logical sequence. 

## The Agentic RAG Architecture

In Agentic RAG, the LLM is an agent equipped with retrieval tools.

### Core Tools Provided to the Agent:
- `search_knowledge_base(query: str, filter_metadata: dict)`: Performs semantic search.
- `read_document(doc_id: str, section: str)`: Pulls exact text, avoiding vector chunking issues.
- `execute_sql(query: str)`: For structured data (because vector DBs are bad at math/aggregation).

### The Execution Loop:
1. **Plan:** The LLM receives the user query and plans the necessary searches.
2. **Execute:** The LLM calls a search tool.
3. **Observe:** The LLM reads the retrieved chunks.
4. **Evaluate:** The LLM asks itself: "Do I have enough information to answer the original question?"
5. **Iterate:** If no, formulate a new search query based on what was just learned. If yes, generate the final answer.

## Production Implications

### The Infinite Loop Problem
Because the execution path is dynamic, an Agentic RAG system can get stuck. If a search tool returns no results, a poorly prompted agent might just keep trying variations of the same search query infinitely, burning tokens and timing out the user request.
**The Fix:** 
1. Implement a hard limit on tool calls (e.g., `max_iterations=5`).
2. Give the agent a "give up" escape hatch in its system prompt: *"If you cannot find the answer after 3 distinct searches, use the `escalate_to_human` tool."*

### Latency and Cost Explosions
Standard RAG takes 1 LLM call (plus an embedding call). Agentic RAG might take 5-10 LLM calls before returning an answer. This means latency goes from 1.5 seconds to 15+ seconds, and costs increase by 10x.
**The Fix:** Agentic RAG should **never** be your default. You should use an upfront Router (a fast, cheap model) to classify the complexity of the query.
- Simple factual query → Route to Standard RAG.
- Complex/Comparative query → Route to Agentic RAG.

## Common Mistakes
- **Failing to expose metadata to the agent:** If your agent can only do semantic search, it will fail at queries like "Show me documents from 2023." You must give the agent a tool that accepts explicit metadata filters (e.g., `search(query="sales", year="2023")`).
- **Using a weak LLM as the planner:** Planning and query formulation require high reasoning capabilities. While you might use an 8B model for standard RAG generation, Agentic RAG routing and planning usually requires frontier models (GPT-4o, Claude 3.5 Sonnet) to avoid getting stuck in stupid loops.

## Interview Questions
- **Q: How does Agentic RAG handle a query like "Summarize the key themes of all 1,000 customer interviews"?**
  - *Answer:* Trick question. Neither Standard nor Agentic RAG is good at this. Agentic RAG relies on search tools, which pull subsets of data. For global summarization over a massive corpus, you need Map-Reduce pipelines or GraphRAG, not a standard search agent. 
- **Q: Your Agentic RAG system is successfully answering multi-hop questions, but users are complaining it takes 20 seconds. How do you optimize?**
  - *Answer:* First, implement a query router to ensure simple questions bypass the agent and go to a standard RAG pipeline. Second, for the agent itself, stream the *intermediate thoughts* (tool calls) to the UI so the user sees the system working ("Searching for Q2 acquisitions...", "Reading Q2 report..."). This dramatically improves perceived latency.

## Further Reading
- [LangGraph Documentation on Agentic RAG](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_adaptive_rag/) — Excellent patterns for adaptive and agentic retrieval.
