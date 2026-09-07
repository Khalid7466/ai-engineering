<Use Case: ERP Data Analyst Agent>
## Objective
An enterprise needed a system to allow business users to ask natural language questions about their ERP data (e.g., "Why did Q3 margins drop in EMEA?"). The system had to fetch data from various SQL tables, Salesforce, and internal APIs to formulate an answer.

## Why Agentic AI?
Initially, the team built a rigid pipeline: 6 hardcoded `if/else` chains using basic intent classification to route queries to specific SQL tools. It broke every time a user asked a multi-part question ("Get Q3 margins and compare them to Salesforce leads") or phrased things unexpectedly. The fixed pipeline was too fragile for ambiguous natural language. We needed a system that could dynamically plan data retrieval steps.

## Technical Decisions
### Decision 1: ReAct Pattern
- **Chose:** A ReAct (Reason-Act) agent loop.
- **Rejected:** Complex multi-agent orchestrator.
- **Rationale:** The problem required dynamic routing between 5-6 well-defined tools, but the task itself was singular (data analysis). A single agent with a ReAct loop was sufficient and easier to debug than a multi-agent swarm.

### Decision 2: Structured Output as Plan (`QueryPlanContract`)
- **Chose:** Pydantic schemas to enforce structured output for the agent's plan and tool calls.
- **Rejected:** Unstructured text parsing (regex) for tool calls.
- **Rationale:** LLMs hallucinate tool names and parameters if left unchecked. By enforcing a strict `QueryPlanContract` via JSON schema/function calling, we guaranteed the agent's output matched the expected tool signatures, eliminating syntax errors.

## Architecture Walkthrough
1. **User Query:** "Why did Q3 margins drop in EMEA?"
2. **Planning:** The agent receives the query and the tool schemas. It outputs a `QueryPlanContract` indicating it needs to call `get_financials(region='EMEA', quarter='Q3')` and `get_sales_volume(region='EMEA', quarter='Q3')`.
3. **Execution (Act):** The application layer executes the tools securely, hitting the ERP database.
4. **Observation:** The tools return raw JSON data to the agent.
5. **Reasoning:** The agent analyzes the data. It might realize it needs more info (e.g., "Margins dropped, but revenue is up. Let's check discount rates."). If so, it loops back to step 2.
6. **Final Output:** Once the agent determines it has sufficient information, it synthesizes a final response for the user.

## Lessons Learned
In v1, we over-trusted the LLM. We gave it direct, unrestricted access to a SQL execution tool. It occasionally wrote destructive queries or inefficient joins that crashed the database. 
In v2, we added code-level guardrails: we replaced the raw SQL tool with highly parameterized, read-only API endpoints (e.g., `get_metrics_by_region`), and implemented a strict `max_iterations = 5` limit on the ReAct loop to prevent infinite token burns.
</Use Case: ERP Data Analyst Agent>
