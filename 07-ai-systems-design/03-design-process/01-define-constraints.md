## TL;DR
Before writing a single line of code or choosing an architectural pattern, an AI system designer must define the primary constraint of the system. In AI engineering, you are always balancing three competing optimization targets: **Latency**, **Precision**, and **Cost**. You can only optimize for one primarily, and your choice dictates the entire architecture.

---

## The AI Engineering Trilemma

Like the classic "Good, Fast, Cheap: Pick Two" triangle, AI systems operate under strict physical and economic constraints.

1. **Latency (Fast):** Time to first token (TTFT) and total time to complete the task.
2. **Precision (Good):** The accuracy, nuance, and hallucination-rate of the output.
3. **Cost (Cheap):** The API token cost or compute resources required per invocation.

You cannot have a system that uses a 10-step multi-agent loop with GPT-4o (high precision) that responds in 500ms (low latency) and costs $0.0001 per run (low cost). You must choose your anchor constraint based on the business use case.

## Decision Table: Anchor Constraints

| Use Case | Primary Constraint | Secondary | Sacrificed | Architectural Implication |
| :--- | :--- | :--- | :--- | :--- |
| **Customer Support Bot** | **Latency** | Cost | Precision | Use small, fast models (Llama 3 8B, Haiku). Use Standard RAG. No multi-step agents. Fallback to human quickly if unsure. |
| **Medical Diagnosis Assistant** | **Precision** | Latency | Cost | Use frontier models (Claude 3.5 Sonnet, GPT-4o). Use Agentic RAG, multi-step verification, and self-reflection chains. Latency of 30s is acceptable if the answer is perfect. |
| **Bulk Resume Screening** | **Cost** | Precision | Latency | Use parallel pipelines with cheap models (GPT-4o-mini). Batch process overnight (latency irrelevant). Occasional minor errors acceptable due to volume. |
| **Real-time Voice AI** | **Latency** | Precision | Cost | Extreme optimization. Smallest possible models, aggressive semantic caching, streaming audio chunk by chunk. Complex reasoning is entirely sacrificed. |

## Production Implications

### Designing for Latency
If the business requires a sub-2-second response time, your architecture is immediately constrained:
- **No autonomous agents.** An agent loop requires multiple sequential network calls. Network physics prevents this from being fast.
- **No complex RAG reranking.** Cross-encoder reranking adds 500ms-1s. You must rely on faster bi-encoders or metadata filtering.
- **Streaming is mandatory.** You must stream tokens to the UI to improve *perceived* latency, even if total generation takes 3 seconds.

### Designing for Precision
If the business requires zero hallucinations (e.g., legal or financial AI):
- **Forced multi-step.** You must use Prompt Chaining or Orchestrator-Workers to allow the model to draft, critique its own draft, and revise before showing the user.
- **Strict grounding.** You must implement architectures that force citations. Every claim in the generated text must be mapped back to a specific source chunk via deterministic code.
- **Cost will explode.** You will use 10x the tokens for a single request compared to a naive implementation.

## Common Mistakes
- **Ignoring the Trilemma in prototyping:** Engineers often build a prototype using a complex LangGraph multi-agent setup with GPT-4o. It works beautifully in Jupyter. They present it to the product team, who loves it. Then they deploy it, realize it takes 45 seconds to run, and the project dies because they didn't define latency constraints upfront.
- **Treating models as interchangeable:** Swapping GPT-4o for GPT-4o-mini will drop costs by 95% and improve latency, but precision will plummet on complex reasoning tasks. You cannot just swap models to fix a constraint issue; you often have to re-architect the system (e.g., adding prompt chaining to make up for the smaller model's lack of reasoning).
- **Failing to establish SLAs:** Never start building until the business side defines the Service Level Agreement (SLA). "Make it as fast as possible" is not a constraint. "P90 latency must be under 3 seconds" is a constraint you can architect against.

## Interview Questions
- **Q: The business wants an AI to review 10,000 legal contracts by Monday. They want the highest possible accuracy, but they only have a $50 budget. How do you design this?**
  - *Answer:* I don't. I push back on the requirements. 10,000 contracts using a frontier model for high precision will cost thousands of dollars. If the $50 budget is hard, we must sacrifice precision and use a small model, which is unacceptable for legal review. The constraints are physically incompatible.
- **Q: Your single-prompt extraction system has 85% accuracy. The business requires 99%. How do you architect for higher precision without fine-tuning?**
  - *Answer:* I move from a fixed pipeline to a multi-step chain. Step 1: Extract. Step 2: A different prompt reviews the extraction against the source text and highlights errors. Step 3: A third prompt generates the final output based on the review. This sacrifices latency and cost to maximize precision.

## Further Reading
- [The Economics of LLMs](https://a16z.com/2023/06/20/navigating-the-high-cost-of-ai-compute/) — Understanding the cost vectors of AI architecture.
