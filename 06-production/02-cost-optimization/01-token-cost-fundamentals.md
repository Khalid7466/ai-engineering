# Token Cost Fundamentals

## TL;DR
Unlike traditional software where infrastructure costs are relatively fixed (paying for server uptime), LLM API costs are entirely variable and scale linearly with usage, measured in **tokens**. Understanding how input and output tokens are priced, and what drives their consumption, is the foundation of building economically viable AI applications.

---

## The Economics of Tokens

A token is the fundamental unit of compute for an LLM. It represents a chunk of text (roughly 4 characters, or ¾ of a word in English). 

When you use a managed API (like OpenAI or Anthropic), you are billed based on two metrics:
1. **Input Tokens (Prompt Context):** The text you send to the model.
2. **Output Tokens (Generation):** The text the model generates and returns to you.

Crucially, **output tokens are significantly more expensive than input tokens** (often 3x to 5x more). This is because processing input tokens is highly parallelizable (the model can evaluate the whole prompt at once), whereas generating output tokens is an auto-regressive, sequential process (the model must generate token $N$ before it can calculate token $N+1$).

## Cost Modeling for Production

To model the cost of a production LLM feature, you cannot just look at the price per 1M tokens. You must model the typical workload.

**Formula:**
`Daily Cost = (Avg Input Tokens × Input Price + Avg Output Tokens × Output Price) × Requests Per Day`

### Example Scenario: A RAG Chatbot
Assume you are using a model priced at $10 / 1M Input Tokens and $30 / 1M Output Tokens.

1. **User Query:** 50 tokens.
2. **System Prompt:** 400 tokens.
3. **Retrieved Documents (RAG):** 5 chunks × 500 tokens = 2,500 tokens.
   - *Total Input Tokens:* 2,950
4. **Model Response:** 300 tokens.
   - *Total Output Tokens:* 300

**Cost per Request:**
- Input Cost: (2950 / 1,000,000) * $10 = $0.0295
- Output Cost: (300 / 1,000,000) * $30 = $0.009
- **Total:** ~$0.038 per request.

At 10,000 requests per day, this feature costs **~$11,400 per month**. 
If the business value of this chatbot does not exceed $11,400, the architecture is economically inviable.

## The Biggest Cost Levers

When costs exceed projections, engineers have three primary levers to pull:

### 1. Model Choice
The most dramatic cost savings come from switching models. Moving a workload from a frontier model (like GPT-4) to a smaller model (like GPT-3.5 or Claude Haiku) can reduce costs by 90% instantly. The engineering challenge is ensuring the smaller model can still accomplish the task (often achieved via few-shot prompting or fine-tuning).

### 2. Output Length Reduction
Because output tokens are the most expensive and dictate latency, constraining generation yields high ROI.
- Instead of asking the model to "explain your reasoning and provide the answer," ask it to "output ONLY the final answer."
- If you need reasoning (Chain of Thought) for accuracy, use a smaller, faster model to summarize the final output before passing it to the user.

### 3. Prompt Length (Context) Optimization
In RAG systems, stuffing 10 documents into the context window is expensive. Optimizing the retrieval pipeline—improving the embedding model, using a reranker to return only the top 3 highly-relevant chunks, or implementing prompt compression—drastically reduces input token bloat.

## Tracking Cost in Production

You cannot optimize what you do not measure. Production systems must track token usage at a granular level.
- **Tagging:** Every API request should include metadata (e.g., `user_id`, `feature_name`, `session_id`).
- **Aggregating:** Observability tools (like LangSmith or Helicone) aggregate token counts by these tags, allowing you to identify which features or specific users are burning the most cash.

## Production Implications

If token costs are not actively monitored and optimized, a successful product launch can become a financial disaster. Furthermore, variable costs make margin prediction difficult for SaaS businesses offering "unlimited AI features." Without hard caps or rate limits based on token expenditure, a single power user can cost a company more than their subscription fee.

## Common Mistakes

- **Ignoring the system prompt size:** Writing a massive, 2000-token system prompt and attaching it to every single user query in a chat session. (See → [06-caching-strategies.md](06-caching-strategies.md) for Prefix Caching solutions).
- **Over-retrieving in RAG:** Fetching too many documents from the vector database just to be "safe," drastically inflating input costs.
- **Assuming word count = token count:** Failing to realize that code, JSON, and non-English languages consume significantly more tokens per word than standard English prose.

## Interview Questions

**Q: Why are output tokens typically priced higher than input tokens?**
**A:** Output generation is autoregressive. The model must compute each token sequentially, requiring multiple passes through the network, which is computationally expensive and memory-bandwidth bound. Input tokens can be processed in parallel in a single forward pass.

**Q: A new feature is costing $10,000 a month in LLM API fees. Name three specific engineering steps you would take to reduce this cost.**
**A:** 1. Analyze the logs to see if a smaller, cheaper model can handle the task via model routing. 2. Implement a Semantic Cache to serve identical or highly similar queries for free. 3. Optimize the RAG pipeline by using a cross-encoder reranker to reduce the number of context documents injected into the prompt.

## Further Reading
- [OpenAI Pricing Page](https://openai.com/pricing) — Essential reference for modeling current token costs.
- → See [02-model-routing.md](02-model-routing.md) for strategies on dynamically selecting models to save money.
