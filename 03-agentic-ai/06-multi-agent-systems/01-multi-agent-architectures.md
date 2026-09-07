# Multi-Agent Architectures

## TL;DR
Multi-agent systems divide complex tasks among specialized LLM personas, much like a human organization. The three primary architectures are Network (peer-to-peer), Supervisor (orchestrator + workers), and Hierarchical (nested supervisors). The core principle is that specialized agents out-perform generalist agents on complex tasks.

---

## The Principle: Specialization > Generalization
If you give one agent a system prompt to be a "Software Engineer, QA Tester, and Product Manager" and give it 50 tools, it will suffer from prompt confusion, hallucinate tool arguments, and fail. 
Instead, you create three separate agents:
1. `EngineerAgent` (5 coding tools)
2. `QAAgent` (3 testing tools)
3. `PMAgent` (2 Jira tools)
They coordinate to solve the problem.

## Architectures

### 1. Supervisor (Orchestrator-Worker)
A single "Router" or "Supervisor" agent receives the user query, breaks it down, and delegates sub-tasks to specialized worker agents.
- **When to use:** The standard default for most enterprise applications. Good for tasks that can be cleanly divided (e.g., "Research the company, then write an email" -> `ResearcherAgent` -> `WriterAgent`).

### 2. Network (Peer-to-Peer / Swarm)
Agents talk directly to each other without a central supervisor. Agent A finishes a task and autonomously decides to hand the context over to Agent B.
- **When to use:** Open-ended, collaborative tasks (e.g., a simulated brainstorming session between a `CriticAgent` and a `CreatorAgent`).
- **Drawbacks:** Harder to trace, prone to infinite argument loops.

### 3. Hierarchical
Nested supervisors. The `CEOAgent` delegates to the `EngineeringManagerAgent`, who delegates to `FrontendAgent` and `BackendAgent`.
- **When to use:** Extremely complex, long-running workflows (e.g., autonomous software factories).

## Production Implications
Multi-agent systems multiply cost and latency. If user input requires 3 agents to coordinate, the user might wait 2 minutes. Furthermore, the error rate is compounded. If the `ResearcherAgent` hallucinates a fact, the `WriterAgent` will confidently write a completely false email. You must implement strict data validation contracts between agents.

## Common Mistakes
- **Overhead over value:** Building a 4-agent system for a task that a single well-prompted agent could do in one step.
- **Assuming perfect communication:** Passing the entire massive context window from Agent A to Agent B, causing Agent B to get lost in the noise. Context should be summarized during handoffs.

## Interview Questions
- **Q: Why would you choose a multi-agent architecture over a single agent with many tools?**
  - A: To avoid prompt confusion and token limit issues. Specialized agents with narrow scopes and fewer tools are more accurate and easier to debug than a single monolithic generalist agent.
- **Q: Describe the Supervisor multi-agent pattern.**
  - A: A central orchestrator agent receives the task, creates a plan, and delegates specific sub-tasks to specialized worker agents. It then aggregates their results to return the final answer.

## Further Reading
- [AutoGen: Enabling Next-Gen LLM Applications](https://arxiv.org/abs/2308.08155) — Microsoft's paper on multi-agent conversation frameworks.
