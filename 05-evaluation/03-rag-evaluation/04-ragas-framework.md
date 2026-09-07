</Agent System Instructions>
<The RAGAS Framework>
## TL;DR
RAGAS (Retrieval Augmented Generation Assessment) is the industry-standard framework for reference-free RAG evaluation. It breaks down evaluation into four distinct metrics: Faithfulness and Answer Relevance (for the generator), and Context Precision and Context Recall (for the retriever). It enables automated, LLM-as-a-judge CI/CD pipelines without requiring expensive human annotation for every run.

---

## The Four Core Metrics

RAGAS maps the two components of RAG (Retriever and Generator) to four specific metrics.

### Generator Metrics
1. **Faithfulness:** Does the generated answer only contain information present in the retrieved context? (Prevents hallucinations).
   → *See [01-faithfulness.md](./01-faithfulness.md)*
2. **Answer Relevance:** Does the generated answer directly address the user's query without unnecessary tangents?
   → *See [02-answer-relevance.md](./02-answer-relevance.md)*

### Retriever Metrics
3. **Context Recall:** Did the retriever pull all the information necessary to answer the query? (Requires a ground-truth answer in the dataset).
   → *See [03-context-precision-recall.md](./03-context-precision-recall.md)*
4. **Context Precision:** Are the retrieved chunks strictly relevant, and are the most relevant chunks ranked at the top?

## Running RAGAS

RAGAS expects a dataset with specific columns depending on the metrics you want to run. A full evaluation requires:
- `question`: The user query.
- `answer`: The generated response from your pipeline.
- `contexts`: A list of strings, the chunks retrieved by your pipeline.
- `ground_truth`: The known correct answer (required for Context Recall).

```python
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevance, context_precision, context_recall

# 1. Prepare your data
data = {
    "question": ["What is the capital of France?"],
    "answer": ["Paris is the capital."],
    "contexts": [["France is a country in Europe. Its capital is Paris."]],
    "ground_truth": ["Paris"]
}
dataset = Dataset.from_dict(data)

# 2. Run evaluation
results = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevance, context_precision, context_recall]
)
print(results)
```

## Interpreting the Scores

RAGAS scores are normalized between 0 and 1. 
- A sudden drop in **Faithfulness** means a prompt change made the model prone to hallucination, or you switched to a weaker LLM.
- A drop in **Context Recall** means a change to your chunking strategy or embedding model broke retrieval.
- A drop in **Context Precision** means you are pulling too much noise.

## Limitations

1. **The Judge is Fallible:** RAGAS relies on an LLM (typically GPT-3.5 or GPT-4) to grade the results. If the judge model is weak, the scores are meaningless. 
2. **Cost and Latency:** Running four LLM-as-a-judge prompts for every single row in your dataset is expensive and slow. It is not suitable for real-time production monitoring; it is designed for offline evaluation in CI/CD.
3. **Domain Specificity:** If the judge LLM cannot understand highly technical jargon (e.g., specific medical terminology), it will give inaccurate Faithfulness or Relevance scores.

## Production Implications
Adopting RAGAS changes development from trial-and-error to systematic engineering. Instead of asking "Does this feel better?", you can explicitly state: "Switching to late-interaction embeddings (ColBERT) improved Context Recall by 12% without degrading Faithfulness, justifying the increased compute cost."

## Common Mistakes
- Running RAGAS using a cheap, weak model (like Llama-3-8B without specialized fine-tuning) as the judge, resulting in garbage metrics.
- Using RAGAS metrics as a direct loss function for fine-tuning. This leads to "Goodhart's Law" where the model learns to game the LLM judge rather than actually improving.

## Interview Questions
- **What are the four core metrics evaluated by RAGAS, and which components of the RAG pipeline do they evaluate?**
  *Answer:* Faithfulness and Answer Relevance evaluate the Generator. Context Precision and Context Recall evaluate the Retriever.
- **What is the primary limitation of frameworks like RAGAS?**
  *Answer:* They rely on LLM-as-a-judge, which makes them expensive, slow to run at scale, and susceptible to the biases and limitations of the judge model.

## Further Reading
- [RAGAS GitHub Repository](https://github.com/explodinggradients/ragas) — Official implementation and tutorials.
