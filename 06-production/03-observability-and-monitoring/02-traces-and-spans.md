# Traces and Spans

## TL;DR
In production LLM applications, a single user request rarely maps to a single API call. RAG pipelines and autonomous agents execute complex, multi-step workflows involving databases, APIs, and multiple LLM inferences. **Traces and Spans** (built on standards like OpenTelemetry) provide a hierarchical, visual breakdown of these workflows, allowing engineers to pinpoint exactly where an error, hallucination, or latency bottleneck occurred.

---

## The Anatomy of a Trace

A **Trace** represents the entire journey of a single execution (e.g., a user submitting a chat message). 
A trace is composed of a tree of **Spans**. A Span represents a single unit of work within that trace, complete with a start time, end time, and metadata.

### Example: A RAG Agent Trace
When a user asks: "Summarize the latest financial report," the trace might look like this:

```text
[Trace] User Chat Request (Total Latency: 3.2s)
├── [Span] Intent Classification LLM (0.4s)
│   └── Metadata: model="gpt-3.5-turbo", tokens=120, intent="data_retrieval"
├── [Span] Vector DB Retrieval (0.2s)
│   └── Metadata: db="pinecone", top_k=3, query="financial report Q3"
├── [Span] Tool Execution: Fetch PDF (0.6s)
│   └── Metadata: tool="s3_fetch", doc_id="doc_789"
└── [Span] Final Generation LLM (2.0s)
    └── Metadata: model="claude-3-opus", prompt_tokens=4500, output_tokens=300
```

Without this structure, if the request takes 3.2 seconds or returns a bad answer, you have no idea which of the four steps caused the issue. With traces, you can immediately see the breakdown.

## OpenTelemetry and LLMs

Historically, AI frameworks (like LangChain) built proprietary tracing systems. Today, the industry is standardizing on **OpenTelemetry (OTel)**, the open standard for observability. 

OTel defines specific **Semantic Conventions** for LLMs. This means that a span representing an LLM call will consistently contain standard attributes, such as:
- `llm.request.model`: e.g., "gpt-4"
- `llm.usage.input_tokens`: e.g., 500
- `llm.usage.output_tokens`: e.g., 250
- `gen_ai.prompt.0.content`: The actual text of the system prompt.

By adhering to OTel standards, you avoid vendor lock-in. You can emit traces from your Python code and view them in Datadog, Honeycomb, Langfuse, or Arize Phoenix interchangeably.

## Injecting Context (Distributed Tracing)

In microservice architectures, the retrieval service might live on Server A, and the LLM generation service on Server B. 
To connect them into a single trace, you must implement **Context Propagation**. The initial entry point generates a `trace_id`. This ID is injected into the HTTP headers and passed to every subsequent service. Each service attaches its spans to that parent `trace_id`.

## Debugging with Spans

Spans are critical for debugging the two hardest problems in AI Engineering:

### 1. The "Hallucination" Debug
A user reports the bot hallucinated a policy. 
- *Action:* Find the `trace_id` for that session.
- *Investigation:* Look at the `Retrieval Span`. Did the Vector DB return the correct document? 
  - If NO: The embedding/retrieval pipeline is broken. Fix the chunking strategy.
  - If YES: Look at the `Generation Span`. Did the prompt truncate the document? If the document is there, the LLM failed to read it. You need a smarter model or better prompt structuring.

### 2. The "Slow Response" Debug
A user complains the bot is taking 10 seconds to respond.
- *Action:* Open the trace.
- *Investigation:* Are all spans taking long, or is one specific span the bottleneck? You might find the LLM took 1 second, but the internal SQL Tool Span took 9 seconds because of a missing database index. 

## Production Implications

Capturing massive text payloads (inputs and outputs) in every span generates a massive amount of data. 

**Cost and Storage:** In a high-traffic production system, logging every 10,000-token span will bloat your observability database rapidly.
- *Solution:* Implement **sampling**. Record 100% of traces that result in an error or negative user feedback, but only a 5% random sample of successful requests.

**Data Privacy:** Spans often contain PII.
- *Solution:* Instrumentation libraries must run scrubbing functions (like regex masking) on the `gen_ai.prompt` attributes *before* emitting the span to a third-party observability platform.

## Common Mistakes

- **Flat logging:** Logging step 1, step 2, and step 3 as separate log lines without a unified `trace_id`, making it impossible to reconstruct the workflow for concurrent users.
- **Forgetting tool inputs:** Tracing the LLM call, but failing to trace the exact JSON parameters the LLM passed to the tool. 
- **Overhead:** Wrapping highly iterative, microsecond functions (like tokenizing text arrays) in heavy spans, creating massive overhead that actually slows down the application.

## Interview Questions

**Q: Describe the difference between a Trace and a Span.**
**A:** A Trace represents the complete end-to-end execution path of a single transaction (like a user asking a question). A Span represents a specific, timed unit of work within that trace, such as a database query, an API call, or an LLM generation. Spans form a parent-child tree structure to make up the trace.

**Q: You notice your RAG application is returning incorrect answers. How do you use tracing to determine if the fault lies with the LLM or the Vector Database?**
**A:** I would inspect the trace for a failed request. First, I examine the Vector DB retrieval span to see the exact context chunks returned. If the necessary information to answer the question is *missing* from those chunks, the retrieval system is at fault. If the information *is present* in the context chunks, but the LLM span shows an incorrect final output, then the LLM generation step is at fault (it ignored or misunderstood the context).

## Further Reading
- [OpenTelemetry Semantic Conventions for GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — The official documentation for standardizing LLM spans.
- → See [01-observability-fundamentals.md](01-observability-fundamentals.md) for the high-level strategy of monitoring.
