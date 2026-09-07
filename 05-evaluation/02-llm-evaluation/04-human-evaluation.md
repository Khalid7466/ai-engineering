</Agent System Instructions>
<Human Evaluation>
## TL;DR
Automated metrics and LLM judges are scalable, but human evaluation remains the gold standard for nuance, safety, and ultimate ground truth. Building a robust human evaluation process requires clear annotation guidelines, calculating inter-annotator agreement (Cohen's kappa), and choosing between crowd-workers and domain experts. 

---

## When Automated Evals are Insufficient
Automated evals fail when assessing:
1. **Subjective Tone:** Is the response empathetic enough for a healthcare application?
2. **Subtle Hallucinations:** When an LLM judge lacks the domain expertise to realize a plausible-sounding medical or legal claim is actually false.
3. **Safety and Toxicity:** Edge cases in jailbreaks or implicit bias require human cultural context.

## Annotation Guidelines
Human evaluators cannot operate on vibes. They need detailed, unambiguous guidelines.
A good rubric includes:
- **Definitions:** Exactly what constitutes a "hallucination" in this context.
- **Examples:** Positive and negative examples of outputs, with explanations for *why* they received a specific score.
- **Edge Cases:** Instructions on how to handle ambiguous situations (e.g., "If the model refuses to answer a toxic prompt, score it as a 5 for safety, but N/A for helpfulness").

## Inter-Annotator Agreement (IAA)
If two humans disagree on the quality of a response, your ground truth is noisy. 
**Cohen's Kappa ($\kappa$)** is the standard metric for measuring agreement between two annotators, accounting for the possibility of random agreement.

- $\kappa < 0$: Less than chance agreement.
- $0.01 - 0.20$: Slight agreement.
- $0.41 - 0.60$: Moderate agreement.
- $0.81 - 1.00$: Almost perfect agreement.

If your IAA is low (e.g., $< 0.4$), your annotation guidelines are too vague or the task is too subjective. You must rewrite the guidelines and retrain the annotators before collecting more data.

## Crowd vs. Expert Annotators

### Crowd Workers (e.g., MTurk, Scale AI, Surge)
- **Pros:** Cheap, fast, highly scalable.
- **Cons:** Low engagement, prone to clicking through rapidly, inadequate for complex domain-specific tasks (e.g., reviewing medical diagnoses).

### Domain Experts (e.g., Doctors, Lawyers, Senior Engineers)
- **Pros:** High quality, necessary for specialized RAG or agent evaluation.
- **Cons:** Extremely expensive and slow.

## Preference Annotation (A vs. B)
Instead of asking annotators to rate a response on a 1-5 scale (pointwise), it is generally more reliable to present two responses and ask them to pick the better one (pairwise). Humans are much better at relative comparison than absolute scoring. This data is also directly usable for RLHF (Reinforcement Learning from Human Feedback).

## Production Implications
Without periodic human evaluation, LLM-as-a-judge pipelines experience "eval drift." The LLM judge might start penalizing valid responses due to a prompt change or a model update. Human evals serve as the anchor to periodically calibrate and validate the automated eval pipeline.

## Common Mistakes
- Launching a massive annotation task on MTurk without first measuring Inter-Annotator Agreement on a small sample.
- Using vague rubrics like "Rate the quality from 1 to 5."
- Using crowd workers to evaluate highly technical documentation or code.

## Interview Questions
- **Why is Inter-Annotator Agreement important?**
  *Answer:* It proves that the evaluation task is objective and well-defined. If humans cannot agree on the correct label, the data is too noisy to be used as a reliable baseline or training target.
- **Why is A/B preference ranking generally preferred over 1-5 point scales for human evaluators?**
  *Answer:* Humans struggle with absolute calibration (one person's 4 is another's 5), but are highly consistent at determining which of two options is better relative to the other.

## Further Reading
- [Training Language Models to Follow Instructions with Human Feedback (InstructGPT)](https://arxiv.org/abs/2203.02155) — Details OpenAI's use of human preference data.
