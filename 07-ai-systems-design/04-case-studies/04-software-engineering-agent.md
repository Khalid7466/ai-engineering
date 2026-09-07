<Use Case: Autonomous Software Engineering Agent>
## Objective
An engineering team wants to build an internal tool that can automatically resolve low-priority Jira tickets (e.g., "Update the button color on the login page", "Fix the null pointer exception in the payment webhook"). The system must read the ticket, find the relevant code, write the fix, run the tests, and open a Pull Request.

**Constraints:**
- The codebase is a massive monorepo.
- The system must be able to compile the code and run unit tests.
- The system must never push code to the `main` branch directly.

## Why a Multi-Agent System?
The team initially built a single "Coder Agent" with tools to read files, edit files, and run tests.
- **Why it failed:** The context window became hopelessly polluted. The agent would read a file, edit it, run the tests, see a massive traceback, and then completely forget what the original Jira ticket was about. Furthermore, the agent was terrible at reviewing its own work, often approving code that barely worked.
- **The Pivot:** We implemented a **Multi-Agent System** with strict persona separation. A Coder agent writes the code, a QA agent runs the tests and reviews the diff, and a DevOps agent manages the git operations.

## Technical Decisions

### Decision 1: Tool Isolation per Agent
- **Chose:** Giving specific tools to specific agents.
- **Rejected:** Giving all tools to one mega-agent.
- **Rationale:** 
  - Coder Agent: `read_file`, `edit_file`, `search_codebase`.
  - QA Agent: `run_test_suite`, `read_diff`.
  - DevOps Agent: `create_branch`, `commit`, `open_pr`.
  By isolating tools, we force the LLMs to stay in character and reduce the cognitive load of selecting from 15 different tools.

### Decision 2: The Handoff Protocol
- **Chose:** Explicit, state-machine driven handoffs (LangGraph).
- **Rejected:** Conversational handoffs (AutoGen).
- **Rationale:** Conversational multi-agent systems are too unpredictable for CI/CD pipelines. We defined a strict state graph: Coder -> QA. If QA fails, it explicitly routes back to Coder with the error payload. If QA passes, it explicitly routes to DevOps. 

### Decision 3: Human Checkpoint
- **Chose:** The system ends by opening a PR for human review.
- **Rejected:** The system merging its own code.
- **Rationale:** No matter how good the AI is, merging directly to `main` without human oversight is a catastrophic risk. The PR acts as the final "Human in the Loop" checkpoint.

## Architecture Walkthrough

```python
# The Multi-Agent State Graph

# Global State shared between agents
class RepoState(TypedDict):
    ticket_description: str
    files_changed: list[str]
    test_results: str
    status: str # "coding", "testing", "pr_ready"

def coder_node(state: RepoState):
    # The Coder agent reads the ticket and edits files
    # It does NOT run tests.
    agent = Agent(tools=[read_file, edit_file], persona="Senior Dev")
    changes = agent.solve(state.ticket_description)
    return {"files_changed": changes, "status": "testing"}

def qa_node(state: RepoState):
    # The QA agent reviews the diff and runs tests
    agent = Agent(tools=[run_test, read_diff], persona="Strict QA")
    feedback = agent.review(state.files_changed)
    
    if feedback.passed:
        return {"test_results": "Pass", "status": "pr_ready"}
    else:
        # Route back to coder with the specific test failures
        return {"ticket_description": f"Fix these errors: {feedback.errors}", "status": "coding"}

def devops_node(state: RepoState):
    # Opens the PR and halts the system
    pr_url = create_pull_request(state.files_changed)
    notify_slack(pr_url)
    return {"status": "done"}

# Execution Graph Definition (Conceptual)
workflow = StateGraph(RepoState)
workflow.add_node("coder", coder_node)
workflow.add_node("qa", qa_node)
workflow.add_node("devops", devops_node)

workflow.add_conditional_edges("qa", 
    lambda state: "devops" if state.status == "pr_ready" else "coder"
)
```

## Lessons Learned

1. **The Infinite Loop of Doom:** The Coder and QA agents would frequently get stuck. QA would say "Test failed, null pointer." Coder would apply a fix. QA would say "Still failed, null pointer." This loop would run until it burned $20 of API credits. We had to implement a strict `max_revisions=3` counter in the state object. If it hits 3, the system aborts, reverts the git branch, and comments on the Jira ticket: "Could not resolve automatically. Human intervention needed."
2. **Editing files is hard:** Giving the LLM a `replace_text` tool often corrupted files because it would miss trailing commas or indentation. We had to implement a specialized `edit_file` tool that allowed the LLM to output a unified diff format, which was then applied via deterministic diff-patching libraries.
3. **The Workspace Sandbox:** You cannot let an AI run arbitrary shell commands on a production CI server. The agents operate inside a tightly restricted, ephemeral Docker container where `rm -rf /` won't destroy company infrastructure.
</Use Case: Autonomous Software Engineering Agent>
