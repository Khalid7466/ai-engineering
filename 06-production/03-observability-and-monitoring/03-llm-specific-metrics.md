# LLM-Specific Metrics

## TL;DR
Standard software metrics (CPU, Memory, Request Latency) are insufficient for managing LLMs in production. AI engineering requires a specialized set of metrics centered around token economics (cost and throughput), latency perception (TTFT), and qualitative behavior (hallucination rates, tool success). Establishing Service Level Objectives (SLOs) for these specific metrics is how you ensure a stable, cost-effective product.

---

## Latency Metrics (The User Experience)

In a traditional API, latency is measured from request sent to response received. In an LLM streaming response, latency is broken down into phases.

### 1. TTFT (Time To First Token)
The time elapsed from when the user hits "Send" to when the first token appears on their screen.
- **Why it matters:** TTFT is the primary driver of perceived performance. If TTFT is < 1 second, users perceive the bot as fast, even if the total generation takes 10 seconds. If TTFT > 3 seconds, users assume the system is broken and may abandon the page.
- **SLO Target:** p95 < 1000ms.

### 2. TBT (Time Between Tokens) / Token Latency
The average time it takes the model to generate subsequent tokens after the first one.
- **Why it matters:** It dictates the "reading speed" of the stream. If TBT is 100ms, the model generates 10 tokens per second (slower than a human reads). If TBT is 20ms, it generates 50 tokens per second (smooth, fast reading).
- **SLO Target:** TBT < 30ms (yielding >30 tokens/sec).

### 3. Total Latency
The total time to complete the request. This is highly correlated with output length and is less useful for streaming, but critical for offline batch processing or synchronous API calls.

## Throughput and Cost Metrics (The Economics)

### 4. Token Throughput (Tokens per Second)
Measured at the infrastructure level. How many total tokens is the GPU generating per second across *all* concurrent requests?
- **Why it matters:** This indicates hardware utilization. A low token throughput with high user load means your batching strategy (see → [04-batching-strategies.md](../02-cost-optimization/04-batching-strategies.md)) is failing or the GPU is memory-bound.

### 5. Cost-per-Query (CPQ)
Calculated dynamically by multiplying the input tokens and output tokens of a request by the specific model's pricing tier.
- **Why it matters:** Averages hide spikes. If 90% of queries cost $0.001 but 10% of queries trigger massive agentic loops costing $0.50, your unit economics are broken. CPQ must be tracked per feature and per user.

### 6. Cache Hit Rate
The percentage of requests answered by the Semantic Cache or Exact Match cache without invoking the LLM.
- **SLO Target:** Varies by domain, but > 30% for FAQ-style bots is a strong indicator of a healthy caching layer.

## Qualitative Metrics (The Output Integrity)

These metrics cannot be measured deterministically. They require asynchronous evaluation pipelines (LLM-as-a-judge) or user feedback.

### 7. Faithfulness / Hallucination Rate
The percentage of outputs where the model generated facts not present in the retrieved context.
- **How to measure:** Run a daily batch job where a smaller model evaluates a sample of logs: *Did output Y rely entirely on context X?*

### 8. Tool-Call Success Rate
In agentic workflows, the percentage of time the LLM outputs a perfectly formatted JSON tool call that executes without throwing a validation or schema error.
- **Why it matters:** A 99% success rate means stable agents. A 70% success rate means the model is struggling to understand the tool schema, causing retries, latency, and wasted tokens.

### 9. User Acceptance Rate (Implicit/Explicit)
Explicit: Thumbs up / Thumbs down clicks on responses.
Implicit: Did the user copy the generated code? Did the user immediately regenerate the response? Did the user close the chat and open a human support ticket?

## Production Implications

You cannot optimize what you do not measure. If you only track total latency, you might try to optimize it by using a smaller model, which ruins output quality. If you track TTFT, you might realize you can keep the high-quality model but implement Prefix Caching to hit your speed targets.

Furthermore, these metrics are used for **Capacity Planning**. If you know your peak Token Throughput is nearing the theoretical limit of your self-hosted vLLM instance, it is time to spin up another GPU node before TTFT degrades.

## Common Mistakes

- **Measuring generation speed by characters/sec instead of tokens/sec:** Tokens vary in length. Standardize on tokens to compare model efficiency accurately.
- **Ignoring p99 TTFT:** Looking only at average TTFT. Averages hide the 1% of users experiencing 15-second TTFTs due to queueing delays during traffic spikes.
- **Treating all tools equally:** Grouping tool-call success rates globally. You must track success rates *per tool*. The model might format `get_weather()` perfectly 100% of the time, but fail at `update_database_schema()` 50% of the time.

## Interview Questions

**Q: In a streaming LLM application, why is Time to First Token (TTFT) a more critical metric than Total Latency?**
**A:** Because TTFT determines the perceived responsiveness of the application. Once the first token arrives, the user begins reading, masking the ongoing generation time. Total latency is heavily dependent on the output length, making it an unreliable metric for system responsiveness.

**Q: How would you monitor the hallucination rate of a production RAG system?**
**A:** Since hallucinations cannot be detected by standard APMs, I would implement an asynchronous evaluation pipeline. We log the user prompt, retrieved context, and the LLM's response. A scheduled job uses an LLM-as-a-Judge to evaluate a random sample of these logs, checking if the response is strictly supported by the context, and reports the aggregate "faithfulness score" to a dashboard.

## Further Reading
- [Evaluating LLM Applications](https://docs.smith.langchain.com/evaluation) — LangSmith's guide on implementing qualitative metrics in production.
- → See [05-alerting-and-dashboards.md](05-alerting-and-dashboards.md) for how to act on these metrics.
