# Model Routing

## TL;DR
Model routing is the practice of dynamically directing an incoming prompt to the most appropriate LLM based on the query's complexity, intent, or required capabilities. By routing simple queries to smaller, cheaper, and faster models, and reserving massive, expensive models only for complex reasoning tasks, teams can drastically reduce costs (often >60%) and improve average latency without sacrificing output quality.

---

## Why Route? The Cost-Capability Curve

Not all prompts are created equal. 
If a user asks a banking chatbot, "What are your business hours?", a small model (like GPT-3.5 or Claude Haiku) can answer it perfectly in 200 milliseconds for a fraction of a cent. 
If a user asks, "Analyze these three loan documents and tell me which one has the most favorable early-repayment terms," that requires the deep reasoning capabilities of a frontier model (like GPT-4 or Claude Opus), which costs significantly more and takes longer.

Using GPT-4 for the business hours query is a waste of money and compute. Using GPT-3.5 for the loan analysis will result in a hallucinated or incorrect answer. Routing solves this mismatch.

## Routing Architectures

There are three primary ways to build a router in production, ranging from simple heuristics to machine learning classifiers.

### 1. Rule-Based Routing
The simplest approach. The application routes based on hardcoded metadata rather than the text itself.
- **Example:** Free-tier users are hard-routed to a smaller model. Premium subscribers are routed to the frontier model.
- **Example:** Short prompts (< 50 tokens) go to a small model; long prompts go to the large model.

### 2. Semantic Routing (Vector Similarity)
Uses embeddings to route based on the *meaning* or *topic* of the prompt.
1. The developer creates a list of "simple" intents (e.g., greetings, password resets, hours of operation) and generates embeddings for example queries.
2. At runtime, the user's prompt is embedded.
3. The system calculates the cosine distance between the user's prompt and the intent embeddings.
4. If it closely matches a "simple" intent, it routes to the cheap model. Otherwise, it defaults to the expensive model.

### 3. LLM-Based Routing (The "Router Model")
Using a very fast, cheap model specifically prompted to act as a dispatcher.
*Router Prompt:* "Analyze the user's query. If it requires mathematical reasoning, output 'HEAVY'. If it is a casual conversation, output 'LIGHT'."
- **Pros:** Highly flexible and easy to update without retraining classifiers.
- **Cons:** Adds the latency of an LLM call *before* the main generation even begins.

### 4. ML Classifier Routing (The Production Standard)
Training a small, dedicated machine learning model (like a Random Forest or a specialized BERT model) to classify query complexity. 
- **Pros:** Extremely fast (sub-10ms) and highly accurate if trained on historical application logs.
- **Cons:** Requires a dataset of labeled queries and ML ops infrastructure to maintain.

## The Cascade Pattern (Fallback Routing)

A variation of routing is the **Cascade**. Instead of predicting complexity upfront, the system *always* sends the query to the cheap model first. 

However, the cheap model is instructed: "If you do not know the answer, or if the request requires complex analysis, output exactly the string 'I NEED HELP'."
If the system detects that string, it seamlessly retries the query against the expensive frontier model. 

This guarantees low costs for easy queries, but severely penalizes latency for hard queries (as the user must wait for the first model to fail before the second one starts).

## Production Implications

The primary tradeoff in model routing is **Cost vs. Latency vs. Maintenance**. 
Adding an LLM-based router saves money but increases Time to First Token (TTFT). Training a fast ML classifier keeps TTFT low but increases engineering overhead. 

In the [Banking Chatbot Use-Case](../use-case.md), implementing a semantic router for common intents reduced inference costs by 60%, proving that optimizing the router layer is often the highest-ROI engineering task for an LLM product in scale.

## Common Mistakes

- **Routing based purely on prompt length:** Assuming short prompts are easy. "Write a python script to solve the Navier-Stokes equations" is a short prompt that requires massive reasoning power.
- **Ignoring the latency penalty:** Putting a slow LLM in front of another LLM to act as a router, ruining the user experience.
- **Not standardizing tool schemas:** If you route between an OpenAI model and an Anthropic model, their tool-calling syntax and behavior differ. The application code must abstract these differences so the router can swap them cleanly.

## Interview Questions

**Q: What is the main economic advantage of model routing?**
**A:** It optimizes the cost-capability tradeoff by reserving expensive, slow frontier models strictly for complex reasoning tasks, while processing the bulk of simple, high-volume queries with fast, cheap models.

**Q: Compare Semantic Routing with LLM-based Routing. When would you use each?**
**A:** Semantic routing uses embeddings and vector similarity to match queries to predefined intents. It is very fast but requires maintaining an intent database. LLM-based routing uses a small LLM to evaluate the query dynamically. It is more flexible and requires no training data, but it is slower and adds API latency. I would use Semantic routing for well-defined domains (like a customer service bot) and LLM-routing for open-ended applications.

## Further Reading
- [RouteLLM](https://github.com/lm-sys/RouteLLM) — An open-source framework by LMSYS for serving and evaluating LLM routers.
- → See [01-token-cost-fundamentals.md](01-token-cost-fundamentals.md) to understand the underlying pricing math that makes routing necessary.
