# Agentic UX

## TL;DR
Agentic UX is the design of interfaces for autonomous AI. Because agents take time to think and can take destructive actions, the UI must shift from a traditional "chat" interface to one emphasizing progress visibility, Human-in-the-Loop (HITL) approvals, and state management.

---

## Human-in-the-Loop (HITL) Patterns
You cannot trust a v1 agent to drop a production database table or send an email to a client autonomously. 
- **The Approval Workflow:** When an agent decides to use an "unsafe" tool, it pauses execution and sends a request to the UI.
- **UX Implementation:** The user sees a card: `Agent wants to execute: DELETE FROM users WHERE id=5`. The user has two buttons: **Approve** or **Reject & Modify**. If rejected, the human feedback is sent back to the agent as an observation.

## Streaming Agent Outputs
Agents are slow. A complex ReAct loop might take 45 seconds before it produces the final answer. If the UI is just a loading spinner, the user will assume the app crashed.
- **Stream Thoughts:** Stream the agent's intermediate steps to the UI (e.g., "Searching Wikipedia...", "Reading document A...", "Calculating totals...").
- **Collapsible Logs:** Provide a clean summary to the user, but allow technical users to expand a "Dev Mode" to see the raw JSON tool calls and thought processes.

## Shifting from Chat to Artifacts
The standard ChatGPT interface (text bubbles) is poor for agentic work. If an agent writes a 500-line React component, dumping it into a chat bubble is unreadable.
- **Artifacts / Workspaces:** When the agent generates code, a document, or a chart, it should render in a dedicated, persistent UI pane next to the chat. The user can interact with the artifact, and the chat becomes just the command-and-control channel.

## Production Implications
Poor Agentic UX causes users to abandon the system. If they don't know what the agent is doing, they lose trust. If the agent makes a mistake silently, it causes damage. In production, building the UX for a multi-agent system often takes more engineering effort than writing the agent backend prompts.

## Common Mistakes
- **The Infinite Spinner:** Making the user wait 60 seconds with no intermediate feedback.
- **All-or-Nothing Autonomy:** Failing to implement granular HITL. Asking the user to approve *every* safe read operation is annoying; never asking for approval on write operations is dangerous.
- **Chatbot UI for everything:** Forcing complex data tables or multi-file code edits into a narrow chat interface.

## Interview Questions
- **Q: What is Human-in-the-Loop (HITL) and when is it strictly necessary?**
  - A: HITL is a pattern where the agent pauses and requests human approval before continuing. It is strictly necessary for any irreversible or high-risk action, such as executing financial transactions, sending external emails, or modifying production databases.
- **Q: How do you handle UI latency for an agent task that takes 2 minutes?**
  - A: By streaming intermediate progress indicators (thoughts, tool execution statuses) to the UI so the user understands the agent is actively working on the problem.

## Further Reading
- [Anthropic: Human in the Loop](https://docs.anthropic.com/en/docs/human-in-the-loop) — Guidelines on building safe, interactive AI systems.
