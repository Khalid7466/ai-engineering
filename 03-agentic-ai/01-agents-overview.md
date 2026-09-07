# Agents Overview

## TL;DR
AI Agents combine a Large Language Model (the brain) with access to tools (hands) and memory, allowing them to autonomously pursue complex goals over multiple steps. This shifts the paradigm from simple read-only text generation to active, read-write interaction with the external world.

---

## Brain-in-a-Jar vs Brain-with-Hands
A standard LLM is like a "brain in a jar." It has vast knowledge frozen at its training cutoff, but it cannot look up current weather, modify a file, or execute code. 

An Agent is a "brain with hands." By connecting the LLM to APIs, code interpreters, and databases through Tool Calling, the LLM can perceive its environment and effect change. The LLM serves as the central reasoning engine, deciding *what* hands to use and *when*.

## The Evolution: LLM → RAG → Agent
1. **LLM:** Pure text-in, text-out based on internal weights.
2. **RAG (Retrieval-Augmented Generation):** Text-in, system retrieves relevant documents, LLM reads them and generates text. The system controls the flow.
3. **Agent:** Text-in, LLM decides to retrieve documents, reads them, decides to run a calculation script, evaluates the result, and finally generates text. The LLM controls the flow.

## Read-only vs Read-Write
Early AI applications were strictly read-only (summarization, translation, Q&A). Agents introduce the concept of "Read-Write" AI. They can read emails, but they can also draft and send replies. They can analyze code, and they can also push commits. This dramatically increases their utility but introduces significant safety and security considerations.

## The 4 Core Components of an Agent
1. **Persona (System Prompt):** Defines the agent's role, constraints, tone, and overall objective. It sets the boundaries of behavior.
2. **Reasoning Engine (LLM):** The core intelligence that parses input, plans steps, and evaluates outcomes.
3. **Memory:** How the agent retains context. This includes short-term working memory (current context window) and long-term storage (vector databases).
4. **Tools (Actions):** The executable functions the agent can call to interact with external systems (e.g., `search_web`, `execute_sql`, `send_slack_message`).

## AI Workers, Not Assistants
The term "Assistant" implies a chatbot that helps a human do a task. The industry is shifting toward calling agents "AI Workers" or "Digital Employees." An AI Worker operates asynchronously, takes ownership of an end-to-end process (like triaging support tickets or researching leads), and only surfaces to the human when it needs approval or has finished the job.

## Production Implications
The most common production failure for simple agents is getting stuck in loops. Because the LLM is driving the control flow, an unexpected tool error can cause the model to repeatedly try the same failing action. Production systems must implement hard limits on iterations, robust tool error handling (returning human-readable errors to the model so it can correct course), and comprehensive observability tracing to debug the agent's thought process.

## Common Mistakes
- **Assuming reliability:** Treating the agent's decisions as deterministic code. LLMs are probabilistic; an agent might take a different path to the same goal on two identical runs.
- **Overloading tools:** Giving an agent 50 distinct tools. The model gets confused. It's better to use a multi-agent architecture with specialized agents that have 3-5 tools each.
- **Ignoring context window limits:** Agent loops generate massive amounts of intermediate tokens (observations). Without summarization or truncation, the context window fills up rapidly and crashes.

## Interview Questions
- **Q: What are the core components of an AI Agent?**
  - A: Persona/Instructions, Reasoning Engine (LLM), Memory (short and long term), and Tools.
- **Q: Why are agents considered "Read-Write" compared to traditional LLMs?**
  - A: Traditional LLMs only output text for the user to read. Agents use tools to modify state in external systems, such as writing files, executing code, or sending emails.

## Further Reading
- [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) — Lilian Weng's foundational post on agent architecture.
