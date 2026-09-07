# Planning Patterns

## TL;DR
Planning patterns dictate how an agent decides what to do. While ReAct discovers steps dynamically, patterns like Plan-and-Execute generate a full itinerary upfront, and LLM Compiler parallelizes independent steps. Choosing the right pattern balances adaptability against cost and latency.

---

## 1. ReAct (Dynamic Planning)
The agent plans one step at a time based on the immediate observation.
- **Mechanism:** `Thought -> Action -> Observation` (repeat until done).
- **When to use:** Highly dynamic environments where the next step strictly depends on the outcome of the previous step (e.g., debugging a server error).
- **Drawbacks:** Slow. If the task has 10 steps, it requires 10 sequential LLM calls.

## 2. Plan-and-Execute
The agent separates planning from execution. It first writes out a comprehensive step-by-step plan, then executes the steps sequentially.
- **Mechanism:**
  1. **Planner LLM:** Takes the user query and generates a list of steps.
  2. **Executor LLM (or code):** Executes step 1, step 2, step 3...
  3. **Synthesizer LLM:** Reviews all outputs and writes the final answer.
- **When to use:** Deterministic tasks where the steps are known upfront (e.g., "Summarize doc A, summarize doc B, and compare them").
- **Drawbacks:** Brittle. If step 2 fails, the entire upfront plan might be invalidated.

## 3. LLM Compiler (Parallel Execution)
Inspired by software compilers, this pattern creates a Dependency Graph (DAG) of tasks.
- **Mechanism:** The planner identifies which tasks are independent and which depend on previous outputs. It then executes independent tasks concurrently.
- **When to use:** Tasks with multiple independent data gathering steps (e.g., "Get the stock price for AAPL, MSFT, and GOOG").
- **Drawbacks:** High implementation complexity. Requires robust async orchestration.

## Production Implications
Defaulting to ReAct for everything is a common anti-pattern that leads to unacceptably high latency. If you ask an agent to research 5 companies, a ReAct agent will do it sequentially, taking 5 minutes. An LLM Compiler will do it in parallel, taking 30 seconds. In production, you often need a hybrid: Plan-and-Execute with a fallback to ReAct if a step fails.

## Common Mistakes
- **Using ReAct for static tasks:** Forcing an agent to dynamically reason through a standard onboarding workflow that never changes.
- **Rigid Plan-and-Execute:** Failing to implement replanning. If step 2 of a 10-step plan fails, the agent must be able to pause, assess the failure, and generate a *new* plan, rather than blindly continuing to step 3.

## Interview Questions
- **Q: What is the main difference between ReAct and Plan-and-Execute?**
  - A: ReAct interleaves planning and execution at every step, adapting dynamically. Plan-and-Execute separates them, generating a complete sequence of steps upfront before executing them.
- **Q: When would you use the LLM Compiler pattern?**
  - A: When a task requires multiple sub-tasks that do not depend on each other, allowing them to be executed in parallel to reduce latency.

## Further Reading
- [Plan-and-Solve Prompting](https://arxiv.org/abs/2305.04091) — Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models.
