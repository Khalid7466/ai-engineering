# Agent Communication and State

## TL;DR
Multi-agent systems require a method for passing information between agents. The two primary paradigms are Shared State (a central object updated by all agents) and Message Passing (agents sending discrete messages to each other). Designing clean handoffs is critical to preventing token bloat.

---

## Message Passing vs Shared State

### Shared State (The Graph Approach)
Used heavily in frameworks like LangGraph. The system maintains a global `State` object (e.g., a Python dictionary). 
When `Agent A` runs, it reads the `State`, performs its task, and *updates* the `State` (e.g., appending a string to `state["research_notes"]`). When `Agent B` runs, it reads the updated global `State`.
- **Pros:** Highly structured, easy to visualize as a state machine.
- **Cons:** If not careful, the state grows massively, blowing out the context window when passed to the next agent.

### Message Passing (The Conversation Approach)
Used in frameworks like AutoGen or CrewAI. Agents communicate by sending text messages to each other, exactly like humans in a Slack channel.
- **Pros:** Feels intuitive. Great for debate or collaborative problem-solving.
- **Cons:** Hard to extract structured data. It's difficult to know when the "conversation" is actually finished.

## The Handoff (Context Transfer)
When Agent A finishes and hands control to Agent B, *what exactly is passed?*
**Anti-Pattern:** Passing the entire ReAct trace of Agent A. Agent B does not need to see the 15 failed SQL queries Agent A tried. It only needs the final data.
**Best Practice:** Agent A must summarize its findings into a predefined schema before handoff. 

## Defining the Interface
Treat agent-to-agent communication like microservice architecture. 
If the `ResearchAgent` calls the `DraftingAgent`, it should use a tool call:
```json
{
  "tool_name": "transfer_to_drafter",
  "arguments": {
    "key_facts": ["Fact 1", "Fact 2"],
    "tone": "professional"
  }
}
```
This forces the LLM to distill its context into strict arguments before the control flow switches.

## Production Implications
In a distributed cloud environment, agents might be running on different servers. Message passing is usually implemented using asynchronous queues (like Kafka, Redis, or RabbitMQ). If an agent is waiting for a response from a peer, it should not block the HTTP thread. It should suspend its state and wake up when the message arrives on the queue.

## Common Mistakes
- **The "Reply All" Problem:** In chat-based frameworks, broadcasting every message to every agent in the swarm, rapidly burning tokens and causing agents to hallucinate responses to messages meant for someone else.
- **Context Bloat:** Passing the entire raw chat history during a handoff instead of a distilled summary.

## Interview Questions
- **Q: What is the difference between Shared State and Message Passing in multi-agent systems?**
  - A: Shared State relies on a central data object that agents sequentially read and modify. Message Passing relies on agents sending discrete conversational messages directly to one another.
- **Q: Why is passing a full ReAct trace during an agent handoff a bad idea?**
  - A: Because it wastes tokens and pollutes the receiving agent's context window with irrelevant trial-and-error details. Handoffs should pass distilled, structured summaries.

## Further Reading
- [OpenAI: Swarm](https://github.com/openai/swarm) — Educational framework exploring lightweight, stateless multi-agent handoffs.
