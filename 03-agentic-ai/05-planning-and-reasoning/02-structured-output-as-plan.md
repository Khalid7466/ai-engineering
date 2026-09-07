# Structured Output as Plan

## TL;DR
By forcing an LLM to output its plan as a strictly typed JSON object (like a Pydantic model) rather than free-form text, you eliminate tool-call hallucination and make agent routing predictable. This pattern is often called the `QueryPlanContract`.

---

## The Problem with Free-Form Planning
If you ask an LLM to plan, it might output:
```text
I will first use the search tool to find the user's ID, then I will look up their billing history.
```
Your application code cannot easily parse this text to execute the tools. You would have to use fragile Regex or another LLM call to extract the tool names.

## The QueryPlanContract Pattern
Instead of free text, you define a strict schema that represents a plan.
```python
from pydantic import BaseModel, Field

class Step(BaseModel):
    tool_name: str
    arguments: dict
    dependency: list[int] = Field(description="Which previous steps this depends on")

class QueryPlanContract(BaseModel):
    confidence_score: float = Field(description="0.0 to 1.0 confidence that this plan will work")
    reasoning_trace: str = Field(description="Step-by-step logic explaining the plan")
    steps: list[Step]
```

When the user provides a query, you force the LLM (using JSON Mode or Structured Outputs / Function Calling) to return exactly this JSON structure. 

## Preventing Hallucination
Because the LLM is constrained by the JSON schema (and modern APIs like OpenAI's `response_format` guarantee schema adherence), it cannot hallucinate a tool call in a weird text format. Your application code can simply deserialize the JSON and iterate through the `steps` array, executing tools deterministically.

## The Confidence Score + Reasoning Trace
Notice the `confidence_score` and `reasoning_trace` fields in the schema.
- **Reasoning Trace:** You *must* put this field *before* the `steps` array in the JSON schema. This forces the LLM to generate its Chain of Thought *before* it generates the tool calls, vastly improving the accuracy of the chosen tools.
- **Confidence Score:** Allows your application to implement thresholds. If the agent returns a plan with `confidence_score: 0.3`, your app can intercept it and say to the user, "I'm not sure how to do this, can you clarify?" rather than attempting a risky action.

## Production Implications
Structured outputs are the bridge between probabilistic LLMs and deterministic software engineering. Without strict schema contracts, your agent application will crash constantly with `JSONDecodeError` or `KeyError` when the LLM decides to change its output format. Always use Structured Outputs (or robust constrained generation like Outlines/Guidance) for the planning phase.

## Common Mistakes
- **Putting the array first:** If your JSON schema puts the `steps` array before the `reasoning_trace` string, the LLM will generate the actions *before* it thinks, completely negating the benefit of Chain of Thought.
- **Trusting the output blindly:** Even with structured output, the LLM might hallucinate a valid JSON structure with an *invalid tool name* (e.g., `tool_name: "magic_button"`). You must still validate the tool name against your registry.

## Interview Questions
- **Q: Why should the `reasoning` field appear before the `action` field in a structured JSON response?**
  - A: Because LLMs are autoregressive (predicting the next token based on previous tokens). Writing out the reasoning first acts as a scratchpad, helping the model calculate the correct action. If the action comes first, the reasoning is just a post-hoc justification for an unthoughtful action.

## Further Reading
- [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs) — Official guide on enforcing strict JSON schemas.
