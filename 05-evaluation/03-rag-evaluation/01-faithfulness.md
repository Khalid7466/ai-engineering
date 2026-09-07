</Agent System Instructions>
<Faithfulness in RAG>
## TL;DR
Faithfulness (also called groundedness) measures whether the LLM's generated answer can be entirely deduced from the retrieved context. An answer is unfaithful if it hallucinates information not present in the context, even if that information happens to be factually correct in the real world. 

---

## The Definition of Faithfulness

In RAG, the LLM is expected to act as a synthesizer of provided information, not a standalone oracle. 

**Query:** "What is the company's refund policy?"
**Retrieved Context:** "Refunds are processed within 5-7 business days."
**LLM Answer:** "Refunds are processed within 5-7 business days, and we offer a 30-day money-back guarantee."

If the "30-day money-back guarantee" is not in the context, this answer is **unfaithful**, regardless of whether the company actually has that policy.

## Measurement Strategies

### 1. LLM-Based Checking (The RAGAS Approach)
The most common approach uses an LLM-as-a-judge to verify claims.
1. Extract all discrete statements/claims from the generated answer.
2. For each claim, ask the judge: "Can this statement be logically deduced from the provided context?"
3. **Faithfulness Score** = (Number of supported claims) / (Total number of claims)

### 2. NLI-Based Checking (Natural Language Inference)
Uses smaller, specialized models trained on NLI tasks (entailment, contradiction, neutral).
- The *Context* is the premise.
- The *Answer* is the hypothesis.
- If the model predicts "entailment," the answer is faithful. 
- Faster and cheaper than LLM-as-a-judge, but struggles with complex reasoning.

## Common Patterns of Faithfulness Failure

1. **Parametric Hallucination:** The LLM relies on its pre-trained weights to answer the question instead of the context. (e.g., The context mentions "President Lincoln," and the LLM adds "who was assassinated in 1865" even though the document was only about his birth).
2. **Context Contradiction:** The LLM hallucinates a negative or directly contradicts the context.
3. **Information Blending:** The LLM mixes information from two unrelated retrieved chunks, creating a false relationship.

## Production Implications

Unfaithful RAG systems destroy user trust. In legal, medical, or financial applications, an unfaithful answer is catastrophic. If your faithfulness score drops in CI, it usually means your prompt needs stricter constraints (e.g., "Answer ONLY using the provided context") or your LLM is too weak to follow grounding instructions.

## Common Mistakes
- Confusing factual accuracy with faithfulness. (An answer can be factually true but unfaithful to the context).
- Trying to measure faithfulness using exact-match metrics, which penalizes the LLM for valid summarization and paraphrasing.
- Not isolating statements before checking for faithfulness. Checking the whole paragraph at once often leads the LLM judge to overlook small unfaithful clauses.

## Interview Questions
- **What is the difference between factuality and faithfulness in a RAG system?**
  *Answer:* Factuality means the information is true in the real world. Faithfulness means the information is derived strictly from the retrieved context. A RAG system must be faithful, even if the retrieved context itself is factually incorrect.
- **How would you programmatically measure the faithfulness of a RAG output?**
  *Answer:* Use an LLM-as-a-judge to extract individual claims from the generated answer, then ask the judge to verify if each claim is supported by, contradicted by, or independent of the retrieved context.

## Further Reading
- [RAGAS: Automated Evaluation of Retrieval Augmented Generation](https://arxiv.org/abs/2309.15217) — The paper defining the standard faithfulness metric.
