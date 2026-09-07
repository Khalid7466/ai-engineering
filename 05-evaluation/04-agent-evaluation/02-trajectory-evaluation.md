</Agent System Instructions>
<Trajectory Evaluation>
## TL;DR
Trajectory evaluation assesses not just the final output of an agent, but the entire call stack: which tools were called, in what order, with what parameters, and how the agent reacted to tool outputs. It is critical for diagnosing multi-step failures, ensuring safety boundaries, and optimizing agent efficiency.

---

## What is a Trajectory?

A trajectory is the complete log of an agent's reasoning and actions during an execution loop. It typically consists of an alternating sequence:
1. `Thought`: The agent's reasoning.
2. `Action`: The tool invoked.
3. `Action Input`: The parameters passed to the tool.
4. `Observation`: The result returned by the environment.

## Methods for Trajectory Evaluation

### 1. Heuristic and Rule-Based Checks
Before using expensive LLM judges, you can write deterministic rules over the trajectory list:
- **Efficiency:** `len(tool_calls) < MAX_STEPS`. Did it take 20 steps to do a 3-step task?
- **Safety:** Ensure `delete_database` tool was never in the trajectory.
- **Progress:** Did the agent call the exact same tool with the exact same parameters twice in a row? (Detecting infinite loops).

### 2. LLM-as-a-Judge for Trajectories
You can pass the entire trajectory trace to a powerful model (like GPT-4) and ask it to evaluate the agent's logic.

**Example Rubric for the Judge:**
- Did the agent correctly interpret the error messages from the tools?
- Did the agent formulate a logical plan?
- Did the agent hallucinate any tool outputs?

```python
# Conceptual LLM Judge Prompt for Trajectory
PROMPT = \"\"\"
Review the following agent trajectory.
Task: {user_task}
Trajectory:
{trajectory_trace}

Evaluate the agent's efficiency and error recovery on a scale of 1-5.
Did it waste API calls? Did it recover from tool errors gracefully?
\"\"\"
```

### 3. Golden Trajectories and Edit Distance
For specific, constrained tasks, you can define a "Golden Trajectory" (the optimal sequence of tool calls). You can then evaluate the agent's trajectory by calculating the edit distance (Levenshtein distance) between the actual sequence of tools used and the golden sequence. 
- *Caveat:* As discussed in [agent challenges](./01-agent-eval-challenges.md), penalizing deviation too harshly punishes creative or resilient problem-solving.

## Evaluating Error Recovery
One of the most important aspects of trajectory evaluation is testing how the agent handles failure. 
- **The Setup:** Intentionally mock a tool to return a `500 Internal Server Error` or `Invalid Parameter` response on the first try.
- **The Eval:** Check the trajectory. Did the agent panic and output the error to the user? Or did it read the error, adjust its parameters, and retry successfully?

## Production Implications
When a user reports that your agent "failed," looking at the final answer tells you nothing. Trajectory logging and evaluation allow you to build trace viewers (like LangSmith or Phoenix) to visualize the exact step where the agent's logic derailed, which is essential for prompt debugging.

## Common Mistakes
- Only evaluating the final `Observation` and ignoring the `Thought` blocks. The agent might have gotten the right answer for the wrong reasons (flawed logic).
- Not testing agent trajectories against mocked failures. If you only test happy paths, your agent will collapse in production the first time an API times out.

## Interview Questions
- **How would you programmatically detect if an agent is stuck in an infinite loop?**
  *Answer:* Analyze the trajectory array. If you detect repeating subsequences of `Action` and `Action Input` with identical `Observation` errors, the agent is looping.
- **Why is evaluating error recovery crucial in trajectory evaluation?**
  *Answer:* Because in production, tools fail, APIs time out, and databases return empty results. An agent's quality is defined by its ability to observe these errors in the trajectory and adjust its plan, rather than failing the entire task.

## Further Reading
- [AgentBench: Evaluating LLMs as Agents](https://arxiv.org/abs/2308.03688) — Comprehensive framework for evaluating agent trajectories across multiple environments.
