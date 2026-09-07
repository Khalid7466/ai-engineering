</Agent System Instructions>
<Evaluation Fundamentals>
## TL;DR
Evaluation fundamentals encompass the distinction between output quality and process quality, online versus offline evaluations, and the choice between automated and human evals. Understanding the "eval pyramid" ensures you build a robust measurement framework that spans from granular unit tests to comprehensive end-to-end assessments.

---

## Output Quality vs. Process Quality

When evaluating an AI system, you must measure both the final result and the steps taken to get there.

- **Output Quality:** Focuses on the final artifact delivered to the user. Was the summary accurate? Did the code run? Is the translation fluent?
- **Process Quality:** Focuses on the intermediate steps. In a RAG system, did it retrieve the right documents? In an agentic system, did it call the correct tools in the right order?

High output quality with poor process quality often indicates the model is relying on its internal parametric knowledge rather than the provided context, increasing the risk of hallucinations on edge cases.

## Online vs. Offline Evals

### Offline Evaluations
Offline evals run in development or CI environments against a static dataset (a "golden dataset"). They are used to gate releases and catch regressions before deployment.
- **Pros:** Safe, reproducible, no impact on real users.
- **Cons:** May not perfectly reflect real-world distribution shifts.

### Online Evaluations
Online evals measure performance in production using actual user interactions.
- **Implicit Metrics:** User engagement (click-through rates, session length, accepted suggestions).
- **Explicit Metrics:** Thumbs up/down, user feedback forms.
- **Pros:** Captures true user satisfaction and real-world behavior.
- **Cons:** Noisy, delayed feedback, and potentially exposes users to degraded experiences during A/B tests.

## Deterministic vs. Probabilistic Metrics

- **Deterministic Metrics:** Exact match, substring match, regex, JSON schema validation. These are cheap, fast, and reliable but only work for constrained tasks.
- **Probabilistic Metrics:** LLM-as-a-judge, BERTScore. These handle the nuance of natural language but introduce their own variability and cost.

## The Eval Pyramid

A robust evaluation strategy mirrors the traditional software testing pyramid:

1. **Unit Evals (Bottom):** Fast, deterministic checks on individual components. (e.g., Does the prompt parser extract the correct entities?)
2. **Component Evals (Middle):** Probabilistic checks on sub-systems. (e.g., RAG context precision, tool-calling accuracy).
3. **End-to-End Evals (Top):** Comprehensive evaluations of the entire system's output quality using LLM-as-a-judge or human annotators. 

## Production Implications

Relying solely on end-to-end evaluations makes debugging nearly impossible. When an end-to-end eval fails, you don't know if the prompt was bad, the retrieval failed, or the tool crashed. Building out the bottom of the eval pyramid is critical for root-cause analysis in production.

## Common Mistakes
- Focusing only on offline evals and ignoring production telemetry.
- Using probabilistic metrics when deterministic metrics would suffice (e.g., using GPT-4 to check if a JSON output contains a specific key).
- Ignoring process quality in RAG systems, leading to "lucky" correct answers that mask underlying retrieval issues.

## Interview Questions
- **What is the difference between online and offline evaluations?**
  *Answer:* Offline evals use static datasets before deployment to catch regressions. Online evals use real user data in production to measure actual impact and satisfaction.
- **Why is evaluating process quality important in a RAG system?**
  *Answer:* Because the LLM might answer correctly based on pre-training data even if retrieval fails. Measuring process quality ensures the system is actually utilizing the retrieved context, which is crucial for answering novel or proprietary questions.

## Further Reading
- [The Testing Pyramid for LLM Applications](https://towardsdatascience.com/the-testing-pyramid-for-llm-applications-a39c5b2447ef) — Adapting software testing principles to AI.
