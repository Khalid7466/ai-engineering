# API Deployment

## TL;DR
Deploying an LLM application built on managed APIs (like OpenAI, Anthropic, or Azure) requires wrapping those external dependencies in resilient infrastructure. Because you do not control the underlying model servers, your deployment architecture must handle rate limits, network timeouts, and streaming connections gracefully to maintain a stable user experience even when the provider fails.

---

## The OpenAI-Compatible Interface

A standard practice in production AI engineering is standardizing internal APIs to match the OpenAI chat completions schema. 
Even if you route traffic to Anthropic, Google, or a self-hosted Llama model, the internal application logic should interface with a unified proxy (like LiteLLM or a custom Gateway) that accepts and returns OpenAI-formatted JSON.

```json
// The standard schema that decouple logic from providers
{
  "model": "gpt-4",
  "messages": [{"role": "user", "content": "Hello"}],
  "stream": true
}
```
This decouple architecture ensures that swapping a model (see → [06-ab-testing-models.md](../03-observability-and-monitoring/06-ab-testing-models.md)) requires zero changes to the frontend or core application logic.

## Resilience Strategies

When depending on third-party APIs, network instability and provider outages are inevitable. Production systems must implement the following patterns:

### 1. Exponential Backoff and Jitter
LLM providers enforce strict rate limits (Tokens Per Minute and Requests Per Minute). When a `429 Too Many Requests` error is returned, immediately retrying will just result in another 429 and potential IP banning.
- **Backoff:** Wait 1 second, then 2, then 4, then 8 before retrying.
- **Jitter:** Add random variance (e.g., 2.3 seconds, 4.1 seconds) to the backoff. If 100 concurrent requests hit a rate limit, jitter prevents the "thundering herd" problem where all 100 requests retry at the exact same millisecond.

### 2. Provider Fallbacks
If OpenAI goes down entirely (returning 5xx errors), the gateway should automatically route the request to a secondary provider (e.g., Anthropic or an Azure OpenAI instance in a different region). 
This requires mapping system prompts and tool schemas on the fly, which is complex but necessary for high-availability enterprise applications.

### 3. Timeout Handling
LLM generation times vary wildly. A request might take 200ms or 20 seconds. 
Standard HTTP clients default to a 60-second timeout. If the API hangs, the user is left staring at a spinner for a full minute before an error appears.
- **Action:** Set aggressive timeouts for the *connection* phase (e.g., 3 seconds) to fail fast if the provider is down, but set longer timeouts for the *read* phase to allow for long generations.

## Streaming Architecture

Because LLM generation is slow, waiting for the entire response to finish before returning it to the user results in an unacceptable TTFT (Time to First Token). 
Production deployments almost universally use **Server-Sent Events (SSE)** or **WebSockets** to stream tokens to the client as they are generated.

**The Streaming Challenge:**
When streaming, the HTTP status code is sent immediately (usually 200 OK) before the first token is generated. 
If the LLM encounters an error or triggered a guardrail *mid-generation*, you cannot change the HTTP status code to 500. 
- **Solution:** The application must emit a specific `error` event in the SSE stream, and the frontend must be programmed to catch that specific event, clear the partial text, and render an error state.

## Rate Limiting Users

In addition to handling provider rate limits, you must enforce rate limits on your own users to prevent a single bad actor (or runaway script) from exhausting your corporate API budget.
- **Tiered Limits:** Free users get 10 requests/hour; paid users get 100.
- **Token-Based Limits:** Standard API limits count *requests*. In LLM apps, you should rate-limit based on *tokens consumed*, ensuring a user sending massive 100,000-token RAG queries is throttled faster than a user sending 10-token queries.

## Common Mistakes

- **Sync HTTP calls in web servers:** Blocking a Python WSGI worker thread (like Gunicorn/Flask) while waiting 10 seconds for an OpenAI response. Under high load, all workers will block, and the entire web server will crash. You must use asynchronous frameworks (FastAPI, Node.js) for LLM deployments.
- **Failing to catch stream interruptions:** If the network drops mid-stream, the frontend might display half a sentence without realizing it's incomplete. 
- **Hardcoding API keys:** Embedding provider keys in frontend code or lambda functions. Keys must reside in a secure backend gateway.

## Interview Questions

**Q: Explain the "Thundering Herd" problem in the context of LLM API rate limits and how to solve it.**
**A:** If an API provider enforces a rate limit and rejects 50 concurrent requests simultaneously, and the application uses standard retries, all 50 requests will retry at the exact same moment a second later, immediately triggering the rate limit again. This is solved by using Exponential Backoff with Jitter—adding random time variance to the retry logic so the retries are staggered, allowing the provider to process them cleanly.

**Q: Why must you use asynchronous web frameworks (like FastAPI) instead of synchronous ones (like basic Flask or Django) when deploying LLM APIs?**
**A:** LLM API calls have exceptionally high latency (often 5-15 seconds). A synchronous web server assigns one worker thread per request. If 10 users query the LLM simultaneously, 10 threads sit idle waiting for the network response. This quickly exhausts the worker pool, causing the server to reject all new connections and effectively crash. Async frameworks allow a single thread to handle thousands of concurrent network waits.

## Further Reading
- [OpenAI API Reference - Streaming](https://platform.openai.com/docs/api-reference/streaming) — Understanding SSE structure.
