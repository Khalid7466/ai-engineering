# Code-Level Guardrails

## TL;DR
Code-level guardrails are deterministic software patterns (like Python interceptors, regex filters, and allow/deny lists) that sit *around* the LLM. Unlike prompt-level guardrails which are probabilistic suggestions, code-level guardrails are hard boundaries. They enforce security by ensuring that the LLM's inputs and outputs are validated before they reach the user or affect external systems.

---

## The Principle of Deterministic Boundaries

Because LLMs are non-deterministic, you cannot trust them to enforce their own rules reliably. The golden rule of production AI engineering is: **Never let an LLM make an irreversible decision or access sensitive data without a deterministic code-level check.**

Code-level guardrails typically exist in three places within an LLM architecture:
1. **Input Interceptors:** Scanning the user's prompt or retrieved data before it reaches the model.
2. **Output Interceptors:** Scanning the model's response before it is sent to the user.
3. **Action/Tool Interceptors:** Validating the parameters of a tool call before executing it.

## Types of Code-Level Guardrails

### 1. Output Filtering (Regex and Heuristics)
The simplest and fastest code-level guardrails use standard string manipulation and regular expressions to catch known bad outputs.

```python
import re

def filter_output(llm_response: str) -> str:
    # Deterministic block: Prevent the model from outputting AWS keys
    aws_key_pattern = re.compile(r'(?i)AKIA[0-9A-Z]{16}')
    if aws_key_pattern.search(llm_response):
        # Log the incident, alert security
        raise SecurityException("Sensitive credential detected in output.")
    return llm_response
```

### 2. Tool and Action Whitelisting
When building Agents (LLMs with tools), the model outputs JSON representing a function call. Code-level guardrails must validate these parameters independently.

**Vulnerable Approach:**
```python
# Trusting the model's output entirely
def execute_query(llm_tool_call):
    db.execute(llm_tool_call.arguments["sql_query"])
```

**Production Approach:**
```python
# Code-level guardrail: Whitelisting actions
def execute_query(llm_tool_call):
    query = llm_tool_call.arguments["sql_query"].upper()
    
    # Deterministic check: Only allow SELECT statements
    if not query.startswith("SELECT") or "DROP" in query or "UPDATE" in query:
        return "System Error: Only read operations are permitted."
    
    return db.execute(query)
```

### 3. Contextual Authorization
If an LLM has access to a tool like `get_user_profile(user_id)`, the LLM might be tricked into passing a `user_id` belonging to someone else. The code-level guardrail must enforce authorization using the application's secure context (like a JWT), not the model's output.

```python
def safe_get_profile(requested_user_id, secure_session):
    # Guardrail: Cross-reference request with deterministic session data
    if requested_user_id != secure_session.user_id:
        return "Error: You can only access your own profile."
    
    return api.get_profile(requested_user_id)
```

## Advanced Guardrails: LLM-as-a-Judge

Sometimes, a rule is too complex for regex (e.g., "Do not give medical advice"). In these cases, production systems use a *secondary, isolated LLM* as a code-level guardrail. 

1. Main LLM generates response `R`.
2. Code pauses execution.
3. A smaller, faster model (the Judge) is prompted: "Is response `R` giving medical advice? Answer only YES or NO."
4. If YES, the code intercepts and returns a safe fallback string.

While this uses an LLM, it is structurally a code-level guardrail because the primary LLM cannot bypass the secondary evaluation.

## Production Implications

Code-level guardrails add latency. If you run a regex over a massive output, or use an LLM-as-a-Judge, you are delaying the Time to First Token (TTFT). Engineering trade-offs must be made between security and user experience. Often, output guardrails are run asynchronously while streaming; if a violation is detected mid-stream, the connection is abruptly killed and the message is redacted on the client side.

## Common Mistakes

- **Relying on the LLM for auth:** Letting the LLM decide if a user has permissions based on the chat context.
- **Failing open on guardrail errors:** If the guardrail service crashes or times out, the system should default to blocking the output, not letting it pass through.
- **Ignoring the retrieved context:** Guardrails must also inspect the context returned by a Vector DB (RAG) before it goes to the model, to prevent indirect prompt injections.
- **Over-filtering:** Using poorly written regex that catches false positives (the Scunthorpe problem), leading to a frustrating user experience.

## Interview Questions

**Q: Explain the difference between a prompt-level guardrail and a code-level guardrail.**
**A:** Prompt-level guardrails are natural language instructions given to the model (e.g., "Don't use profanity"), which are probabilistic and can be bypassed. Code-level guardrails are deterministic logic executed outside the model (e.g., a Python script that checks the output against a profanity dictionary and blocks the API response), which cannot be bypassed by manipulating the model.

**Q: How would you secure an LLM agent that has access to a company's internal Slack API?**
**A:** I would implement strict code-level tool interceptors. First, a whitelist of allowed API endpoints (only `chat.postMessage`, no `admin.users.delete`). Second, contextual authorization to ensure the agent can only post to channels the requesting user is already in. Third, an output filter to scan the drafted message for PII before the API call is executed.

## Further Reading
- [NeMo Guardrails by NVIDIA](https://github.com/NVIDIA/NeMo-Guardrails) — Open-source toolkit for adding programmable guardrails to LLM applications.
- → See [03-prompt-injection.md](03-prompt-injection.md) for attacks that these guardrails are designed to stop.
