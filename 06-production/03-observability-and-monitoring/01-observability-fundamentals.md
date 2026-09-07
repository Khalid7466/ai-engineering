# Observability Fundamentals

## TL;DR
Observability in LLM systems requires a paradigm shift from traditional software monitoring. Because LLMs are non-deterministic, probabilistic, and incur highly variable costs per request, traditional APM metrics (like CPU usage and raw HTTP latency) are insufficient. LLM observability demands tracking token consumption, Time-to-First-Token, tool execution traces, and qualitative evaluations (like hallucination rates) to understand system health.

---

## Why Traditional Monitoring Fails

If you deploy a standard microservice, you monitor three main signals: **Error Rate, Latency, and Throughput**. If latency spikes or error rates jump to 5%, an alert fires, and you roll back the deployment.

If you deploy an LLM agent, these metrics tell you almost nothing about the user experience:
- **"Errors" are silent:** A hallucinated response returns an HTTP 200 OK. The model didn't crash; it just confidently lied.
- **Latency is relative:** An HTTP response that takes 10 seconds is a disaster for a traditional API. For an LLM generating a 1,000-word essay, 10 seconds is exceptionally fast.
- **Costs are per-request:** An infinite loop in a standard app wastes cheap CPU cycles. An infinite loop in an LLM agent calling a tool repeatedly costs real API dollars instantly.

## The Pillars of LLM Observability

To achieve true observability in production AI, you must capture three distinct layers of data:

### 1. Traces and Spans (The Execution Path)
Agents and RAG pipelines perform multiple steps before returning an answer. A trace captures the entire lifecycle of a request.
If a user asks, "What's my balance?", the trace must capture:
- Span 1: The embedding of the query.
- Span 2: The Vector DB retrieval (and which documents were returned).
- Span 3: The LLM deciding to call the `get_balance` tool.
- Span 4: The Python execution of the tool.
- Span 5: The final LLM generation.

Without distributed tracing, debugging *why* an agent gave a wrong answer is impossible. 

### 2. LLM-Specific Metrics (Telemetry)
Instead of raw latency, production systems track:
- **TTFT (Time to First Token):** How fast does the user see the first word? This dictates perceived performance.
- **Tokens per Second (Throughput):** How fast does the model generate text once it starts?
- **Token Usage (Cost):** Granular tracking of input/output tokens tagged by `user_id`, `feature`, and `model`.

### 3. Qualitative Evaluations (Evals)
Because errors are often logical rather than technical, observability pipelines must evaluate the *quality* of the output. 
This is often done asynchronously by running smaller "Judge" LLMs over a sample of production logs to score them on:
- **Faithfulness:** Did the answer rely strictly on the retrieved context? (Hallucination check).
- **Answer Relevance:** Did the output actually answer the user's question?
- **Toxicity:** Did the model generate harmful content?

## The Observability Stack

A modern AI engineering stack typically involves instrumenting the application code (using standards like OpenTelemetry or SDKs from specific platforms) and sending the data to a specialized observability platform.

- **LangSmith / Langfuse:** Deeply integrated with orchestration frameworks (like LangChain or LlamaIndex) for complex agent tracing.
- **Helicone / LiteLLM:** Proxy-based solutions. You route your OpenAI calls through their proxy, and they automatically log costs, latency, and tokens without changing your core application logic.
- **Arize Phoenix:** Focused heavily on the evaluation and ML-ops side (drift, hallucination detection).

## Production Implications

Without robust observability, you are flying blind. When an executive asks, "Why did our OpenAI bill double this month?" or a customer complains, "The bot gave me the wrong price," you need the ability to pull up the exact trace. 

In the [Banking Post-Mortem](../use-case.md), the engineering team caught the prompt injection attack not because the application crashed, but because their observability platform fired an alert on a sudden spike in "Tool Access Denied" spans for a specific user ID.

## Common Mistakes

- **Logging prompts to standard stdout:** Traditional log aggregators (Splunk, Datadog) truncate long multi-line strings. An 8,000-token prompt logged to a standard JSON log will be unreadable. You need specialized tools built for wide textual data.
- **Ignoring privacy:** Logging every user prompt and response in plain text to a dashboard means your engineers have access to user PII. Production tracing often requires scrubbing sensitive data before it reaches the observability platform.
- **Focusing on total latency over TTFT:** Panicking because average response times are 5 seconds, without realizing that TTFT is 0.5 seconds and the users are happily reading the streaming text as it generates.

## Interview Questions

**Q: Why is HTTP status 500 an insufficient metric for tracking the failure rate of an LLM application?**
**A:** LLMs rarely fail via standard system crashes (500s). The most critical failures—hallucinations, prompt injections, and off-topic ramblings—result in a successful HTTP 200 response. You must use qualitative evaluations and user-feedback loops to measure true failure rates.

**Q: If you have a multi-agent system where Agent A passes a task to Agent B, how do you debug a bad final output?**
**A:** By implementing distributed tracing. Every request requires a unique `trace_id` that is passed through the entire system. I would look at the trace in an observability tool (like Langfuse) to inspect the inputs and outputs of every single sub-step (spans) to identify exactly where the bad data was introduced—whether it was a bad vector retrieval or Agent A passing incorrect parameters to Agent B.

## Further Reading
- → See [02-traces-and-spans.md](02-traces-and-spans.md) for a deep dive into OpenTelemetry and trace structures.
- → See [03-llm-specific-metrics.md](03-llm-specific-metrics.md) for the exact SLOs you should set.
