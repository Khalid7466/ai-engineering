# Chain of Thought in Agents

## TL;DR
Chain of Thought (CoT) is the practice of prompting an LLM to explain its step-by-step reasoning before outputting a final answer or action. In agents, CoT acts as a cognitive scratchpad, drastically reducing errors in tool selection and task planning.

---

## CoT in the Agent Context
In a standard chatbot, CoT might look like: "Let's think step by step. First, I carry the 1..."
In an agent, CoT is explicitly formalized as the `Thought` step in the ReAct loop, or the `reasoning_trace` field in a structured output contract.

**Without CoT:**
- Input: "Delete my oldest project."
- Output: `delete_project(id="latest")` (Model guesses wrong)

**With CoT:**
- Input: "Delete my oldest project."
- Output: 
  - `Thought: I need to find all projects, sort them by creation date to find the oldest, and then call the delete tool on that specific ID.`
  - `Action: list_projects()`

## Self-Reflection Patterns
Advanced agents use CoT for *Self-Reflection*. Instead of just planning the next step, the agent evaluates its *previous* step.
- **Self-Correction:** After observing a tool error, the prompt forces the agent to reflect: `Thought: The SQL query failed because I used the wrong table name. I should check the schema first.`
- **Verification:** Before returning a final answer, the agent runs a verification CoT: `Thought: Does my compiled answer actually address the user's specific constraints? No, I forgot to filter by year. I will refine it.`

## Scratchpad Thinking
Models have no internal working memory other than the tokens they generate. CoT provides a "scratchpad." If a task requires keeping track of 5 variables, the model cannot hold them in its "head"; it must write them down in the CoT trace so they are part of the context window for the next token prediction.

## Production Implications
CoT increases latency and token costs. A model might generate 200 tokens of reasoning to produce a 10-token tool call. For simple, highly deterministic tasks, you might want to skip CoT to save time. However, for complex routing, skipping CoT is the #1 cause of agent failure. In production, you should log the CoT traces (via LangSmith or custom tracing) but *hide them from the user UI* to maintain a clean experience.

## Common Mistakes
- **Exposing the scratchpad to the user:** Users do not want to see 5 paragraphs of "I am now deciding what to do next." Hide the CoT and show a simple progress spinner ("Analyzing data...").
- **Pseudo-CoT:** Asking the model to "explain its reasoning" *after* it has already output the tool call. This does not improve decision quality; it just justifies the decision it already made.

## Interview Questions
- **Q: Why is Chain of Thought necessary for complex agent tasks?**
  - A: LLMs do not have hidden state or working memory. CoT forces the model to externalize its intermediate calculations and logical steps into the context window, improving accuracy for the final prediction.
- **Q: What is a Self-Reflection pattern in agentic loops?**
  - A: It is a specific CoT step where the agent is prompted to explicitly critique its own previous actions or draft answers before proceeding, leading to autonomous error correction.

## Further Reading
- [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903) — The seminal Google Brain paper on CoT.
