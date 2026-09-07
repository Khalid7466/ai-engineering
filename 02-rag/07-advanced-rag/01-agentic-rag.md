# Agentic RAG

## TL;DR
Standard RAG is a rigid, linear pipeline (Retrieve -> Generate). Agentic RAG gives the LLM autonomy (tool calling) to decide *whether* to retrieve, *what* to retrieve, and when to execute *multiple* retrieval hops to synthesize an answer. It solves complex, multi-part questions that break standard vector search.

---

## When Standard RAG Fails

Standard RAG fails on "Multi-hop" reasoning.
**Query:** "Did the company that acquired WhatsApp have higher revenue in 2023 than the company that acquired GitHub?"
A single vector search for this query will fail. The vector DB doesn't know who acquired WhatsApp or GitHub. 

## The Agentic Solution

In Agentic RAG, the LLM acts as an orchestrator with access to search tools.
1. **Planning:** The LLM decomposes the query: 
   - Step 1: Find who acquired WhatsApp.
   - Step 2: Find who acquired GitHub.
   - Step 3: Find 2023 revenue for Company A.
   - Step 4: Find 2023 revenue for Company B.
   - Step 5: Compare.
2. **Execution (Tool Calling):** The LLM issues discrete search queries to the vector DB (or SQL DB) iteratively, digesting the results of one search to formulate the next.

## Routing and Fallbacks

Agents can dynamically route queries to different data sources.
- If the query is "What is my vacation balance?", the agent routes to the HR SQL database via an API tool.
- If the query is "How do I setup the VPN?", the agent routes to the Vector DB containing IT wikis.

### CRAG (Corrective RAG)
An agentic pattern where an evaluator assesses the quality of the retrieved documents. If the vector DB returns poor results, the agent falls back to searching the public web (via a tool like Tavily or Bing) to fill the knowledge gap.

## Production Implications
Agentic RAG is vastly more powerful but much slower and harder to control. A standard RAG pipeline takes 1-2 seconds. An Agentic RAG workflow might require 5 sequential LLM calls, taking 15 seconds. It also introduces the risk of infinite loops if the agent fails to find the data and keeps re-searching.

## Common Mistakes
- **Using Weak Models for Agents:** Agentic tool-calling requires advanced reasoning capabilities. GPT-3.5 or small open-source models often get stuck in loops or format tool calls incorrectly.
- **No Timeout Constraints:** Letting an agent execute 20 sequential searches, blowing up API costs and leaving the user hanging.

## Interview Questions
- **Q: How does Agentic RAG handle a query that spans both unstructured PDF data and structured SQL data?**
  - *Answer:* The LLM is provided with multiple tools (e.g., `search_pdfs` and `query_database`). The agent analyzes the user's intent, calls the SQL tool to fetch structured data, calls the vector tool to fetch unstructured context, and synthesizes a final answer combining both sources.

## Further Reading
- [LangGraph](https://langchain-ai.github.io/langgraph/) — Framework for building stateful, multi-actor LLM agents.
