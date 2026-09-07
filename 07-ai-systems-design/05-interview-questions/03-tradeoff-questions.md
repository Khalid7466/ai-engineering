## TL;DR
System design is the art of managing tradeoffs. In AI Engineering, there are no absolute "right" answers, only better fits for specific constraints. This file covers the five most common architectural tradeoffs you must navigate (and defend) in interviews and production design reviews.

---

## Question 1: RAG vs. Fine-tuning
**"When should you choose RAG, and when should you choose Fine-tuning?"**

**Model Answer:**
You choose based on whether you are optimizing for **Knowledge** or **Form/Style**.
- **Use RAG for Knowledge:** If the system needs to know specific, changing facts (e.g., today's inventory levels, user documents), use RAG. Fine-tuning is terrible for memorizing facts; the model will confidently hallucinate outdated information.
- **Use Fine-tuning for Form/Style:** If the system needs to output data in a very specific JSON schema, speak in a highly stylized corporate tone, or learn a specialized domain vocabulary (like parsing medical jargon), use fine-tuning. 
- **The Hybrid:** In production, we often use both. We use RAG to fetch the facts, and we feed those facts into a small, fast model that has been fine-tuned to format the answer perfectly.

## Question 2: Agent vs. Pipeline
**"How do you decide between building an Autonomous Agent and a fixed Prompt Chain?"**

**Model Answer:**
The decision rests entirely on the **predictability of the execution path**. 
- **Use a Pipeline (Prompt Chain):** If the steps to solve the problem are known ahead of time (e.g., Extract Email -> Classify Intent -> Draft Response). Pipelines guarantee lower latency, predictable costs, and trivial debugging.
- **Use an Agent:** If the task requires dynamic exploration (e.g., "Find the bug in this codebase"). The system must be able to try something, fail, observe the error, and try a different approach. Agents trade latency and cost for flexibility.
*Golden Rule:* Always start with a Pipeline. Only upgrade to an Agent when the Pipeline fails to handle the variance in user requests.

## Question 3: Big Context vs. RAG
**"Models now have 1 million to 2 million token context windows. Is RAG obsolete? Can't we just put all the documents in the prompt?"**

**Model Answer:**
RAG is not obsolete. While massive context windows are technically possible, they fail in production for three reasons:
1. **Cost:** Passing 1 million tokens into an API for every single user query will cost dollars per query, not fractions of a cent. RAG keeps the prompt small and cheap.
2. **Latency:** Processing 1 million input tokens takes time (often 10-30 seconds). A RAG system with a small payload returns answers in <2 seconds.
3. **Precision (Lost in the Middle):** Research consistently shows that models suffer from degraded recall when information is buried in massive context blocks. RAG forces the model to focus only on highly relevant, filtered information.
Massive context is great for one-off analyses (e.g., "Summarize this entire book"), but RAG is required for scalable, multi-user systems.

## Question 4: Open-Source vs. Closed API
**"What are the real tradeoffs between using a closed API (OpenAI/Anthropic) vs. self-hosting an open-weight model (Llama 3/Mistral)?"**

**Model Answer:**
1. **Data Privacy / Compliance:** If you have strict HIPAA, SOC2, or defense requirements that forbid sending data to third parties, you must self-host open-source models within your VPC.
2. **Cost at Scale:** APIs are cheaper to start (pay per token), but at massive scale (millions of queries), self-hosting a smaller 8B parameter model on dedicated GPUs becomes significantly cheaper than paying OpenAI margins.
3. **Capability & Maintenance:** Closed APIs give you access to frontier reasoning (GPT-4o) with zero MLOps overhead. Self-hosting requires a dedicated DevOps team to manage GPU clusters, vLLM deployment, and continuous updates.

## Question 5: Single Agent vs. Multi-Agent
**"Where is the line between needing one complex agent vs. a multi-agent system?"**

**Model Answer:**
The line is drawn at **Persona Conflict and Context Pollution**.
- **Single Agent:** Works well if the goal is unified and the toolset is small (e.g., a "Research Agent" with a web search tool).
- **Multi-Agent:** Required when the task demands adversarial validation (e.g., a "Coder" trying to ship fast vs. a "QA Tester" trying to break things). If you put both instructions into a single prompt, the model compromises and does neither well. Multi-agent is also required when the total context required for the task exceeds what one agent can hold without forgetting its original instructions.
