# Types of Agent Memory

## TL;DR
Agent memory is categorized into four types: Working (short-term scratchpad), Episodic (past experiences and conversation logs), Semantic (extracted facts and knowledge), and Procedural (learned skills and execution patterns). Understanding and implementing these correctly prevents agents from repeating mistakes or forgetting context.

---

## The Four Types of Memory

### 1. Working Memory (Short-term)
This is the agent's current context window. It includes the system prompt, the immediate user query, and the recent trace of Thoughts, Actions, and Observations for the current task. 
- **Mechanism:** Direct inclusion in the LLM context.
- **Limitation:** Bound by the model's context window limit (e.g., 128k tokens) and degrades in recall accuracy as it grows.

### 2. Episodic Memory (Long-term Experiences)
This is the history of past interactions. It allows the agent to recall what happened yesterday or in previous sessions.
- **Mechanism:** Storing conversation turns in a vector database and retrieving them via semantic search ("What did we discuss about the database schema last week?").
- **Limitation:** Retrieval can be noisy. The agent might pull in an irrelevant past conversation just because it shares keywords.

### 3. Semantic Memory (Long-term Facts)
Instead of storing raw conversation logs, semantic memory extracts and consolidates *facts* about the user or the world.
- **Mechanism:** An asynchronous process that reads episodic logs and updates a knowledge graph or a structured profile (e.g., "User prefers Python," "Database is Postgres 14").
- **Limitation:** Requires complex entity resolution and contradiction handling (e.g., if the user later says "I switched to MySQL").

### 4. Procedural Memory (Skills & Patterns)
Procedural memory is the agent's knowledge of *how* to do things. 
- **Mechanism:** In simple agents, this is hardcoded in the system prompt or tool descriptions. In advanced systems, successful execution plans (e.g., a complex SQL join that finally worked) are saved and retrieved when a similar task appears.

## Why You Need All 4 for Production
A production agent relying only on Working Memory is an amnesiac. It will ask the user for their API key every single session. Relying only on Episodic Memory means the agent has to read through 50 pages of chat logs to realize the user's name is "Alice." Combining Semantic (fast fact lookup) with Working (current task state) creates a snappy, personalized experience.

## Production Implications
Memory management is fundamentally a database synchronization problem. If an agent updates a record in an external system but fails to update its semantic memory, it will hallucinate the old state in the next turn. Ensure that actions which modify external state also trigger an update or invalidation of the relevant semantic memory.

## Common Mistakes
- **Dumping everything into context:** Trying to put all episodic memory into the working memory, causing massive latency and API costs.
- **Ignoring Semantic Memory:** Storing only raw logs (episodic) and forcing the agent to infer facts on the fly every time.
- **Static Procedural Memory:** Never updating the system prompt based on common failure patterns observed in production.

## Interview Questions
- **Q: What is the difference between Episodic and Semantic memory in an AI agent?**
  - A: Episodic memory stores raw past events and conversation logs (the "what happened"). Semantic memory stores distilled facts and concepts extracted from those events (the "what is true").
- **Q: How is Working Memory implemented in an LLM agent?**
  - A: Working memory is implemented directly via the context window, passing the immediate history of the current interaction to the model on each API call.

## Further Reading
- [Generative Agents: Interactive Simulacra of Human Behavior](https://arxiv.org/abs/2304.03442) — The Stanford paper detailing the architecture of agent memory streams.
