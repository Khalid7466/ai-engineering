## TL;DR
The Architecture Decision Tree is the core framework for selecting the right AI system design pattern for a given business problem. It forces engineers to systematically evaluate a problem based on execution predictability, reasoning requirements, and scale, rather than defaulting to the newest, most complex agent framework. 

---

## The Core Question: Is the Execution Path Fixed?

Every AI system design conversation must start here. 

**If YES (The Pipeline Family):** You know the exact sequence of steps required to solve the problem before the code runs. You just need the LLM to perform specific transformations at certain nodes in that sequence.
**If NO (The Agent Family):** You cannot predict the exact sequence of steps. The system must inspect the state of the world, decide which tool to use, evaluate the result, and decide the next step dynamically.

### The Decision Tree

1. **Is the execution path fixed?**
   - **YES:** Go to step 2.
   - **NO:** Go to step 4.

2. **Does the task require injecting external knowledge?**
   - **NO:** The task is purely transformational (extracting JSON, translating, summarizing, classifying).
     → **Pattern: [Prompt Chaining](02-architectural-patterns/01-prompt-chaining.md)**
   - **YES:** The LLM needs facts it wasn't trained on. Go to step 3.

3. **Can the required knowledge be retrieved in a single, predictable pass?**
   - **YES:** A standard vector search or SQL query is sufficient to gather all context.
     → **Pattern: [Standard RAG](02-architectural-patterns/02-standard-rag.md)**
   - **NO:** The system might need to search, read the result, realize it needs more info, and search again.
     → **Pattern: [Agentic RAG](02-architectural-patterns/03-agentic-rag.md)**

4. **Is the dynamic task narrow and bounded?**
   - **YES:** The system needs to choose between a small set of tools to achieve a very specific, singular goal (e.g., pulling data from API A or B to answer a question).
     → **Pattern: [Autonomous Agent (Single)](02-architectural-patterns/04-autonomous-agent.md)**
   - **NO:** The task is broad, requires multiple specialized domains, or involves generating complex, multi-part artifacts. Go to step 5.

5. **Can the complex task be broken down into sub-tasks governed by a central planner?**
   - **YES:** There is a clear "manager" role that can delegate independent tasks to "workers" and assemble the results.
     → **Pattern: [Orchestrator-Workers](02-architectural-patterns/05-orchestrator-workers.md)**
   - **NO:** The task requires continuous, open-ended collaboration, negotiation, or adversarial review between distinct personas holding separate context.
     → **Pattern: [Multi-Agent System](02-architectural-patterns/06-multi-agent-system.md)**

## The Golden Rule: Left to Right

Always start your design on the "Fixed/Pipeline" side of the tree. Only move down and to the right when you can explicitly prove that the simpler architecture fails to solve the business problem.

Complexity in AI systems scales exponentially, not linearly. A Prompt Chain is 10x easier to debug than Standard RAG. Standard RAG is 10x easier to debug than a Single Agent. A Single Agent is 10x easier to debug than a Multi-Agent System.

## Production Implications

What happens if you choose the wrong architecture?

### Error 1: Over-agentifying simple tasks
*Scenario:* You build a ReAct Agent to extract invoice data into a JSON schema.
*Production Result:* The agent sometimes decides to use its "web search" tool to look up the vendor instead of just reading the document. Latency spikes to 15 seconds. Costs 5x more than needed. The system randomly fails because the agentic loop gets confused.
*Fix:* Downgrade to Prompt Chaining with Structured Outputs.

### Error 2: Under-agentifying complex tasks
*Scenario:* You build a Standard RAG pipeline to answer complex financial due diligence questions like "Compare the QoQ growth of competitor A and B and identify the primary driver."
*Production Result:* The single-pass retrieval pulls in random snippets about "growth," but misses the specific quarterly data. The LLM hallucinates the answer because the context is incomplete. 
*Fix:* Upgrade to Agentic RAG so the system can issue multiple iterative queries (e.g., query 1: competitor A Q1, query 2: competitor B Q1) before synthesizing.

## Common Mistakes
- **Assuming agents are "better" RAG:** Agents are not inherently better; they are more dynamic. They trade reliability and latency for flexibility. 
- **Ignoring the latency budget:** Standard RAG takes 1-2 seconds. An Autonomous Agent taking 3 steps takes 10-15 seconds. If your product requires real-time responses, you cannot use an open-ended agent, regardless of how complex the problem is. You must constrain the problem.
- **Treating multi-agent as a default:** Multi-agent systems look great in demos, but in production, they are notoriously difficult to test, debug, and monitor. Use them only when context windows are maxed out or strict persona separation (like Coder vs. QA) is mandated.

## Interview Questions
- **Q: You need to build a system that translates a user's natural language query into a SQL statement, runs it, and summarizes the data. Which pattern do you choose?**
  - *Answer:* This is Prompt Chaining, or potentially a very simple Orchestrator-Worker if the schema is large. It's a fixed execution path: Intent classification -> SQL Generation -> Execution -> Summarization. Do not use an autonomous agent because the steps are entirely predictable.
- **Q: Your standard RAG system is failing because users are asking "Compare document X and document Y," and the retriever only pulls chunks from X. How do you fix the architecture?**
  - *Answer:* Move to Agentic RAG. The system needs the ability to plan: "I need to retrieve summary of X, then retrieve summary of Y, then compare." A single semantic search cannot execute a logical comparison plan.

## Further Reading
- [Patterns for Building LLM-based Systems & Products](https://eugeneyan.com/writing/llm-patterns/) — Eugene Yan's definitive guide to LLM design patterns.
