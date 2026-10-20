# LLM APIs and SDKs

## TL;DR
Integrating LLMs into production requires robust engineering around API interactions. Standard REST calls are rarely sufficient due to extreme latencies, rate limits, and the need for streaming. You must choose the right abstractions (SDKs) and handle failures gracefully.

---

## The Standard Payload (ChatCompletions)
Almost all providers (OpenAI, Anthropic, open-source via vLLM) have standardized around the OpenAI ChatCompletions schema. You pass a list of message objects, and receive a response object.

```python
import openai

client = openai.Client()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.7,
)
print(response.choices[0].message.content)
```

## Abstraction Layers: LangChain vs. LiteLLM

As you scale, you will likely need to switch between OpenAI, Anthropic, and open-source models. Hardcoding the OpenAI SDK becomes problematic.

1. **LiteLLM:** The lightweight approach. It provides a universal interface (matching the OpenAI spec) that translates your call to *any* provider (Anthropic, Bedrock, Vertex). It is unopinionated and excellent for routing and cost-tracking.
2. **LangChain / LlamaIndex:** Heavyweight frameworks. They provide massive toolkits for chaining prompts, managing memory, and connecting to vector databases. 
   - *Warning:* LangChain is notorious in production for being overly complex, hard to debug, and brittle. Many senior AI engineers recommend avoiding LangChain in favor of writing pure Python with LiteLLM and Pydantic.

## Streaming
Standard HTTP requests wait for the entire response to be generated before returning. Because LLMs generate auto-regressively, a 1000-word response might take 15 seconds. 
You *must* use Server-Sent Events (SSE) streaming for user-facing applications. This returns tokens as they are generated, reducing Time-To-First-Token (TTFT) from 15 seconds to 0.5 seconds.

```python
# Streaming example
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a story."}],
    stream=True
)

for chunk in response:
    # Print tokens to console as they arrive
    print(chunk.choices[0].delta.content or "", end="")
```

## Resilience and Error Handling
APIs go down. They enforce aggressive rate limits (Tokens Per Minute - TPM, Requests Per Minute - RPM).

1. **Exponential Backoff:** If you hit a 429 (Rate Limit) error, you cannot just retry immediately. You must wait 1 second, then 2, then 4, etc., using libraries like `tenacity`.
2. **Async Generation:** If you need to process 10,000 documents, doing it sequentially in a `for` loop will take days. You must use the `AsyncClient` and `asyncio.gather` to make concurrent requests, carefully managing concurrency limits so you don't instantly trigger rate limits.
3. **Fallbacks:** Use LiteLLM to configure automatic fallbacks. "If OpenAI is down or rate-limited, automatically send the exact same payload to Anthropic."

## Production Implications
- **Timeouts:** LLM APIs can sometimes hang during the pre-fill phase. You must set explicit timeout limits on your HTTP clients, or your server threads will lock up waiting for a response that will never come.
- **Cost Tracking:** In a multi-tenant SaaS app, you must track which user generated which tokens. Use the `usage` object returned in the API response to log prompt and completion tokens to your billing database.

## Common Mistakes
- **Not streaming in the UI:** Forcing the user to stare at a loading spinner for 10 seconds. They will assume the app is broken.
- **Swallowing errors:** Not logging the specific API error codes. A rate-limit error requires a different engineering solution than a content-moderation filter error.

## Interview Questions
- **Q: Why is streaming critical when building user-facing LLM applications?**
  - *A:* Because text generation is auto-regressive and slow. Streaming sends chunks to the client as they are generated, vastly improving perceived performance and Time-To-First-Token.
- **Q: How do you handle rate limits when processing thousands of documents?**
  - *A:* I would use an asynchronous HTTP client to process documents concurrently, combined with an exponential backoff library (like Tenacity) to gracefully retry requests when hitting a 429 error. I might also implement a token bucket algorithm to strictly control the outbound request rate.

## Further Reading
- [LiteLLM Documentation](https://docs.litellm.ai/) - Guide to universal API routing.
- [Tenacity library](https://tenacity.readthedocs.io/en/latest/) - Python library for retry logic.

---
<!-- nav:start -->
[Previous: Model Selection](15-model-selection.md) | [Module Overview](README.md) | [Next: Use Case: Medical Q&A Bot](use-case.md)
<!-- nav:end -->
