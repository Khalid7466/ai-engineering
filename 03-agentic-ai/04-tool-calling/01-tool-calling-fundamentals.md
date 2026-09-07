# Tool Calling Fundamentals

## TL;DR
Tool calling (or function calling) is the mechanism by which an LLM interacts with the outside world. The LLM does not execute code; instead, it generates a structured JSON object representing a function signature. Your application code parses this JSON, executes the actual function, and returns the result back to the LLM.

---

## How the LLM 'Calls' a Tool
When people say "the AI searched the web," it is technically a misnomer. The LLM cannot make HTTP requests. 
The actual flow is:
1. **System Prompt:** You provide the LLM with a list of available tools formatted as JSON schemas.
2. **LLM Decision:** Based on the user prompt, the LLM outputs a special response indicating "I want to call `search_web` with the argument `query='AI news'`".
3. **Execution:** Your application intercepts this response, pauses the LLM, and runs the actual `search_web("AI news")` Python/Node function.
4. **Return:** Your application takes the text result of that function, appends it as a new "Tool Message" in the chat history, and calls the LLM again.

## The Tool Schema
A tool schema defines what the tool does and what arguments it requires. It usually consists of a `name`, a `description`, and `parameters` (typically defined using JSON Schema).

```json
{
  "name": "get_current_weather",
  "description": "Get the current weather in a given location. Use this when the user asks about the weather.",
  "parameters": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "The city and state, e.g., San Francisco, CA"
      },
      "unit": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"]
      }
    },
    "required": ["location"]
  }
}
```

## Why Description Quality Matters
The most critical part of the schema is the `description`. The LLM uses the description to decide *whether* to use the tool and *how* to formulate the arguments. 
- **Bad:** `description: "Fetches user data."` (When should it be used? What does it return?)
- **Good:** `description: "Fetches a user's billing history by UUID. Use this ONLY after you have obtained the user's UUID using the search_user tool."`

## Parallel Tool Calls
Modern LLMs support parallel tool calling. If a user asks, "What is the weather in New York, London, and Tokyo?", the LLM can output three distinct tool call JSONs in a single response. Your application should execute all three concurrently and return the array of results, dramatically reducing latency.

## Production Implications
The primary production issue with tool calling is hallucination of arguments or completely fabricated tool names. If your schema is too complex, the LLM will provide string values for integer fields, or omit required parameters. In production, you must use a robust validation layer (like Pydantic in Python) to catch these errors and feed the validation error back to the LLM so it can correct itself, rather than crashing the application.

## Common Mistakes
- **Overloading schemas:** Giving a single tool 15 optional parameters. LLMs struggle with highly complex schemas; it is better to break them into smaller, focused tools.
- **Assuming execution:** Forgetting that the developer must write the code to execute the tool. The LLM only generates the JSON.
- **Poor descriptions:** Writing tool descriptions meant for developers instead of descriptions optimized for the LLM's routing logic.

## Interview Questions
- **Q: Describe the lifecycle of a tool call in an AI agent.**
  - A: The LLM receives available tool schemas -> LLM outputs a structured JSON requesting a tool -> Application code parses the JSON -> Application executes the local function -> Application appends the result to the message history -> Application calls the LLM again.
- **Q: How does the LLM know which tool to use?**
  - A: It relies entirely on the semantic meaning of the tool's `name` and the natural language `description` provided in the tool schema.

## Further Reading
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling) — The official documentation on function calling mechanics.
