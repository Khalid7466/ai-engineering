## TL;DR
Prompt Chaining is the simplest and most robust AI system architecture. It involves breaking a complex task into a linear sequence of smaller, specialized LLM calls (or deterministic code steps) where the output of one step becomes the input to the next. It is used when the execution path is fixed, predictable, and requires no external knowledge retrieval.

---

## The Mechanism

Instead of asking an LLM to do five things at once in a massive "mega-prompt", Prompt Chaining decomposes the work. 

A typical chain looks like this:
1. **Gatekeeper / Classifier:** Determine the intent of the input.
2. **Extractor:** Pull specific entities from the text into a structured format (JSON).
3. **Validator:** (Deterministic Code) Check if the extracted entities match business rules.
4. **Generator:** Draft a response based on the validated entities.

By isolating tasks, you dramatically reduce the cognitive load on the LLM for any single step, which reduces hallucinations, improves instruction adherence, and makes debugging trivial.

## Code Example: The Support Ticket Chain

Imagine processing an incoming customer support email.

```python
def process_support_ticket(email_text: str) -> dict:
    # Step 1: Classify intent (Fast, cheap model)
    intent = llm_fast.predict(
        prompt=f"Classify intent (refund, tech_support, other): {email_text}",
        schema=IntentSchema
    )
    
    if intent.category == "other":
        return route_to_human(email_text)
        
    # Step 2: Extract details (Structured output)
    extracted_data = llm_structured.predict(
        prompt=f"Extract order ID and issue description from: {email_text}",
        schema=SupportExtractionSchema
    )
    
    # Step 3: Deterministic validation (NO LLM)
    is_valid = verify_order_in_database(extracted_data.order_id)
    if not is_valid:
        return request_clarification()
        
    # Step 4: Generate response (Slower, higher-quality model)
    draft = llm_smart.predict(
        prompt=f"Draft a polite response for {intent.category} for order {extracted_data.order_id}."
    )
    
    return {"status": "processed", "draft": draft}
```

## Production Implications

### The Cascading Failure Problem
If Step 1 in a chain gets the classification wrong, Step 2, 3, and 4 will execute perfectly... but produce completely garbage results. Errors compound linearly.
**Solution:** You must implement assertions and validation between steps. If Step 2 extracts an order ID that doesn't fit the expected regex pattern, the chain must halt and escalate, not pass bad data to Step 3.

### Latency Accumulation
Four LLM calls take longer than one LLM call. If each call takes 1 second, your user waits 4 seconds. 
**Solution:** Use smaller, faster models (like Llama 3 8B or Claude Haiku) for intermediate routing and extraction steps, saving the heavy models (GPT-4) only for the final generation step.

## Common Mistakes
- **Chaining when a single prompt would do:** If the task is simple (e.g., "Summarize this paragraph and extract the names"), a modern LLM can do it in one shot reliably. Don't chain unless quality degrades.
- **Using LLMs for deterministic logic:** Do not use an LLM in a chain to "check if the user is over 18 based on their birthdate." Extract the birthdate with an LLM, then use Python to do the math.
- **Ignoring intermediate observability:** If a chain fails in production, you need to know *which* step failed. Every node in the chain must log its input and output to a tracing system (like LangSmith or Braintrust).

## Interview Questions
- **Q: Why would you use Prompt Chaining instead of an Agent?**
  - *Answer:* Predictability, cost, and latency. If I know the exact steps needed to solve a problem, an Agent will waste time and tokens "thinking" about what to do next. A chain forces the execution path, guaranteeing lower latency and higher reliability.
- **Q: How do you handle a step failing in a prompt chain?**
  - *Answer:* Introduce deterministic validation between LLM calls. If the output schema is violated or business logic fails, trigger a fallback mechanism—either a retry with a "fix this" prompt, or an escalation to a human.
- **Q: Can prompt chaining be parallelized?**
  - *Answer:* Yes. The "Parallel Map" or "Fan-out/Fan-in" pattern is a variation of chaining. If Step 2 needs to evaluate 5 different sub-topics, you can launch 5 concurrent LLM calls, wait for them to finish, and pass all 5 results into the final Step 3 synthesizer.

## Further Reading
- [Anthropic Prompt Engineering Interactive Tutorial](https://github.com/anthropics/anthropic-cookbook) — Demonstrates chaining best practices for Claude.
