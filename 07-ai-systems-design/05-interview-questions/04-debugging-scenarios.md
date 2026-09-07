## TL;DR
Debugging AI systems is fundamentally different from traditional software because the failures are often probabilistic, not syntactic. These five scenarios test your ability to diagnose and fix systemic failures in RAG and Agent architectures.

---

## Scenario 1: The Stubborn Hallucinator
**Symptoms:** Your Standard RAG system is retrieving the exact, correct documents. The vector search works perfectly. However, the LLM ignores the retrieved text and hallucinates an answer based on its pre-training data.
**Debug Process:** 
This is a classic "Parametric Memory Override" issue. The LLM thinks it knows the answer better than the context provided.
**The Fix:** 
1. **Strengthen the System Prompt:** Change the prompt from "Answer the question using the context" to "You are a strict data extractor. ONLY use the provided context. If the answer is not explicitly in the context, output exactly 'I do not know'."
2. **Temperature:** Ensure temperature is set to `0.0`. 
3. **Format Forcing:** Ask the LLM to output its answer and include a direct quote from the context proving it.

## Scenario 2: The Agentic Thrash
**Symptoms:** Your autonomous agent works perfectly in local testing. In production, 30% of the time it hits `max_iterations`, times out, and fails the user. 
**Debug Process:**
I would pull the LangSmith/Phoenix traces for the failed runs. I am looking for "thrashing"—when the agent calls a tool, gets an error, tries again, gets an error, and loops endlessly.
**The Fix:**
Often this happens because users ask slightly out-of-domain questions that the agent's tools aren't built for. I would:
1. Implement an upfront Classifier/Router. If the question isn't solvable by the agent's tools, reject it immediately before the agent starts looping.
2. Modify the tool error messages. Instead of returning a raw Python stack trace to the LLM, catch the exception and return a natural language hint: "The tool failed because the date format was wrong. Use YYYY-MM-DD."

## Scenario 3: The Bill Shock
**Symptoms:** Your RAG application's API costs tripled overnight, but user traffic only increased by 10%.
**Debug Process:**
LLM API costs are a function of `Tokens * Invocations`. If traffic is relatively flat, tokens per invocation must have exploded.
1. I check the token usage logs. Is input context size larger, or output generation larger?
2. If input size exploded: A developer likely increased the `top_k` retrieval parameter (e.g., returning 50 chunks instead of 5), or a bug in the chunking logic is returning massive documents.
3. If output size exploded: The model might be caught in a conversational loop or ignoring brevity constraints.
**The Fix:** Hardcode a strict token limit on the context window payload before it hits the API, and enforce a `max_tokens` limit on the generation response.

## Scenario 4: The Degrading Update
**Symptoms:** You swapped the generation model from `gpt-3.5-turbo` to `gpt-4o-mini` to save money. Accuracy stayed the same, but p90 latency increased from 1.5s to 4s.
**Debug Process:**
Model latency is driven by Time To First Token (TTFT) and generation speed (tokens per second).
**The Fix:**
1. **Check Output Length:** Newer, "chattier" models often include preamble ("Certainly! I can help with that..."). This adds 20-30 tokens of generation time. I would aggressively prompt: "Output the answer directly. No preamble. No conversational filler."
2. **Streaming:** Ensure streaming is fully implemented down to the UI so the TTFT feels fast, even if the total generation is slightly slower.

## Scenario 5: The Sycophantic Pivot
**Symptoms:** After updating the system prompt to "Be extremely helpful and polite to the user," the customer support bot starts falsely promising refunds to angry customers, violating company policy.
**Debug Process:**
This is prompt pollution. By emphasizing "politeness" heavily in the system prompt, you inadvertently instructed the model to prioritize user satisfaction over factual accuracy and constraints. The model became a sycophant.
**The Fix:**
1. Remove the subjective "helpful and polite" instructions.
2. Implement **Constitutional AI / Guardrails**: Separate the instructions. Provide a clear hierarchy in the prompt: "PRIORITY 1: Adhere strictly to company policy. PRIORITY 2: Be polite." 
3. If necessary, move the policy enforcement to a deterministic check or a separate fast LLM evaluation step that reviews the draft response for policy violations before showing it to the user.
