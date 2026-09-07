## TL;DR
This is the capstone module of the AI Engineering knowledge base. Having mastered fundamentals (embeddings, fine-tuning, RAG, prompt engineering), you are now ready for the hardest part of building AI products: System Design. This module covers how to compose these primitives into production-grade systems, introducing the core mental model of fixed versus dynamic execution paths, and providing a framework for matching business problems to architectural patterns.

---

## The Shift to System Design
Up until this point, we have primarily focused on the mechanics of individual AI components. You know how to chunk documents, embed them, and retrieve them for RAG. You know how to structure a prompt to improve reasoning. You know how to format data for fine-tuning. 

In production, these components rarely operate in isolation. A single AI feature in a modern application often requires orchestrating multiple LLM calls, deterministic code, retrieval systems, and state management. The challenge shifts from "how do I make the model output X?" to "how do I string together models, tools, and code to solve business problem Y reliably, at scale, and within budget?"

AI System Design is the discipline of architecting these pipelines and agentic systems.

## The Core Mental Model: Fixed vs. Dynamic Execution Paths

The single most important decision in AI system design is determining the nature of the execution path. All AI architectures exist on a spectrum between purely fixed (deterministic) and purely dynamic (agentic).

### Fixed Execution Paths (Pipelines)
In a fixed execution path, the steps to solve the problem are known ahead of time. The software developer defines the sequence of operations. The LLM is invoked at specific, predictable points in the pipeline to perform bounded tasks (e.g., classification, extraction, summarization).

**Characteristics:**
- **Predictability:** The system will always execute steps A → B → C.
- **Observability:** Easy to monitor and debug. When it fails, you know exactly which step failed.
- **Latency:** Generally lower and more predictable.
- **Examples:** Prompt Chaining, Standard RAG, parallel mapping.

### Dynamic Execution Paths (Agents)
In a dynamic execution path, the steps to solve the problem are *not* known ahead of time. The software developer defines a goal, a set of tools, and an environment. The LLM itself determines the sequence of operations, deciding which tools to call, analyzing the output, and deciding what to do next.

**Characteristics:**
- **Flexibility:** Can handle novel edge cases and complex, open-ended tasks.
- **Unpredictability:** The system might take 2 steps or 20 steps to reach a conclusion.
- **Latency:** Highly variable and generally slower due to multiple sequential LLM calls.
- **Examples:** Autonomous ReAct Agents, Multi-Agent Systems.

### The Golden Rule of AI System Design
**Start as far to the left (fixed) on the spectrum as possible, and only move to the right (dynamic) when forced by the complexity of the problem.** 

Engineers often fall into the trap of building a dynamic, autonomous agent because it feels "smarter" or more cutting-edge, only to struggle with reliability, runaway costs, and impossible debugging loops. If a problem can be solved with a three-step prompt chain, do not build an agent to solve it.

## What's in this Module?

This module is structured to guide you from foundational decisions to complex implementations:

1. **Architecture Decision Tree:** A rigorous framework for deciding *which* pattern to use for a given problem.
2. **Architectural Patterns:** Deep dives into the 6 canonical patterns (from Prompt Chaining to Multi-Agent Systems), explaining when to use them and what breaks in production.
3. **Design Process:** The mechanics of designing an AI system, including constraint definition, context engineering, and execution topologies.
4. **Case Studies:** Full architectural walkthroughs of real-world AI systems, spanning customer support, ERP data analysis, legal AI, and software engineering.
5. **Interview Questions:** Scenarios, tradeoffs, and debugging challenges to test your system design acumen.

→ See [01-architecture-decision-tree.md](01-architecture-decision-tree.md) to begin exploring the design framework.
