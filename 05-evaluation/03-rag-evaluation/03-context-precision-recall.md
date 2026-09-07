</Agent System Instructions>
<Context Precision and Recall>
## TL;DR
Context Precision and Context Recall evaluate the *retrieval* phase of a RAG pipeline. Precision asks, "Of the chunks we retrieved, how many were actually useful?" Recall asks, "Did we retrieve all the chunks necessary to answer the query?" Balancing this F1 tradeoff is the core challenge of RAG engineering.

---

## The Retrieval Tradeoff

Evaluating retrieval requires a golden dataset where, for a given query, you know exactly which chunks in the corpus are the "ground truth" necessary to answer it.

### Context Recall
**Definition:** The proportion of ground-truth relevant chunks that were successfully retrieved.
- **Formula:** (True Positives) / (True Positives + False Negatives)
- **High Recall, Low Precision:** You retrieve 50 chunks. 2 of them contain the exact answer. (You didn't miss anything, but you pulled a lot of garbage).
- **Impact:** High recall is necessary for the LLM to answer the question at all. If recall is low, the LLM physically does not have the information it needs.

### Context Precision
**Definition:** The proportion of retrieved chunks that are actually relevant to the query. 
- **Formula:** (True Positives) / (True Positives + False Positives)
- **High Precision, Low Recall:** You retrieve 2 chunks. Both are highly relevant, but you missed a 3rd chunk required to fully answer a multi-part question.
- **Impact:** Low precision fills the LLM context window with noise. This increases latency, increases API costs, and drastically increases the chance of the LLM hallucinating or getting "distracted" (the needle-in-a-haystack problem).

## Measuring Precision and Recall in RAGAS

In modern RAG evaluation (like RAGAS), you often don't have human-labeled ground truth chunks. Instead, RAGAS uses an LLM to estimate these metrics:

- **Estimated Context Recall:** Provide the LLM with the *Ground Truth Answer* (from your eval dataset) and the *Retrieved Context*. Ask the LLM: "Can the ground truth answer be fully derived from this context?"
- **Estimated Context Precision:** For each retrieved chunk, ask the LLM: "Is this specific chunk useful for answering the query?" Precision is often calculated in a rank-aware manner (e.g., Mean Average Precision), penalizing systems that put the relevant chunks at the very bottom of the retrieved list.

## The Good-Model / Bad-Answer Failure Mode

If your RAG system is failing, you must isolate the generator (LLM) from the retriever (Vector DB). 
If the final answer is bad, look at Context Recall.
- If Context Recall is **low**, the retriever failed. Do not tweak the LLM prompt. You need better embeddings, hybrid search, or better chunking.
- If Context Recall is **high** but the final answer is bad, the generator failed. The context had the answer, but the LLM failed to synthesize it. Now you should tweak the prompt or use a smarter model.

## Production Implications
Engineers often try to fix low Context Recall by simply increasing `top_k` (retrieving 20 chunks instead of 5). This artificially inflates recall but destroys Context Precision, leading to massive latency spikes, blown context limits, and degraded LLM reasoning.

## Common Mistakes
- Evaluating RAG systems purely on final answer quality, making it impossible to know if the retriever or the generator is at fault.
- Ignoring the ranking of retrieved chunks. (A relevant chunk at position 1 is much better than a relevant chunk at position 15 due to LLM position bias).

## Interview Questions
- **In a RAG system, how do you diagnose whether poor performance is caused by the retriever or the LLM?**
  *Answer:* Evaluate Context Recall. If the necessary information is not present in the retrieved chunks, the retriever is at fault. If the information is present but the LLM still generates a bad answer, the generator is at fault.
- **Why is simply increasing `top_k` a bad strategy for improving RAG performance?**
  *Answer:* It increases Context Recall at the expense of Context Precision. Passing too many irrelevant chunks to the LLM increases latency, cost, and the likelihood of hallucinations due to context-window noise.

## Further Reading
- [Evaluating RAG Systems with RAGAS](https://docs.ragas.io/en/latest/concepts/metrics/context_precision.html) — RAGAS documentation on context metrics.
