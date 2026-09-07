# Multi-Agent Frameworks

## TL;DR
The AI engineering ecosystem offers several frameworks for orchestrating multi-agent systems. LangGraph (state machines) is best for complex, production-grade workflows. CrewAI (role-based) is best for rapid prototyping. AutoGen (conversational) is best for peer-to-peer debate scenarios.

---

## 1. LangGraph
Built by the LangChain team, LangGraph treats multi-agent workflows as cyclical graphs (State Machines). You define nodes (agents or Python functions) and edges (conditional routing logic).
- **Core Concept:** Shared State. Every node receives a global `State` object and returns an update to that state.
- **Best For:** Complex, deterministic enterprise workflows. If you need strict control over exactly how and when Agent A passes data to Agent B, LangGraph is the industry standard.
- **Drawback:** Steep learning curve, heavily relies on LangChain abstractions.

## 2. CrewAI
CrewAI focuses on a role-playing paradigm. You define `Agents` (with roles, goals, and backstories) and `Tasks`. You then assemble them into a `Crew` and define a process (Sequential or Hierarchical).
- **Core Concept:** Role-playing and sequential task delegation.
- **Best For:** Rapid prototyping and scenarios that map neatly to human organizational structures (e.g., an automated marketing department).
- **Drawback:** Under the hood, it can be a bit of a "black box," making it harder to debug granular state changes or implement complex conditional branching compared to LangGraph.

## 3. Microsoft AutoGen
AutoGen treats agents as conversational entities. You create agents and have them literally chat with each other to solve a problem.
- **Core Concept:** Message Passing. Agents trigger based on receiving a message in a simulated chat room.
- **Best For:** Code generation, debugging, and open-ended research where multiple "personas" debating a topic yields a better result than a strict workflow.
- **Drawback:** Conversational routing is highly non-deterministic. It is very easy for agents to get stuck in an endless loop politely thanking each other instead of writing code.

## Comparison Table

| Feature | LangGraph | CrewAI | AutoGen |
| :--- | :--- | :--- | :--- |
| **Paradigm** | State Machine (Graphs) | Role-based (Crews) | Conversational (Chat) |
| **Control Flow** | Highly Deterministic | Sequential / Hierarchical | Highly Probabilistic |
| **State Management** | Shared Global State | Task Outputs | Chat History |
| **Learning Curve** | High | Low | Medium |

## Production Implications
Do not marry a framework before you understand your workflow. If you use AutoGen for a strict ETL pipeline, you will spend weeks fighting the framework to make it deterministic. If you use LangGraph for a creative brainstorming task, you will over-engineer a graph that could have been a simple API call. Many senior teams eventually abandon these frameworks and build custom orchestration using native Python `asyncio` and standard structured LLM calls.

## Common Mistakes
- **Framework over-reliance:** Assuming the framework will magically fix LLM hallucination. A badly prompted agent will fail in LangGraph just as easily as it fails in a raw Python script.
- **Using AutoGen for strict pipelines:** Trying to force conversational agents to execute a strict 5-step deterministic workflow.

## Interview Questions
- **Q: When would you choose LangGraph over CrewAI for a project?**
  - A: LangGraph is preferable for complex, production-grade systems requiring highly deterministic routing, cyclical graphs, and strict control over shared state. CrewAI is better for rapid prototyping of sequential, role-based tasks.
- **Q: What is a common failure mode when using conversational multi-agent frameworks like AutoGen?**
  - A: Agents getting stuck in endless conversational loops (e.g., endlessly agreeing with each other or apologizing for errors) without actually completing the assigned task.

## Further Reading
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [CrewAI Documentation](https://docs.crewai.com/)
