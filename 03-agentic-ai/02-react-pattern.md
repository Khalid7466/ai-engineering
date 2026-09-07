# The ReAct Pattern

## TL;DR
ReAct (Reasoning and Acting) is the foundational design pattern for AI agents. It forces the LLM to alternate between thinking about what to do next (Reasoning), taking an action via a tool (Acting), and observing the result (Observation) in a continuous loop until the task is complete.

---

## The Reason → Act → Observe Loop
The core innovation of ReAct is combining chain-of-thought reasoning with tool execution. Instead of just predicting an answer, the model is prompted to follow a strict cycle:
1. **Thought (Reason):** The model analyzes the current state and decides what information or action is needed next.
2. **Action (Act):** The model formats a request to call a specific tool.
3. **Observation:** The application executes the tool and returns the raw output back to the model.

This loop repeats. The model uses the Observation to inform its next Thought.

## Trace Example
Here is what a typical ReAct trace looks like when asked: "What is the square root of the population of the capital of France?"

```text
Thought 1: I need to find the capital of France first.
Action 1: search_knowledge_base(query="capital of France")
Observation 1: The capital of France is Paris.

Thought 2: Now I need to find the population of Paris.
Action 2: search_web(query="population of Paris 2024")
Observation 2: The estimated population of Paris in 2024 is 2.1 million.

Thought 3: I need to calculate the square root of 2,100,000.
Action 3: calculator(expression="sqrt(2100000)")
Observation 3: 1449.13767462

Thought 4: I have the final answer.
Action 4: FinalAnswer(answer="The square root of the population of Paris is approximately 1449.")
```

## How the Loop Terminates
The loop terminates when the model determines it has gathered enough information to fulfill the user's request. It usually signals this by calling a special tool, often named `FinalAnswer`, `Finish`, or simply returning a standard text response instead of a tool call structure.

## Max Iterations as a Guardrail
ReAct loops are inherently dangerous in production because they can run infinitely if the model gets confused or if a tool constantly returns an unhelpful error. 
You **must** implement a `max_iterations` counter (e.g., 5 or 10 steps). If the loop hits this limit, the system forcefully terminates the agent, returning an error like "Agent stopped after reaching maximum steps."

## When ReAct Gets Stuck (Loop Detection)
Even with max iterations, burning 10 API calls doing the exact same failing action is expensive. 
Models often get stuck in a rut:
- Thought: I need to read the file.
- Action: read_file('data.csv')
- Observation: Error: File not found.
- Thought: The file wasn't found. Let me try reading it again.
- Action: read_file('data.csv')

**Mitigations:**
- **Informative Errors:** Instead of generic stack traces, return actionable errors to the model (e.g., "Error: File 'data.csv' not found. Try using list_dir to see available files.").
- **Heuristic Loop Detection:** In your application code, track the hash of the last N actions. If the agent proposes an identical tool call with identical arguments 3 times in a row, forcefully inject a system message: "You are repeating the same action and it is failing. Try a different approach or give up."

## Production Implications
ReAct is token-intensive. Every time the loop iterates, the entire history of previous Thoughts, Actions, and Observations is sent back to the model. This means step 6 costs significantly more than step 1. For long-running tasks, you must implement context window management (summarizing early observations) to prevent token limits and control costs.

## Common Mistakes
- **Hiding errors from the model:** If a tool fails, developers sometimes return an empty string or crash the app. You must return the stringified error *as the observation* so the model can reason about the failure.
- **Missing "Thought" forcing:** Forgetting to require the model to output its reasoning *before* the action. The model needs that scratchpad space to plan; forcing it to output just the tool call degrades its decision-making quality.

## Interview Questions
- **Q: What problem does the ReAct pattern solve compared to standard Chain of Thought?**
  - A: Standard CoT happens entirely inside the model's internal knowledge. ReAct allows the model to ground its reasoning in external reality by taking actions and observing real-world feedback before continuing its thought process.
- **Q: How do you prevent a ReAct agent from running forever?**
  - A: Implement a hard `max_iterations` limit on the execution loop and use heuristic loop detection to catch repetitive failing actions.

## Further Reading
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) — The original Princeton/Google research paper.
