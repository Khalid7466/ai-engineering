</Agent System Instructions>
<Challenges in Agent Evaluation>
## TL;DR
Evaluating AI agents is exponentially harder than evaluating standard LLMs or RAG systems. Agents operate non-deterministically, can achieve goals through multiple valid paths, produce irreversible side effects, and suffer from the credit assignment problem in multi-step workflows. Traditional text-based metrics are entirely inadequate.

---

## Why Agent Evals are Hard

Standard LLM evaluation looks at a static input and output: Given query X, did it generate text Y? 
Agents, however, interact with an environment. They plan, use tools, observe results, and iterate.

### 1. Non-Determinism and Multiple Valid Paths
If you ask an agent to "Find the cheapest flight to NYC and email it to Alice," there are multiple valid trajectories:
- **Path A:** Search Kayak tool -> Draft Email -> Send Email tool.
- **Path B:** Search Expedia tool -> Search Kayak tool -> Compare -> Send Email tool.
Both succeed. You cannot evaluate agents using exact-match on the sequence of tool calls, because Path B is perfectly valid (and perhaps more thorough).

### 2. Side Effects and State
Agents take actions that change the world (writing to databases, sending emails, deleting files). You cannot evaluate them safely in production. 
- You must build mock environments, sandboxes, and dummy APIs. If the mock environment doesn't perfectly replicate production, the eval is useless.

### 3. The Credit Assignment Problem
If an agent fails a 15-step task on step 14, why did it fail?
- Did the LLM hallucinate on step 14?
- Did a tool return an ambiguous error message on step 10, confusing the agent?
- Did the initial planning phase on step 1 fail to account for a constraint?
Assigning blame (credit assignment) to the specific component that caused the cascade of failures is a major infrastructure challenge.

### 4. Multi-Step Cascading Failures
A 95% success rate on individual steps sounds good. But if an agent requires 10 steps to complete a task, the overall success rate is $0.95^{10} \approx 60\%$. Evaluating agents requires measuring both the step-level reliability and the overall task completion rate.

## Evaluating the Goal vs. the Process

- **Goal-based Evaluation:** Did Alice receive an email with the cheapest flight? This requires checking the final state of the environment (e.g., querying the mock email server).
- **Process-based Evaluation:** Did the agent waste money by calling the search API 50 times? Did it attempt a prompt injection on its own tools? 

## Production Implications
Without robust agent evaluations, teams deploy agents that enter infinite loops of tool calling, rack up massive API bills, or execute destructive actions. You cannot deploy an autonomous agent without a CI pipeline that runs it through hundreds of simulated environments and verifies both goal completion and process safety.

## Common Mistakes
- Evaluating only the final text output of the agent, ignoring the tools it called.
- Using a static list of expected tool calls for evaluation, which breaks as soon as the agent finds a different, valid way to solve the problem.
- Testing agents in environments that have real-world side effects.

## Interview Questions
- **What is the credit assignment problem in agent evaluation?**
  *Answer:* In a multi-step agent trajectory, if the final goal fails, it is difficult to determine which specific earlier step, flawed plan, or tool output was the root cause of the failure.
- **Why are exact-match sequences inappropriate for evaluating agent tool calls?**
  *Answer:* Because agents can often achieve the same goal through multiple valid sequences of actions (e.g., trying a tool, failing, trying an alternative tool, and succeeding). Exact match penalizes successful, resilient behavior.

## Further Reading
- [WebArena: A Realistic Web Environment for Building Autonomous Agents](https://arxiv.org/abs/2307.13854) — Standard benchmark for evaluating agents in browser environments.
