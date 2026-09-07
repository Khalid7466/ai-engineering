# In-Context Memory Management

## TL;DR
In-context memory is the most immediate form of agent memory, relying on the LLM's context window. Because context windows are finite and long contexts degrade performance and increase cost, you must actively manage this memory using summarization, sliding windows, and truncation.

---

## Conversation History in the Context Window
Every time an agent takes a step in a ReAct loop, the new `Thought`, `Action`, and `Observation` must be appended to the list of messages and sent back to the LLM. 
```python
messages = [
    {"role": "system", "content": "You are a helpful agent."},
    {"role": "user", "content": "Analyze this data."},
    {"role": "assistant", "content": "Thought: I should read the file.\nAction: read_csv"},
    {"role": "tool", "content": "Row 1, Row 2, Row 3..."}
]
```
As this list grows, the cost per API call increases linearly, and the total cost of the loop increases quadratically.

## When Context Fills Up
When an agent runs for 20+ steps, or when a tool returns a massive JSON payload, you will hit the context limit (e.g., 128k tokens). Even before hitting the hard limit, models suffer from "Lost in the Middle" syndrome—they forget instructions placed in the middle of a massive context block.

## Strategies for Managing Context

### 1. Sliding Window (FIFO)
The simplest approach: keep the system prompt, but only retain the last $N$ messages (e.g., the last 5 turns).
- **Pros:** Trivial to implement. Guarantees bounded context size.
- **Cons:** The agent instantly forgets anything that happened $N+1$ steps ago, which can cause it to repeat steps it already completed.

### 2. Summarization to Compress History
Instead of dropping old messages, periodically use a smaller, cheaper LLM (or the same LLM) to summarize the older portion of the conversation.
```text
System: [Summary of steps 1-10: The agent found the database credentials, logged in, and discovered the 'users' table is empty.]
Assistant: Thought: Now I need to check the 'logs' table.
... (recent messages)
```
- **Pros:** Retains the high-level narrative without the token bloat.
- **Cons:** Summarization is lossy. Exact IDs, error codes, or specific paths might be summarized away, causing the agent to fail if it needs them later.

### 3. Observation Truncation
Tools often return too much data. If `search_web` returns a 50,000-token webpage, the context window is blown immediately.
- **Solution:** Enforce strict caps on tool outputs. If a tool output exceeds 2,000 tokens, truncate it and append a note: `[Output truncated. Use the 'grep_file' tool to search for specific strings.]`

## Production Implications
Failing to manage in-context memory leads to catastrophic failures in long-running tasks. You will see API errors (`context_length_exceeded`) or observe the agent entering bizarre hallucination states as its attention mechanism degrades over 100k+ tokens. Implement robust token counting (using libraries like `tiktoken`) in your orchestration layer before sending requests.

## Common Mistakes
- **Appending raw HTML/JSON:** Directly injecting massive tool outputs into the context window without truncation.
- **Losing the System Prompt:** Accidentally dropping the initial system prompt when applying a sliding window, causing the agent to forget its persona entirely.
- **Ignoring "Lost in the Middle":** Trusting that a 100k token context window means the model will perfectly recall a detail from token 50,000. It won't.

## Interview Questions
- **Q: What is the "Lost in the Middle" phenomenon in LLMs?**
  - A: It is the degradation of recall accuracy for information located in the middle of a large context window, whereas information at the very beginning or end is recalled with high accuracy.
- **Q: How would you prevent a ReAct agent from exceeding its context window on a long-running task?**
  - A: Implement observation truncation for large tool outputs, and use a rolling summarization strategy to compress older steps while keeping the system prompt and recent steps intact.

## Further Reading
- [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172) — Research paper on context window recall degradation.
