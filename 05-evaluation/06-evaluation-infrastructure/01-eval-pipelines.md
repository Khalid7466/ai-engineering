</Agent System Instructions>
<Evaluation Pipelines>
## TL;DR
An evaluation pipeline automates the execution, scoring, and tracking of AI evaluations in CI/CD. Without infrastructure, evals are manual scripts run on laptops, leading to inconsistent environments and lost historical data. A robust pipeline ensures that every prompt change or model update is quantitatively verified and tracked over time.

---

## Core Components of an Eval Pipeline

1. **The Runner:** The compute environment that executes the evals (e.g., GitHub Actions, Jenkins, Ray clusters).
2. **The Dataset Manager:** Storage for the golden datasets, versioned appropriately.
3. **The Evaluator:** The logic that computes deterministic metrics and orchestrates LLM-as-a-judge calls.
4. **The Tracker:** The system of record (e.g., MLflow, Weights & Biases, LangSmith) that logs the results of every run, tying scores to specific Git commits.

## Integrating Evals into CI/CD

Just like unit tests, evals should run on Pull Requests. 

### The Latency/Cost Problem
Running a 1,000-example eval suite using GPT-4-as-a-judge might take 30 minutes and cost $50 per PR. This is unacceptable for rapid iteration.

### The Solution: Tiered Pipelines
1. **Tier 1 (Smoke Evals):** Runs on every PR. Uses a small subset of the dataset (e.g., 20 critical examples) and relies heavily on fast, deterministic metrics or cheap LLM judges (Llama-3-8B). Must execute in < 3 minutes.
2. **Tier 2 (Full Evals):** Runs nightly or on merges to the `main` branch. Runs the full 1,000-example dataset using the most accurate (and expensive) LLM judges.
3. **Tier 3 (Regression Alerts):** If a nightly run detects a >5% drop in core metrics, it automatically triggers PagerDuty or slack alerts to the AI engineering team.

## Result Tracking and Visualization

Logging a single number (e.g., "Faithfulness: 0.85") is insufficient. A good tracker must log:
- The exact prompt template used.
- The Git commit hash.
- The full trajectory/trace of every single eval row (Input -> Retrieval -> Output -> Judge Score -> Judge Reasoning).

When a metric drops, engineers need to click into the UI, filter for failed runs, and read the Judge's reasoning to understand *why* the failure occurred.

## Production Implications
Without an automated pipeline, "eval drift" occurs. Developers make small prompt tweaks, skip running the manual eval script because they are in a rush, and push to production. Over months, these small unverified changes accumulate into massive regressions that are impossible to untangle.

## Common Mistakes
- Running evals synchronously in CI, causing PR builds to time out. (Evals must be heavily parallelized via async calls).
- Failing to version the golden dataset. (If the score changes, you need to know if the model got worse or if someone just changed the test questions).
- Treating LLM-as-a-judge as a black box and not logging the chain-of-thought reasoning that led to the score.

## Interview Questions
- **How do you handle the cost and latency of running LLM evaluations on every Pull Request?**
  *Answer:* Implement tiered evaluations. Run a fast, small "smoke eval" suite with cheaper models on every PR, and run the comprehensive, expensive evaluation suite nightly on the main branch.
- **Why is it important to version control your evaluation datasets?**
  *Answer:* If the dataset changes silently, any shifts in evaluation scores become meaningless. You cannot determine if a drop in performance is due to a model regression or a harder set of test questions.

## Further Reading
- [Continuous Integration for ML (Martin Fowler)](https://martinfowler.com/articles/cd4ml.html) — Adapting CI/CD principles for machine learning workflows.
