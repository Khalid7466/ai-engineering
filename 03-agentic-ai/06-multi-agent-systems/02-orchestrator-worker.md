# Orchestrator-Worker Pattern

## TL;DR
The Orchestrator-Worker pattern is the most robust multi-agent architecture for production. An orchestrator LLM decomposes the user's intent into a plan, delegates execution to specialized worker LLMs (or deterministic scripts), aggregates the results, and handles worker failures gracefully.

---

## How It Works

### 1. Decomposition
The Orchestrator agent acts as the system's entry point. Its only job is routing and planning. It does *not* execute business logic tools.
- **User:** "Give me a summary of Q3 sales and cross-reference with client complaints."
- **Orchestrator Thought:** I need to use the `SalesAgent` to get Q3 data, and the `SupportAgent` to get complaint data.

### 2. Delegation
The Orchestrator formats a specific sub-prompt for the first worker.
- **Orchestrator -> SalesAgent:** "Find total Q3 sales grouped by region."
- The `SalesAgent` runs its own ReAct loop using SQL tools, completes the task, and returns a JSON summary back to the Orchestrator.

### 3. Aggregation
The Orchestrator waits for the workers to return (often running them in parallel if they are independent). It takes the JSON from `SalesAgent` and the JSON from `SupportAgent`, synthesizes them into a final narrative, and returns it to the user.

## Failure Handling
The Orchestrator is responsible for error recovery. 
If the `SupportAgent` returns: `Error: Could not access Jira API`, the Orchestrator must decide:
- Do I retry the `SupportAgent` with different instructions?
- Do I fallback to a different system?
- Do I return a partial answer to the user? ("I found the sales data, but couldn't access complaints.")

## Production Implications
The interface between the Orchestrator and the Workers should be strictly typed (e.g., Pydantic models). If a Worker returns free-form text, the Orchestrator has to spend tokens parsing it. If the Worker returns structured JSON, the Orchestrator can easily aggregate it. 
Furthermore, Workers don't necessarily need to be LLMs. A worker can be a deterministic Python script. The Orchestrator doesn't care, as long as it adheres to the contract.

## Common Mistakes
- **Leaking Tools to the Orchestrator:** Giving the Orchestrator direct access to the SQL database tool. The Orchestrator should only have tools like `delegate_to_sales` or `delegate_to_support`.
- **Sequential Bottlenecks:** Forcing the Orchestrator to wait for `Worker A` to finish before starting `Worker B` when their tasks are completely independent.

## Interview Questions
- **Q: In an Orchestrator-Worker architecture, should the Orchestrator agent have direct access to database execution tools?**
  - A: No. The Orchestrator's role is planning and delegation. Direct tool execution should be handled by specialized Worker agents to maintain separation of concerns and prevent the Orchestrator's prompt from becoming overly complex.
- **Q: How does the Orchestrator handle a Worker failure?**
  - A: The Orchestrator receives the error as an observation. It can then reason whether to retry the delegation with modified instructions, delegate to a fallback worker, or return a partial result to the user.

## Further Reading
- [LangGraph: Multi-Agent Workflows](https://langchain-ai.github.io/langgraph/) — Documentation on building orchestrator patterns using graph state machines.
