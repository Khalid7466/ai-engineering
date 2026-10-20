# Model Selection

## TL;DR
Choosing the right LLM for an application is not about picking the "smartest" model. It is an engineering tradeoff between Latency, Cost, Capability, and Data Privacy. The landscape is split between Closed API providers (OpenAI, Anthropic, Google) and Open-Source models (Meta, Mistral) that you can self-host.

---

## The Big Three (Closed APIs)
For the highest capability frontier models, you generally rely on APIs:
1. **OpenAI (GPT-4o, GPT-4o-mini):** The industry standard. Excellent tooling, JSON structured outputs, and general reasoning.
2. **Anthropic (Claude 3.5 Sonnet, Opus):** Currently dominates coding tasks and large-context document analysis. Claude 3.5 Sonnet is arguably the best balance of extreme capability and speed/cost on the market.
3. **Google (Gemini 1.5 Pro, Flash):** Notable for massive context windows (up to 2 Million tokens) and native multimodal capabilities (processing hour-long videos directly).

## Open Source (Weights Available)
Models you can download and run on your own hardware or through managed providers (TogetherAI, Groq).
1. **Meta (Llama 3 8B, 70B, 405B):** The gold standard of open-source. The 8B model is incredibly fast and cheap for basic tasks, while the 70B rivals GPT-4 class models.
2. **Mistral (Mistral-Nemo, Mixtral 8x7B):** Pioneers of MoE architectures in open-source. Excellent performance and highly permissive licenses.

## Decision Framework

### 1. Capability (Does it need to be a genius?)
- **Complex logic, coding, massive RAG synthesis:** Use Frontier models (Claude 3.5 Sonnet, GPT-4o).
- **Data extraction, basic summarization, classification:** Use smaller, faster models (GPT-4o-mini, Llama 3 8B, Claude 3 Haiku). *Never pay GPT-4 prices to parse a 3-line address into JSON.*

### 2. Latency (Time to First Token)
- If building a real-time voice assistant, latency must be <500ms. Groq (running Llama 3 on specialized LPU hardware) or GPT-4o-mini are required. Heavy frontier models are too slow.

### 3. Cost
- Frontier models cost ~$3.00 to $15.00 per 1M tokens. 
- Small models cost ~$0.15 per 1M tokens.
- At scale (e.g., processing millions of customer reviews), model selection can mean the difference between a $50 bill and a $5,000 bill.

### 4. Data Privacy & Compliance
- **Healthcare/Finance/Defense:** Often legally prohibited from sending sensitive data to OpenAI servers. 
- **Solution:** You must self-host Open-Source models (Llama 3) within your own AWS/Azure VPC.

## Production Implications
- **Vendor Lock-in:** API providers frequently deprecate old models. If your entire app relies on a specific quirk of `gpt-3.5-turbo-0613`, your app will break when they turn it off. Use abstraction layers (→ See [16-llm-apis-and-sdks.md](16-llm-apis-and-sdks.md)).
- **Routing:** Modern AI Engineering often involves "LLM Routing." Use a cheap, fast model (Llama 3 8B) to classify the user's intent. If it's a simple greeting, the small model answers. If it's a complex math question, the system dynamically routes the prompt to GPT-4o.

## Common Mistakes
- **Defaulting to GPT-4 for everything:** Wasting money and introducing high latency for simple text-formatting tasks.
- **Underestimating self-hosting costs:** Thinking open-source is "free". Renting an 8xH100 GPU node to run Llama 3 405B costs thousands of dollars a month. It is often much cheaper to use the API unless you have massive continuous volume.

## Interview Questions
- **Q: When would you choose Llama-3-8B over GPT-4o?**
  - *A:* I would choose Llama-3-8B for tasks requiring low latency, low cost (high volume), or strict data privacy (self-hosting), provided the task is relatively simple, like basic text classification or summarizing short emails.
- **Q: What is LLM routing?**
  - *A:* Dynamically directing prompts to different models based on the complexity of the request. Simple queries go to fast/cheap models, while complex reasoning tasks go to expensive frontier models, optimizing both cost and latency.

## Further Reading
- [LMSYS Chatbot Arena Leaderboard](https://chat.lmsys.org/?leaderboard) - The industry standard crowdsourced Elo rating for comparing model capabilities.

---
<!-- nav:start -->
[Previous: Prompt Engineering](14-prompt-engineering.md) | [Module Overview](README.md) | [Next: LLM APIs and SDKs](16-llm-apis-and-sdks.md)
<!-- nav:end -->
