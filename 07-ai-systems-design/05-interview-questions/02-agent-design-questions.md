## TL;DR
This file contains five common AI Engineering interview questions focused on Agent system design, complete with model answers that demonstrate production-level architectural thinking and safety considerations.

---

## Question 1: System Architecture
**"Design an agent that can autonomously research a topic on the web and write a comprehensive 5-page report."**

**Model Answer:**
A single Autonomous Agent will fail at this due to context window exhaustion and loss of focus. I would design this using the **Orchestrator-Worker** pattern.
1. **Planner (Orchestrator):** Takes the topic and generates a JSON outline with 5 distinct sections.
2. **Research Workers:** For each section, a parallel Research Agent is spawned. It has a `web_search` tool and a `scrape_page` tool. It researches only its specific section and outputs a localized summary. 
3. **Context Engineering:** To prevent context bloat, the scraper tool does not return raw HTML; it pipes through a small LLM that extracts only the text relevant to the current section.
4. **Synthesizer (Orchestrator):** The Orchestrator receives the 5 localized summaries, reviews them for flow, and drafts the final report.

## Question 2: Safety and Guardrails
**"How do you prevent an agent with access to a company database from taking destructive actions (like dropping tables or emailing clients inappropriately)?"**

**Model Answer:**
You can never rely on the system prompt for security (e.g., "Do not drop tables"). Prompt injection can easily bypass this.
1. **Principle of Least Privilege:** The database credentials the agent uses must be strictly Read-Only at the IAM/database level. It physically cannot drop a table.
2. **Human-in-the-Loop (HITL) for State Changes:** If the agent needs to send an email, the `send_email` tool does not actually send an email. It writes a payload to a staging queue. A human reviews the drafted email in a dashboard and clicks "Approve," which triggers the actual send.
3. **Deterministic Tool Wrappers:** If the agent writes SQL, the SQL string is evaluated by a Python regex or SQL parser to reject any non-SELECT statements *before* execution.

## Question 3: Debugging Loops
**"Your agent is stuck in an infinite loop. It calls a tool, gets an error, and calls the exact same tool with the exact same inputs again. How do you fix this?"**

**Model Answer:**
This is the "Sycophancy Loop." It happens when the LLM apologizes for the error but lacks the reasoning capability to fix it.
1. **Framework-level Circuit Breakers:** I implement state tracking. If the agent executes the exact same tool call (identical arguments) twice and receives the same error twice, the system intercepts the execution, aborts the loop, and escalates to a human.
2. **Prompt Engineering:** Modify the tool's error response. Instead of just returning "Syntax Error," return "Syntax Error. You MUST change your input parameters before trying again. Here is an example of a correct input..."
3. **Model Upgrade:** If using a smaller model (e.g., 8B parameters), I would upgrade the agent's reasoning engine to a frontier model (GPT-4o, Claude 3.5 Sonnet), which are much better at self-correction.

## Question 4: Multi-Agent Design
**"Design a multi-agent system for code review. Why use multi-agent instead of a single prompt?"**

**Model Answer:**
Single prompts suffer from confirmation bias; an LLM is bad at aggressively critiquing code it just wrote. A multi-agent system introduces necessary adversarial personas.
1. **Architecture:** A state graph with two distinct personas. Agent A is the "Author" (optimizes for speed and feature completion). Agent B is the "Reviewer" (optimizes for security, edge cases, and performance).
2. **Handoff Protocol:** Agent A writes code and passes it to Agent B. Agent B cannot edit the code; it can only output a list of requested changes or an "Approve" flag. 
3. **Halting Condition:** If Agent B requests changes, control routes back to A. This loops until B approves, or until `max_revisions=3` is hit, at which point the system halts and asks a human to resolve the dispute.

## Question 5: Evaluation
**"How do you evaluate the performance of an autonomous agent in production?"**

**Model Answer:**
Evaluating agents is fundamentally different from evaluating standard LLM outputs because the execution path is non-deterministic.
1. **Trajectory Evaluation:** I don't just evaluate the final answer; I evaluate the path taken. I use an LLM-as-a-Judge to grade the trace: "Did the agent take the most efficient path?", "Did it use unnecessary tools?"
2. **Task Completion Rate:** The binary metric of whether the agent successfully achieved the user's goal without hitting max iterations or crashing.
3. **Cost and Latency per Task:** Agents can solve a problem by blindly searching the web 50 times. While the output is "correct", the cost is unacceptable. I monitor the average number of tool calls per session. If it spikes, the agent is thrashing.
