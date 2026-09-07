</Agent System Instructions>
<LLM-as-a-Judge>
## TL;DR
LLM-as-a-judge uses a powerful model (like GPT-4 or Claude 3.5 Sonnet) to evaluate the outputs of another system based on specific criteria. It bridges the gap between deterministic metrics (which are too rigid) and human evaluation (which is too slow and expensive). Frameworks like G-Eval standardize this approach, though it requires careful mitigation of position bias, self-evaluation bias, and prompt sensitivity.

---

## The G-Eval Framework

G-Eval (Generative Evaluation) uses LLMs with chain-of-thought prompting to evaluate text across criteria like coherence, relevance, or fluency. 

A standard LLM-as-a-judge prompt includes:
1. **Task Description:** What the system is trying to achieve.
2. **Criteria:** Detailed rubric for evaluation (e.g., "Score 1 if completely irrelevant, Score 5 if perfectly relevant").
3. **Input Context:** The user query and any retrieved documents.
4. **Generated Output:** The text to be evaluated.
5. **Chain of Thought:** Requesting the judge to explain its reasoning before outputting a final score.

```python
# Example LLM-as-a-judge prompt
PROMPT = \"\"\"
Evaluate the helpfulness of the Assistant's response.
Score from 1 to 5. 
1: Completely unhelpful or factually incorrect.
5: Highly helpful, accurate, and concise.

User Query: {query}
Assistant Response: {response}

First, write out your reasoning. Then, on a new line, output only the integer score.
\"\"\"
```

## Pairwise vs. Pointwise Evaluation

- **Pointwise:** The judge scores a single output in isolation (e.g., 1-5 scale). Prone to calibration drift.
- **Pairwise (A/B Testing):** The judge compares two outputs (Model A vs. Model B) and selects a winner. Generally more reliable and correlates better with human preferences (used heavily in the Chatbot Arena).

## Biases and Mitigation

LLM judges are not objective; they exhibit systematic biases:

1. **Position Bias:** In pairwise evaluation, the judge often prefers the first response (or sometimes the second). 
   - *Mitigation:* Always run the evaluation twice, swapping the order of Model A and Model B. Only declare a winner if the judge agrees in both orientations.
2. **Verbosity Bias:** LLMs tend to equate "longer" with "better," even if the extra text is fluff.
   - *Mitigation:* Explicitly penalize unnecessary verbosity in the grading rubric.
3. **Self-Evaluation Bias:** Models prefer their own outputs. GPT-4 will rate GPT-4 outputs higher than Claude's, and vice versa.
   - *Mitigation:* Use a panel of different models as judges, or use the strongest available independent model.

## Cost Considerations

Running GPT-4 to judge every output in a CI pipeline is expensive and slow.
- **Solution:** Use smaller, specialized models (e.g., Prometheus, Llama-3-8B) fine-tuned specifically for evaluation tasks.

## Production Implications
If your LLM-as-a-judge prompt is poorly designed, your entire evaluation pipeline becomes noise. Teams often chase improvements in a metric that only exists because the judge prompt is biased toward a specific phrasing, leading to over-optimized, brittle production systems.

## Common Mistakes
- Not requiring the judge to output chain-of-thought reasoning before the score (leads to arbitrary scoring).
- Failing to swap positions in pairwise evaluations.
- Trusting the judge blindly without periodic human audits of the judge's decisions.

## Interview Questions
- **What is position bias in LLM-as-a-judge, and how do you fix it?**
  *Answer:* Position bias is the tendency of an LLM to favor the first (or last) option presented in a pairwise comparison. Fix it by swapping the order of the options and running the evaluation twice.
- **Why should an LLM judge generate its reasoning before outputting a score?**
  *Answer:* Chain-of-thought prompting forces the model to process the criteria and context fully, resulting in a more accurate and stable final score.

## Further Reading
- [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685) — Foundational paper on the viability of LLM judges.
