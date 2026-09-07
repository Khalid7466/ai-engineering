# Agentic AI

## TL;DR
Agentic AI represents the shift from passive text generators to active systems capable of reasoning, planning, and taking actions in an environment to achieve a goal. It matters because it unlocks automation for complex, multi-step, open-ended tasks that fixed pipelines cannot handle. It applies when your problem requires dynamic decision-making at runtime.

---

## What Agents Are and Why They Exist
An AI Agent is a system where an LLM is given the autonomy to control a loop of reasoning and actions. In traditional software, control flow is determined by hardcoded `if/else` statements. In Agentic AI, the LLM acts as the routing engine, deciding which tool to call, assessing the outcome, and deciding the next step.

Agents exist to solve the "fragility of pipelines." When dealing with unstructured natural language or shifting environments, pre-defining every possible path is impossible. Agents provide resilience by dynamically planning a path to the objective.

## The Spectrum: Pipeline → RAG → Agent
Not everything needs to be an agent. There is a spectrum of autonomy:
1. **Pipeline / Chain:** A fixed sequence of LLM calls (e.g., summarize document, then translate summary). Highly deterministic, zero autonomy.
2. **Retrieval-Augmented Generation (RAG):** The system fetches data based on user input before generating an answer. Mildly dynamic, but the flow (Retrieve → Read → Generate) is static.
3. **Agent:** The LLM decides *whether* to retrieve, *what* to retrieve, *what tool* to use next, and *when* the task is complete.

## When NOT to Use Agents
Using agents for everything is a classic anti-pattern. You should **not** use agents when:
- The task can be solved with a deterministic script or a simple API call.
- Low latency is critical (agents often require multiple slow LLM calls before returning a result).
- 100% predictable execution paths are required (e.g., highly regulated compliance workflows where deviation is unacceptable).
- The cost of an error is catastrophic and cannot be isolated.

## Module Structure
- `01-agents-overview.md`: Core concepts and the anatomy of an agent.
- `02-react-pattern.md`: The fundamental Reason-Act-Observe loop.
- `03-agent-memory/`: Types of memory and how to manage context.
- `04-tool-calling/`: How agents interact with the external world.
- `05-planning-and-reasoning/`: Advanced planning strategies beyond naive ReAct.
- `06-multi-agent-systems/`: Architectures for coordinating multiple specialized agents.
- `07-bleeding-edge/`: Agentic UX and the future of autonomous systems.

## Production Implications
Over-engineering is the biggest risk in Agentic AI. Developers often build multi-agent systems when a simple RAG pipeline would suffice. In production, every additional step an agent can take multiplies the latency, cost, and probability of hallucination or entering an infinite loop. Start simple, add autonomy only when the fixed pipeline breaks.

## Common Mistakes
- **Premature Agency:** Giving the LLM control over the execution flow when a simple `if/else` would work.
- **Under-constraining:** Failing to implement timeouts, max iterations, or strict tool schemas, leading to runaway API costs.
- **Ignoring Latency:** Expecting synchronous web-like response times from an agent that might loop 5 times before answering.

## Interview Questions
- **Q: What is the difference between a Chain and an Agent?**
  - A: A Chain executes a predefined, hardcoded sequence of steps. An Agent uses an LLM to dynamically decide the sequence of steps at runtime based on intermediate observations.
- **Q: When would you choose NOT to use an Agent?**
  - A: When the workflow is highly deterministic, requires sub-second latency, or operates in a high-risk environment where unpredicted actions are unacceptable.

## Further Reading
- [The Spectrum of AI Agency](https://example.com) — A conceptual breakdown of autonomy levels.
