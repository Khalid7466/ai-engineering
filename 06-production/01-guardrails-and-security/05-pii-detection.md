# PII Detection and Masking

## TL;DR
Sending Personally Identifiable Information (PII)—like Social Security Numbers, names, or financial data—to external LLM APIs violates data privacy regulations (GDPR, CCPA, HIPAA) and corporate data residency policies. PII detection involves scanning inputs to redact sensitive data before it leaves the corporate network, and scanning outputs to prevent accidental data leaks from the model to the user.

---

## Why PII Matters in LLM Production

When you use managed LLM APIs (like OpenAI, Anthropic, or Gemini), the data you send leaves your infrastructure. Even if the provider promises not to train on API data, transmitting highly sensitive information to a third party is often a violation of compliance frameworks (SOC 2, HIPAA) or regional data residency laws.

Furthermore, in multi-tenant RAG systems, if the retrieval mechanism accidentally pulls in a document containing another user's PII, the LLM might seamlessly incorporate it into the response, causing a massive data breach (see the [Banking Use-Case](../use-case.md)).

## Detection Approaches

Detecting PII in unstructured text is a classic NLP problem that has been adapted for LLM pipelines. Because latency is critical, organizations use a tiered approach, relying on fast deterministic methods first, and slower probabilistic methods second.

### 1. Regex Patterns
The fastest method for standardized PII (Credit Cards, SSNs, phone numbers, emails).
- **Pros:** Microsecond latency, deterministic.
- **Cons:** Extremely rigid. Cannot detect context-dependent PII like a person's name or a physical address.

### 2. Named Entity Recognition (NER) models
Small, specialized NLP models (like spaCy or specialized BERT variants) trained specifically to identify entities like `PERSON`, `ORG`, or `LOC`.
- **Pros:** Fast enough for real-time streaming (usually <50ms latency). Can identify names and addresses in context.
- **Cons:** Requires maintenance; can produce false positives (flagging a company name as a person).

### 3. Microsoft Presidio
[Microsoft Presidio](https://microsoft.github.io/presidio/) is the industry standard open-source framework for PII detection in production. It combines regex, logic checks (like Luhn validation for credit cards), and NER models into a unified, customizable pipeline.

### 4. LLM-Based Detection
Using a fast LLM (like Llama-3 8B or GPT-4o-mini) prompted specifically to extract PII from a text chunk.
- **Pros:** Highly contextual. Can identify complex PII that rules miss (e.g., "My appointment is regarding my recent heart surgery").
- **Cons:** High latency, expensive, and subject to hallucination. Usually reserved for offline batch processing or highly complex edge cases, not real-time proxying.

## Masking vs. Redacting

Once PII is detected, it must be handled before the prompt is sent to the external API.

- **Redaction:** Replacing the PII with a generic token. 
  *Input:* "My name is John Doe." -> *Output:* "My name is [REDACTED]."
  *Issue:* The LLM loses context. It doesn't know *who* it is talking about, which can ruin conversational coherence.

- **Masking / Tokenization:** Replacing the PII with a consistent pseudonym or token that can be reversed later.
  *Input:* "John bought an apple for Jane." -> *Output:* "<PERSON_1> bought an apple for <PERSON_2>."
  The LLM generates a response: "Tell <PERSON_1> that <PERSON_2> said thanks."
  The application then reverses the mask before showing the user: "Tell John that Jane said thanks."

## On-Premise vs. Cloud Tradeoffs

For organizations with extreme privacy requirements (healthcare, defense, finance), masking PII before sending it to an API is often insufficient, because the context of the conversation itself is sensitive. 

In these scenarios, the only production-ready solution is **Self-Hosted Inference** (running open weights models like Llama-3 or Mistral on internal clusters). This ensures no data ever leaves the corporate VPC, eliminating the need for complex, latency-heavy masking pipelines at the API boundary.

## Common Mistakes

- **Relying solely on Regex:** Regex will miss names, medical conditions, and addresses, leading to compliance failures.
- **Not reversing masks:** Masking data before sending it to the LLM, but forgetting to unmask it in the UI, resulting in a terrible user experience ("Hello <USER_NAME>, how can I help?").
- **Ignoring the output boundary:** Focusing all effort on scrubbing the prompt going *to* the LLM, but failing to scan the output coming *from* the LLM for accidentally retrieved PII.

## Interview Questions

**Q: Why might you choose Microsoft Presidio over a prompt telling the LLM to "Mask all PII"?**
**A:** Telling the LLM to mask PII means the PII has already been transmitted to the external LLM provider, which violates compliance. Furthermore, LLMs are non-deterministic and might fail to mask everything. Presidio runs deterministically on your own infrastructure *before* the API call is made.

**Q: Explain how tokenization/masking preserves LLM functionality better than simple redaction.**
**A:** Simple redaction removes the data entirely (e.g., replacing multiple names with `[NAME]`), which destroys the model's ability to track entities and relationships in a complex prompt. Tokenization replaces entities with consistent unique identifiers (e.g., `<PERSON_A>`, `<PERSON_B>`), allowing the LLM to maintain logical coherence. The application can then map the identifiers back to the real names in the final output.

## Further Reading
- [Microsoft Presidio Documentation](https://microsoft.github.io/presidio/) — The leading open-source tool for data protection and anonymization.
- → See [04-deployment/02-self-hosted-inference.md](../04-deployment/02-self-hosted-inference.md) for alternatives when PII cannot be masked.
