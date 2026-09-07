<Use Case: ERP Data Analyst Agent>
## Objective
An enterprise wants an AI assistant that can answer ad-hoc questions about their internal ERP database (e.g., SAP, NetSuite). Users will ask questions like, "What was our top-selling product in the Northwest region last quarter, and how does that compare to the same quarter last year?"

**Constraints:**
- The database has 500+ tables. 
- Absolute accuracy is required. Generating a syntactically valid SQL query that calculates the wrong metric is a critical failure.
- The system must NEVER modify the database (Read-Only).

## Why an Orchestrator-Worker Pattern?
The naive approach is text-to-SQL: putting the database schema in a prompt and asking an LLM to output a query. 
- **Why it failed:** With 500 tables, the schema doesn't fit in the context window. Even if it did, LLMs struggle to navigate massive, poorly-named enterprise schemas. Furthermore, complex comparative questions require multiple SQL queries and data synthesis.
- **The Pivot:** We need an Orchestrator-Worker pattern. The Orchestrator plans the analysis, and a specialized SQL Worker (equipped with tools to explore the schema dynamically) executes the plan.

## Technical Decisions

### Decision 1: Schema Exploration vs. Schema Injection
- **Chose:** Dynamic Schema Exploration Tools.
- **Rejected:** Stuffing the schema into the prompt (Context Pollution).
- **Rationale:** Instead of giving the agent the whole schema, we give it tools: `list_tables()`, `get_table_schema(table_name)`, and `search_schema_descriptions(keyword)`. The agent discovers the schema exactly like a human analyst would.

### Decision 2: The QueryPlanContract
- **Chose:** Forcing the LLM to write a plan before executing SQL.
- **Rejected:** Letting the LLM run SQL immediately.
- **Rationale:** We force the Orchestrator to output a `QueryPlan` JSON object. This acts as a chain-of-thought mechanism, drastically reducing logical errors in the subsequent SQL generation.

### Decision 3: Security and Read-Only Enforcement
- **Chose:** Database-level user permissions + regex guardrails.
- **Rejected:** Just telling the LLM "don't write to the DB".
- **Rationale:** System prompts are easily bypassed. The database connection string used by the AI uses a strictly Read-Only role. Furthermore, any generated SQL is parsed by a Python regex to block `DROP`, `UPDATE`, `INSERT`, `DELETE` before it is ever sent to the database.

## Architecture Walkthrough

```python
# The Orchestrator-Worker Architecture

def erp_analyst_pipeline(user_question: str) -> str:
    # STEP 1: Orchestrator creates a plan
    plan = orchestrator_llm.predict(
        prompt=f"Create a step-by-step data analysis plan for: {user_question}",
        schema=AnalysisPlan # e.g., Step 1: Find revenue for Q3. Step 2: Find revenue for Q3 last year.
    )
    
    results = []
    # STEP 2: The SQL Worker Agent executes the plan
    for step in plan.steps:
        step_result = run_sql_agent(step.description)
        results.append(step_result)
        
    # STEP 3: Orchestrator synthesizes the final answer
    final_report = orchestrator_llm.predict(
        prompt=f"Answer the user based on these data results: {results}"
    )
    return final_report

def run_sql_agent(task: str):
    # This is a cyclic graph (Agent) that can explore the schema and run queries
    agent = Agent(
        tools=[search_schema, get_table_details, execute_sql_safely],
        system_prompt="You are a SQL expert. Explore the schema, then write and run queries."
    )
    return agent.run(task)

def execute_sql_safely(query: str):
    # HARD GUARDRAIL: No write operations allowed
    if contains_write_operations(query):
        return "Error: Only SELECT statements are permitted."
        
    try:
        # Executed using a Read-Only DB user
        return read_only_db.execute(query)
    except SQLError as e:
        return f"Query failed with error: {e}. Please fix the syntax and try again."
```

## Lessons Learned

1. **Self-Correction is powerful but dangerous:** When the `execute_sql_safely` tool returns a syntax error, the agent often successfully rewrites the query and tries again. However, if it loops more than 3 times, it usually goes off the rails. We implemented a hard `max_retries=3` circuit breaker.
2. **Semantic mapping is required:** Enterprise databases have columns named `REV_Q3_ACT`. The LLM doesn't know this means "Actual Q3 Revenue". We had to create a separate vector database containing a "data dictionary" mapping business terms to column names, which the agent could search via the `search_schema_descriptions` tool.
3. **Data shape matters:** If a SQL query returns 10,000 rows, returning that raw data to the agent will blow up the context window. We modified the `execute_sql_safely` tool to always append `LIMIT 100` unless explicitly told otherwise, and return a summary of the dataframe (e.g., column means) rather than raw rows if the result set was too large.
</Use Case: ERP Data Analyst Agent>
