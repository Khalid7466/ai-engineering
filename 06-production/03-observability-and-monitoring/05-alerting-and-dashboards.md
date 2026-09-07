# Alerting and Dashboards

## TL;DR
Dashboards visualize the health of an LLM system, while alerts proactively notify engineers when that health degrades. Because LLMs fail in unique ways (cost spikes, high hallucination rates, API rate limits), production alerting requires thresholds and anomaly detection tailored to token economics and probabilistic outputs, integrated deeply with incident management tools like PagerDuty.

---

## Designing the LLM Dashboard

A production dashboard should answer three questions immediately upon loading:
1. Is the system fast? (Latency)
2. Is the system safe/accurate? (Quality)
3. Are we burning cash? (Cost)

### Core Dashboard Panels
- **Time to First Token (TTFT) p95 & p99:** A line chart tracking responsiveness. Spikes indicate queueing issues on self-hosted infrastructure or provider-side delays.
- **Cost per Hour & Daily Spend Run-Rate:** A bar chart of total token cost.
- **Error Rate by Type:** A pie chart separating HTTP 5xx errors (infrastructure) from 429s (rate limits) and Application Errors (tool execution failures).
- **Evaluation Scores (Moving Average):** A line chart showing the asynchronous evaluation scores (e.g., Faithfulness, Answer Relevance) to detect slow degradations in model quality over time.
- **Cache Hit Ratio:** A gauge showing the percentage of requests served by the semantic cache.

## What to Alert On (And How to Set Thresholds)

Alert fatigue is a major risk. If you alert on every 5-second request, engineers will start ignoring the channel. Alerts must be actionable.

### 1. Cost Anomalies (The "Infinite Loop" Alert)
Agents can get stuck in loops, repeatedly calling tools and generating massive context windows.
- **Trigger:** Spend rate exceeds $X per hour, OR a single `user_id` consumes > N tokens in a 5-minute window.
- **Action:** PagerDuty alert to the on-call engineer; automated system action to temporarily rate-limit or suspend the offending `user_id`.

### 2. Provider Rate Limits (HTTP 429s)
API providers (OpenAI, Anthropic) enforce strict Tokens-Per-Minute (TPM) limits.
- **Trigger:** `429 Too Many Requests` rate > 2% of total traffic over a 3-minute window.
- **Action:** Verify exponential backoff is functioning. If sustained, request a quota increase or failover to a secondary model/provider (e.g., fallback from Azure OpenAI to direct OpenAI).

### 3. TTFT Degradation
- **Trigger:** p99 TTFT exceeds 3000ms for a sustained 5-minute window.
- **Action:** If self-hosted, this indicates batch saturation; auto-scale a new GPU node. If managed API, check provider status pages for outages.

### 4. Guardrail Intervention Spike
If your code-level guardrails or PII detectors are suddenly blocking a massive number of requests, you are likely under a coordinated prompt injection attack.
- **Trigger:** Guardrail block rate increases by 300% above baseline.
- **Action:** Page security team. Investigate the trace logs for adversarial prompts or compromised RAG documents.

## Avoiding Alert Fatigue

LLM APIs exhibit natural variance. A single query taking 15 seconds is normal if it requires generating 2,000 tokens of code. 

**Best Practices:**
- **Use percentiles, not averages:** Alert on p99 or p95, never on the average (which hides outliers) or the maximum (which triggers on expected one-off long generations).
- **Use burn-rate alerting:** Instead of alerting the moment an error occurs, alert if the error rate consumes a significant portion of your monthly error budget (e.g., "Error rate is 5x the baseline for 10 minutes").
- **Separate Severity:**
  - *Sev 1 (Page at 3 AM):* API provider is down, hard crash, massive data leak detected.
  - *Sev 3 (Slack message during business hours):* Hallucination rate crept up by 2% this week, semantic cache hit rate dropped below 15%.

## Production Implications

Effective alerting requires the observability platform (like LangSmith or Datadog) to have deep integrations with notification systems (PagerDuty, Opsgenie, Slack). 

In modern architectures, alerts are often tied to **automated remediations**. If an alert fires for "OpenAI API Latency > 5s", a web-hook can automatically toggle the application's router to send traffic to Anthropic Claude or a fallback self-hosted model until the alert resolves.

## Common Mistakes

- **Alerting on Total Latency:** Firing alerts because requests take > 10 seconds. In a streaming app, total latency is dictated by output length. A 10-second request is fine if TTFT was 500ms.
- **No cost alerts:** Deploying a multi-step agent without token-spend alerts, leading to thousands of dollars burned over a weekend due to an unexpected recursive logic bug.
- **Alerting on single evaluation failures:** Paging someone because the "Toxicity Evaluator" flagged one message. Evals are probabilistic; alert only on sustained statistical shifts in the failure *rate*.

## Interview Questions

**Q: Why should you configure alerts to monitor HTTP 429 errors specifically in LLM applications?**
**A:** Because LLM providers use strict Tokens-Per-Minute (TPM) rate limits. Unlike standard web APIs where rate limits are request-based, LLM limits can be exhausted rapidly by a small number of users generating massive contexts. Tracking 429s is critical for knowing when to implement fallback models or request quota increases.

**Q: You are building a dashboard for a customer support agent. What are the top three metrics you put on the first row?**
**A:** 1. Time to First Token (TTFT) p95, to ensure the UI feels responsive. 2. Tool-Call Success Rate, to ensure the agent is successfully executing actions (like refunds or database lookups) without formatting errors. 3. Cost-per-Query, to ensure the unit economics of deflecting the human support ticket remain viable.

## Further Reading
- [Site Reliability Engineering (SRE) - Google](https://sre.google/sre-book/monitoring-distributed-systems/) — The foundational concepts of alerting and SLIs/SLOs, which apply directly to AI.
- → See [03-llm-specific-metrics.md](03-llm-specific-metrics.md) for the specific metrics that feed these dashboards.
