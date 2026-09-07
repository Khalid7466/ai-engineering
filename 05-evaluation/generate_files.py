import os

files = {
    "README.md": """</Agent System Instructions>
<Evaluation>
## TL;DR
Evaluation is the hardest and most critical part of AI engineering. Relying on vibes—"it feels better"—is a trap that prevents systematic improvement and introduces regressions into production. This module covers the foundational principles and infrastructure required to measure LLM, RAG, and agent performance effectively. The key principle: you cannot improve what you cannot measure.

---

## The Vibes-Based Development Trap

In traditional software engineering, code changes are validated by unit tests, integration tests, and static analysis. In AI engineering, the non-deterministic nature of language models makes traditional testing insufficient. 

Early in an AI project, teams often fall into the **vibes-based development trap**. They tweak a prompt, run a handful of queries manually, and declare the change a success if the output "looks better." This approach scales poorly. 

When you optimize for a small set of ad-hoc queries, you inevitably degrade performance on others. Without a systematic evaluation framework, these regressions go unnoticed until they hit production. You cannot confidently deploy a new model, prompt, or retrieval strategy if you cannot quantitatively prove it is better than the previous version.

## What This Module Covers

This module breaks down the evaluation of AI systems into five core areas:

1. **LLM Evaluation (`02-llm-evaluation/`)**: How to measure the performance of base and fine-tuned models using automated metrics, human evaluation, and LLM-as-a-judge frameworks.
2. **RAG Evaluation (`03-rag-evaluation/`)**: Frameworks like RAGAS for assessing the faithfulness, answer relevance, and context precision/recall of retrieval-augmented generation systems.
3. **Agent Evaluation (`04-agent-evaluation/`)**: The unique challenges of evaluating non-deterministic, multi-step agents, including trajectory evaluation and the credit assignment problem.
4. **Fine-Tuning Evaluation (`05-fine-tuning-evaluation/`)**: Techniques for benchmarking fine-tuned models, checking for capability regression, and mitigating catastrophic forgetting.
5. **Evaluation Infrastructure (`06-evaluation-infrastructure/`)**: How to build robust evaluation pipelines, integrate them into CI/CD, construct golden datasets, and track results over time.

## Production Implications

If you ignore evaluation, you are flying blind. In production, this manifests as:
- **Silent Regressions**: A prompt update improves edge cases but breaks core functionality.
- **Wasted Effort**: Engineering time spent on optimizations that don't actually improve user outcomes.
- **Lack of Confidence**: Inability to roll out new models (e.g., upgrading from GPT-3.5 to GPT-4o) because you don't know how it will impact the system.

## Common Mistakes
- Relying entirely on manual testing and "vibes."
- Evaluating only the final output of a multi-step agent or RAG system, ignoring the intermediate steps (e.g., retrieval quality, tool selection).
- Using reference-based metrics (e.g., BLEU, ROUGE) for open-ended generative tasks.
- Failing to build a robust, representative "golden dataset" for evaluation.

## Interview Questions
- **Why is evaluation harder for LLMs than for traditional software?** 
  *Answer:* LLMs are non-deterministic and output natural language, making exact-match string comparisons ineffective. Evaluation often requires subjective judgment or proxy metrics.
- **What is the risk of "vibes-based" evaluation?** 
  *Answer:* It leads to silent regressions, overfitting to small, non-representative test sets, and prevents confident iterations.

## Further Reading
- [Evaluating LLMs is a double-edged sword](https://huyenchip.com/2023/10/11/llm-evaluation.html) — Chip Huyen's comprehensive guide to LLM evaluation.
""",
    "use-case.md": """</Evaluation>
<Use Case: Telecom Customer Support Chatbot>
## Objective
A major telecom company wanted to automate customer support using a RAG-based chatbot. The bot needed to answer questions about billing, troubleshooting, and plan upgrades by retrieving information from internal knowledge bases.

## Why Eval-Driven Development?
For the first three months, the engineering team relied on "vibes-based development." They would tweak prompts and chunking strategies, manually test 5-10 queries, and deploy if it "felt better."

This approach failed spectacularly. Customers complained that the bot was hallucinating policies (e.g., promising refunds that didn't exist) and failing to use the right tools (e.g., checking a user's account balance). 

A newly hired AI engineer implemented an Eval-Driven Development (EDD) approach in week 1. The goal was to build a systematic, automated pipeline to measure performance before any changes reached production.

## Technical Decisions

### Decision 1: Building the Golden Dataset
- **Chose:** A manually curated dataset of 100 "golden" Q&A pairs, representative of real user queries.
- **Rejected:** Using an LLM to generate thousands of synthetic Q&A pairs.
- **Rationale:** While synthetic data is great for scaling, the team needed a high-quality, ground-truth baseline to start. Real user queries provided the most accurate reflection of production challenges.

### Decision 2: Evaluation Framework
- **Chose:** RAGAS (Retrieval Augmented Generation Assessment) combined with LLM-as-a-judge for tool calling.
- **Rejected:** Exact match or BLEU/ROUGE scores.
- **Rationale:** The bot's answers varied in phrasing. RAGAS allowed the team to measure faithfulness (preventing hallucinations) and context precision (ensuring the right docs were retrieved) without requiring exact string matches.

## Architecture Walkthrough

1. **Dataset Construction:** The team extracted 100 complex, diverse queries from real support logs. For each query, human annotators provided the expected answer, the required retrieved context, and the correct tool calls.
2. **Automated Pipeline:** They built a Python script that ran the 100 queries through the chatbot, logging the retrieved context, tool calls, and final answers.
3. **Evaluation Execution:** 
    - **RAGAS** evaluated faithfulness and answer relevance.
    - **LLM-as-a-judge** (using GPT-4) evaluated whether the correct tools were invoked with the correct parameters.
4. **CI/CD Integration:** The evaluation script was integrated into GitHub Actions. Any PR that degraded the overall score by more than 2% or introduced a faithfulness failure was blocked.

## Lessons Learned

### The Baseline Results
When the eval suite was first run, the results were sobering:
- **34% Faithfulness Failure Rate:** The bot was frequently contradicting the retrieved documents, leading to policy hallucinations.
- **22% Tool Failure Rate:** The bot was guessing account details instead of calling the `get_account_balance` tool.

### Catching Regressions
Shortly after implementing EDD, a developer submitted a PR that optimized the prompt to make the bot more conversational. The eval suite caught that while answer relevance improved slightly, tool calling accuracy dropped by 15%. The regression was caught in CI, saving the company from deploying a broken update. 

EDD transformed the team's culture. They moved from arguing over subjective quality to making data-driven decisions based on evaluation metrics.
""",
    "01-evaluation-fundamentals.md": """</Agent System Instructions>
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
""",
    "02-llm-evaluation/01-reference-based-metrics.md": """</Agent System Instructions>
<Reference-Based Metrics>
## TL;DR
Reference-based metrics compare an LLM's output against a human-written "ground truth" reference. Metrics like BLEU and ROUGE rely on lexical overlap, while BERTScore and METEOR incorporate semantic similarity. While useful for constrained tasks like translation or extractive summarization, they fundamentally fail for open-ended generation where multiple distinct answers can be equally correct.

---

## Lexical Overlap Metrics

### BLEU (Bilingual Evaluation Understudy)
BLEU measures precision based on n-gram overlap between the generated text and the reference text. It penalizes brevity to prevent models from outputting a single correct word.
- **Primary Use Case:** Machine translation.
- **Why it's bad for open-ended generation:** BLEU requires exact word matches. "The cat sat on the mat" and "A feline rested on the rug" mean the same thing but have a terrible BLEU score.

### ROUGE (Recall-Oriented Understudy for Gisting Evaluation)
ROUGE focuses on recall—how much of the reference n-grams appear in the generated output. ROUGE-L specifically looks at the longest common subsequence.
- **Primary Use Case:** Summarization.
- **Why it's bad for open-ended generation:** Like BLEU, it penalizes paraphrasing and ignores semantic meaning. 

## Semantic Metrics

### BERTScore
BERTScore addresses the flaws of lexical metrics by using pre-trained language models (like BERT) to compute cosine similarity between the contextual embeddings of the generated and reference tokens.
- **Pros:** Handles paraphrasing well; recognizes that "cat" and "feline" are similar.
- **Cons:** Computationally expensive; biased by the underlying embedding model's training data.

### METEOR
METEOR improves upon BLEU by incorporating stemming (matching "running" with "run") and synonym dictionaries (WordNet) before calculating overlap. 

## Why Reference-Based Metrics Fail for LLMs

In traditional NLP (translation, classification), the space of acceptable answers is narrow. For modern LLM tasks (creative writing, reasoning, open-ended Q&A), the space is vast. 

If the reference answer is: *"Paris is the capital of France, known for the Eiffel Tower."*
And the LLM outputs: *"The capital of France is Paris, and it features famous landmarks like the Eiffel Tower."*

Lexical metrics will score this poorly. Even semantic metrics like BERTScore struggle when the LLM provides additional valid context not present in the reference.

## Production Implications
Using BLEU or ROUGE to evaluate a customer support chatbot will lead to catastrophic misalignment. Engineers will optimize prompts to mimic the exact phrasing of the reference dataset, resulting in robotic, repetitive outputs and penalizing the model for helpful elaboration.

## Common Mistakes
- Blindly applying ROUGE to generative Q&A tasks.
- Assuming a high BERTScore means the answer is factually correct (it only measures semantic similarity, not truthfulness).
- Wasting engineering hours trying to improve BLEU scores on open-ended tasks.

## Interview Questions
- **Why is BLEU a poor metric for evaluating a creative writing LLM?**
  *Answer:* BLEU measures exact n-gram overlap. Creative writing has many valid, diverse ways to express the same idea, which BLEU penalizes.
- **How does BERTScore improve upon ROUGE?**
  *Answer:* BERTScore uses contextual embeddings to measure semantic similarity, allowing it to recognize paraphrases and synonyms that ROUGE's exact-match n-gram approach misses.

## Further Reading
- [BERTScore: Evaluating Text Generation with BERT](https://arxiv.org/abs/1904.09675) — The original paper introducing semantic evaluation.
""",
    "02-llm-evaluation/02-llm-as-judge.md": """</Agent System Instructions>
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
""",
    "02-llm-evaluation/03-benchmarks.md": """</Agent System Instructions>
<Benchmarks>
## TL;DR
Public benchmarks like MMLU, HumanEval, and HELM provide standardized tests to compare base and fine-tuned models. The `lm-evaluation-harness` makes running these accessible. However, benchmarks must be interpreted with extreme skepticism due to data contamination, task-specific overfitting, and the disconnect between benchmark scores and real-world utility.

---

## Key Benchmarks

### MMLU (Massive Multitask Language Understanding)
Tests knowledge breadth across 57 subjects (math, history, law, medicine) using multiple-choice questions. It is the standard proxy for general knowledge capability.

### HumanEval
Created by OpenAI, it evaluates coding capabilities by prompting the model to complete Python functions based on docstrings. Evaluated using `pass@k` (does at least one of *k* generated samples pass the hidden unit tests?).

### HellaSwag & ARC
- **HellaSwag:** Tests commonsense natural language inference (picking the most logical completion to a sentence).
- **ARC (AI2 Reasoning Challenge):** Grade-school science questions, split into Easy and Challenge sets.

### HELM (Holistic Evaluation of Language Models)
A comprehensive framework by Stanford that evaluates models across diverse scenarios and metrics (accuracy, fairness, bias, toxicity), rather than just raw performance.

## Running Benchmarks: lm-evaluation-harness
EleutherAI's `lm-evaluation-harness` is the industry standard for evaluating open-source models. It provides a unified interface to run hundreds of benchmarks locally against Hugging Face, vLLM, or API-based models.

```bash
# Running MMLU against a local model
lm_eval --model hf \
    --model_args pretrained=meta-llama/Llama-3-8B \
    --tasks mmlu \
    --device cuda:0 \
    --batch_size 8
```

## The Contamination Problem
Because LLMs are trained on massive scrapes of the internet, benchmark test sets (which are public) inevitably leak into the training data.
- **Data Contamination:** The model isn't "reasoning" through the MMLU question; it simply memorized the answer during pre-training.
- **Mitigation:** De-contamination checks (searching training data for benchmark n-grams) are standard, but newer methods rely on creating private, held-out eval sets that are never published.

## Production Implications
Optimizing a fine-tune purely to increase MMLU or HumanEval scores often leads to catastrophic forgetting or degradation in the specific tasks your users actually care about. A model that scores 85 on MMLU might still fail completely at your proprietary data extraction task. 

## Common Mistakes
- Assuming a model with a higher MMLU score will perform better on a domain-specific RAG task.
- Fine-tuning on data that unintentionally includes benchmark test sets, leading to artificially inflated performance.
- Using 0-shot evaluation for one model and 5-shot evaluation for another, then comparing the scores.

## Interview Questions
- **What does data contamination mean in the context of LLM benchmarks?**
  *Answer:* It occurs when the questions and answers from a benchmark test set are accidentally included in the model's training data, allowing the model to memorize the answers and artificially inflating its score.
- **What does the HumanEval benchmark measure, and how is it evaluated?**
  *Answer:* It measures Python coding capability. It is evaluated using the pass@k metric, where the model generates k code completions, and the test is passed if at least one completion successfully passes a suite of hidden unit tests.

## Further Reading
- [Language Model Evaluation Harness](https://github.com/EleutherAI/lm-evaluation-harness) — EleutherAI's GitHub repository.
""",
    "02-llm-evaluation/04-human-evaluation.md": """</Agent System Instructions>
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
""",
    "03-rag-evaluation/01-faithfulness.md": """</Agent System Instructions>
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
""",
    "03-rag-evaluation/02-answer-relevance.md": """</Agent System Instructions>
<Answer Relevance>
## TL;DR
Answer Relevance measures how well the generated answer addresses the user's specific query. It is distinct from faithfulness: an answer can be perfectly faithful to the retrieved context but completely irrelevant to what the user actually asked. 

---

## Faithfulness vs. Answer Relevance

- **Faithfulness:** Does the answer match the *context*?
- **Answer Relevance:** Does the answer match the *query*?

**Scenario:**
- **Query:** "How do I reset my password?"
- **Retrieved Context:** "To update your billing info, go to settings. To reset your password, click 'Forgot Password' on the login screen."
- **LLM Answer:** "To update your billing info, go to settings."

This answer is **100% faithful** (the information is in the context), but it has **0% answer relevance** (it didn't answer the user's question).

## How to Measure Answer Relevance

Measuring relevance directly with LLM-as-a-judge (e.g., "Score how relevant this is from 1-10") can be noisy. The RAGAS framework uses an ingenious reverse-engineering approach:

1. Take the generated answer.
2. Prompt an LLM to generate *N* potential questions that this answer would be a good response for.
3. Compute the semantic similarity (using embeddings) between the user's *original query* and the *generated questions*.
4. **Relevance Score:** The mean cosine similarity across the *N* generated questions.

If the answer was truly relevant to the original query, the reverse-generated questions will closely match the original query. If the answer went on a tangent, the generated questions will diverge from the original query, resulting in a low score.

## Penalizing Incompleteness and Redundancy

High answer relevance requires being concise and direct. 
- **Incompleteness:** Failing to answer all parts of a multi-part query lowers relevance.
- **Redundancy:** Including massive amounts of irrelevant information (even if the correct answer is buried inside) lowers relevance. 

## Production Implications

Low answer relevance in production usually stems from two issues:
1. **Poor Retrieval (Context Precision):** The retriever pulled irrelevant documents, forcing the LLM to either say "I don't know" or hallucinate an answer based on the irrelevant docs.
2. **Poor Prompting:** The LLM is instructed to summarize everything in the context, rather than extracting only the specific answer the user requested.

## Common Mistakes
- Combining faithfulness and relevance into a single "quality" score. They diagnose different failure modes and must be tracked separately.
- Ignoring verbosity. An LLM that regurgitates 500 words to answer a yes/no question is providing an irrelevant experience, even if the "yes" is in there somewhere.

## Interview Questions
- **Can a RAG answer be faithful but irrelevant? Provide an example.**
  *Answer:* Yes. If the user asks for a password reset, and the context contains both password reset and billing info, the LLM might only summarize the billing info. The output is faithful to the context but irrelevant to the query.
- **How does the RAGAS framework calculate answer relevance without relying on subjective 1-10 scoring?**
  *Answer:* It uses an LLM to reverse-generate questions based on the generated answer, then calculates the embedding cosine similarity between the generated questions and the original user query.

## Further Reading
- → See [04-ragas-framework.md](./04-ragas-framework.md) for how this metric fits into the broader RAGAS suite.
""",
    "03-rag-evaluation/03-context-precision-recall.md": """</Agent System Instructions>
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
""",
    "03-rag-evaluation/04-ragas-framework.md": """</Agent System Instructions>
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
""",
    "04-agent-evaluation/01-agent-eval-challenges.md": """</Agent System Instructions>
<Challenges in Agent Evaluation>
## TL;DR
Evaluating AI agents is exponentially harder than evaluating standard LLMs or RAG systems. Agents operate non-deterministically, can achieve goals through multiple valid paths, produce irreversible side effects, and suffer from the credit assignment problem in multi-step workflows. Traditional text-based metrics are entirely inadequate.

---

## Why Agent Evals are Hard

Standard LLM evaluation looks at a static input and output: Given query X, did it generate text Y? 
Agents, however, interact with an environment. They plan, use tools, observe results, and iterate.

### 1. Non-Determinism and Multiple Valid Paths
If you ask an agent to "Find the cheapest flight to NYC and email it to Alice," there are multiple valid trajectories:
- **Path A:** Search Kayak tool -> Draft Email -> Send Email tool.
- **Path B:** Search Expedia tool -> Search Kayak tool -> Compare -> Send Email tool.
Both succeed. You cannot evaluate agents using exact-match on the sequence of tool calls, because Path B is perfectly valid (and perhaps more thorough).

### 2. Side Effects and State
Agents take actions that change the world (writing to databases, sending emails, deleting files). You cannot evaluate them safely in production. 
- You must build mock environments, sandboxes, and dummy APIs. If the mock environment doesn't perfectly replicate production, the eval is useless.

### 3. The Credit Assignment Problem
If an agent fails a 15-step task on step 14, why did it fail?
- Did the LLM hallucinate on step 14?
- Did a tool return an ambiguous error message on step 10, confusing the agent?
- Did the initial planning phase on step 1 fail to account for a constraint?
Assigning blame (credit assignment) to the specific component that caused the cascade of failures is a major infrastructure challenge.

### 4. Multi-Step Cascading Failures
A 95% success rate on individual steps sounds good. But if an agent requires 10 steps to complete a task, the overall success rate is $0.95^{10} \approx 60\%$. Evaluating agents requires measuring both the step-level reliability and the overall task completion rate.

## Evaluating the Goal vs. the Process

- **Goal-based Evaluation:** Did Alice receive an email with the cheapest flight? This requires checking the final state of the environment (e.g., querying the mock email server).
- **Process-based Evaluation:** Did the agent waste money by calling the search API 50 times? Did it attempt a prompt injection on its own tools? 

## Production Implications
Without robust agent evaluations, teams deploy agents that enter infinite loops of tool calling, rack up massive API bills, or execute destructive actions. You cannot deploy an autonomous agent without a CI pipeline that runs it through hundreds of simulated environments and verifies both goal completion and process safety.

## Common Mistakes
- Evaluating only the final text output of the agent, ignoring the tools it called.
- Using a static list of expected tool calls for evaluation, which breaks as soon as the agent finds a different, valid way to solve the problem.
- Testing agents in environments that have real-world side effects.

## Interview Questions
- **What is the credit assignment problem in agent evaluation?**
  *Answer:* In a multi-step agent trajectory, if the final goal fails, it is difficult to determine which specific earlier step, flawed plan, or tool output was the root cause of the failure.
- **Why are exact-match sequences inappropriate for evaluating agent tool calls?**
  *Answer:* Because agents can often achieve the same goal through multiple valid sequences of actions (e.g., trying a tool, failing, trying an alternative tool, and succeeding). Exact match penalizes successful, resilient behavior.

## Further Reading
- [WebArena: A Realistic Web Environment for Building Autonomous Agents](https://arxiv.org/abs/2307.13854) — Standard benchmark for evaluating agents in browser environments.
""",
    "04-agent-evaluation/02-trajectory-evaluation.md": """</Agent System Instructions>
<Trajectory Evaluation>
## TL;DR
Trajectory evaluation assesses not just the final output of an agent, but the entire call stack: which tools were called, in what order, with what parameters, and how the agent reacted to tool outputs. It is critical for diagnosing multi-step failures, ensuring safety boundaries, and optimizing agent efficiency.

---

## What is a Trajectory?

A trajectory is the complete log of an agent's reasoning and actions during an execution loop. It typically consists of an alternating sequence:
1. `Thought`: The agent's reasoning.
2. `Action`: The tool invoked.
3. `Action Input`: The parameters passed to the tool.
4. `Observation`: The result returned by the environment.

## Methods for Trajectory Evaluation

### 1. Heuristic and Rule-Based Checks
Before using expensive LLM judges, you can write deterministic rules over the trajectory list:
- **Efficiency:** `len(tool_calls) < MAX_STEPS`. Did it take 20 steps to do a 3-step task?
- **Safety:** Ensure `delete_database` tool was never in the trajectory.
- **Progress:** Did the agent call the exact same tool with the exact same parameters twice in a row? (Detecting infinite loops).

### 2. LLM-as-a-Judge for Trajectories
You can pass the entire trajectory trace to a powerful model (like GPT-4) and ask it to evaluate the agent's logic.

**Example Rubric for the Judge:**
- Did the agent correctly interpret the error messages from the tools?
- Did the agent formulate a logical plan?
- Did the agent hallucinate any tool outputs?

```python
# Conceptual LLM Judge Prompt for Trajectory
PROMPT = \"\"\"
Review the following agent trajectory.
Task: {user_task}
Trajectory:
{trajectory_trace}

Evaluate the agent's efficiency and error recovery on a scale of 1-5.
Did it waste API calls? Did it recover from tool errors gracefully?
\"\"\"
```

### 3. Golden Trajectories and Edit Distance
For specific, constrained tasks, you can define a "Golden Trajectory" (the optimal sequence of tool calls). You can then evaluate the agent's trajectory by calculating the edit distance (Levenshtein distance) between the actual sequence of tools used and the golden sequence. 
- *Caveat:* As discussed in [agent challenges](./01-agent-eval-challenges.md), penalizing deviation too harshly punishes creative or resilient problem-solving.

## Evaluating Error Recovery
One of the most important aspects of trajectory evaluation is testing how the agent handles failure. 
- **The Setup:** Intentionally mock a tool to return a `500 Internal Server Error` or `Invalid Parameter` response on the first try.
- **The Eval:** Check the trajectory. Did the agent panic and output the error to the user? Or did it read the error, adjust its parameters, and retry successfully?

## Production Implications
When a user reports that your agent "failed," looking at the final answer tells you nothing. Trajectory logging and evaluation allow you to build trace viewers (like LangSmith or Phoenix) to visualize the exact step where the agent's logic derailed, which is essential for prompt debugging.

## Common Mistakes
- Only evaluating the final `Observation` and ignoring the `Thought` blocks. The agent might have gotten the right answer for the wrong reasons (flawed logic).
- Not testing agent trajectories against mocked failures. If you only test happy paths, your agent will collapse in production the first time an API times out.

## Interview Questions
- **How would you programmatically detect if an agent is stuck in an infinite loop?**
  *Answer:* Analyze the trajectory array. If you detect repeating subsequences of `Action` and `Action Input` with identical `Observation` errors, the agent is looping.
- **Why is evaluating error recovery crucial in trajectory evaluation?**
  *Answer:* Because in production, tools fail, APIs time out, and databases return empty results. An agent's quality is defined by its ability to observe these errors in the trajectory and adjust its plan, rather than failing the entire task.

## Further Reading
- [AgentBench: Evaluating LLMs as Agents](https://arxiv.org/abs/2308.03688) — Comprehensive framework for evaluating agent trajectories across multiple environments.
""",
    "04-agent-evaluation/03-eval-driven-development.md": """</Agent System Instructions>
<Eval-Driven Development (EDD)>
## TL;DR
Eval-Driven Development (EDD) adapts Test-Driven Development (TDD) for AI. You write the evaluation dataset and the metrics *before* you write the prompt, build the RAG pipeline, or design the agent. This approach prevents vibes-based development, anchors progress in quantitative metrics, and catches regressions automatically in CI/CD.

---

## The EDD Workflow

1. **Define the Golden Dataset:** Before touching an LLM, curate a dataset of 50-100 representative inputs (user queries, tasks) and define what a successful output or final state looks like.
2. **Define the Metrics:** Decide how success will be measured (e.g., RAGAS Context Recall, deterministic tool-call checks, or LLM-as-a-judge for tone).
3. **Establish a Baseline:** Run a naive prompt or basic model against the dataset to get a baseline score.
4. **Iterate and Optimize:** Modify prompts, chunking strategies, or tool descriptions. Run the eval suite after *every* change. If the score goes up, keep the change. If it goes down, revert.

## Constructing the Golden Dataset

The golden dataset is your ground truth. It must be:
- **Representative:** It should reflect actual production traffic, not just edge cases.
- **Diverse:** Include easy questions, complex multi-step reasoning tasks, and adversarial inputs (e.g., prompt injections).
- **Static but Living:** The core set should remain stable so you can track regressions over time, but it should be updated periodically with failed queries from production.

## The Sandbox Environment
For agents, EDD requires a safe sandbox. If your agent interacts with a database, your eval suite must spin up a temporary Docker container with a dummy database, run the agent, check the database state (e.g., "Was the record deleted?"), and then tear down the container. Mocking tools is acceptable, but full sandboxes provide higher fidelity.

## CI/CD Integration
EDD is useless if it only runs on a developer's laptop.
- The eval suite must run on every Pull Request.
- **Regression Gating:** If a PR drops the overall eval score by >2%, or fails any critical deterministic checks (e.g., PII leakage), the CI pipeline blocks the merge.

## Catching Regressions: A Case Study
*(Reference: → See [use-case.md](../use-case.md))*
In the telecom chatbot use case, an engineer optimized the system prompt to make the bot more conversational. 
- **Without EDD:** The engineer would have manually tested "Hello, how are you?", seen a polite response, and deployed.
- **With EDD:** The CI pipeline ran the 100 golden queries. It caught that the new conversational instructions caused the LLM to ignore the `get_account_balance` tool instruction in 15% of the test cases. The regression was caught before deployment.

## Production Implications
EDD is the only way to scale AI engineering teams. Without it, team members will argue over subjective changes ("I think this prompt is better"). EDD replaces opinions with data, allowing teams to refactor massive AI pipelines with the confidence that they haven't broken core functionality.

## Common Mistakes
- Building the application first and writing the evals months later. 
- Using synthetic data generated by an LLM as the *only* source for the golden dataset (it often lacks the messy complexity of real user data).
- Allowing flaky evals. If an LLM judge gives a different score on the exact same output across runs, developers will start ignoring the CI failures.

## Interview Questions
- **How does Eval-Driven Development differ from traditional Test-Driven Development?**
  *Answer:* TDD relies on exact, deterministic assertions (e.g., `assert output == 5`). EDD deals with non-deterministic outputs, requiring probabilistic metrics, LLM judges, and continuous tracking of aggregate scores over a dataset rather than binary pass/fail on every test.
- **Why is a sandbox environment critical for evaluating agents?**
  *Answer:* Agents execute side effects (writing files, calling APIs). A sandbox ensures that testing these actions during evaluation does not corrupt production data or incur massive real-world API costs.

## Further Reading
- [Shifting LLM Evaluation Left](https://www.wandb.courses/courses/building-llm-apps) — Concepts on bringing evaluation earlier into the development lifecycle.
""",
    "05-fine-tuning-evaluation/01-benchmarking-ft-models.md": """</Agent System Instructions>
<Benchmarking Fine-Tuned Models>
## TL;DR
Evaluating a fine-tuned model requires comparing it against its base model to prove that the fine-tuning actually improved task performance without degrading general capabilities. This is achieved using held-out test sets from the fine-tuning distribution and cross-distribution evaluation to test for generalization.

---

## The Baseline Comparison

Never evaluate a fine-tuned model in isolation. You must always run the exact same evaluation suite on the **base model** (e.g., Llama-3-8B) and the **fine-tuned model**. 
If the base model achieves 80% accuracy on your task with a 5-shot prompt, and your fine-tuned model achieves 82%, the expensive fine-tuning process was likely not worth the operational overhead.

## Evaluation Distributions

### 1. In-Distribution Evaluation (Held-out Test Set)
When creating a fine-tuning dataset, randomly hold out 10-20% of the data. 
- **Purpose:** Measures how well the model learned the specific format, tone, or task it was trained on.
- **Risk:** High scores here do not prove the model is good; they only prove the model memorized the specific style of the training data.

### 2. Out-of-Distribution Evaluation (Cross-Distribution)
Test the model on data that is related to the task but formatted differently or drawn from a different source.
- **Example:** If fine-tuned on Python code summarization, evaluate it on JavaScript code summarization.
- **Purpose:** Measures *generalization*. Did the model learn the underlying concept, or did it just overfit to the exact syntax of your training set?

### 3. General Capability Benchmarks (Regression Testing)
Run standard benchmarks (e.g., MMLU, standard conversational evals).
- **Purpose:** Checks for capability regression. Fine-tuning forcefully pushes model weights in a specific direction. You need to ensure you haven't destroyed the model's fundamental ability to speak English or reason logically. 
- *(Reference: → See [02-catastrophic-forgetting.md](./02-catastrophic-forgetting.md))*

## The "Tax" of Fine-Tuning
Fine-tuning often introduces an "alignment tax." A base model that is highly creative might become overly rigid and repetitive after being fine-tuned on a strict JSON-output task. Evaluation must capture whether this tradeoff is acceptable for your specific use case.

## Production Implications
Deploying a fine-tuned model without evaluating cross-distribution performance often leads to brittle systems. The model will perform flawlessly in demos (using data similar to the training set) but fail completely in production when users phrase their queries slightly differently than the training examples.

## Common Mistakes
- Evaluating the fine-tuned model on the training data (data leakage).
- Failing to establish a baseline with the base model, masking the fact that few-shot prompting might have been sufficient.
- Only measuring in-distribution performance and ignoring general capability regression.

## Interview Questions
- **Why is it critical to evaluate a fine-tuned model on an out-of-distribution dataset?**
  *Answer:* To ensure the model has actually generalized the task concepts rather than just overfitting to the specific format and phrasing of the training dataset.
- **What is capability regression in the context of fine-tuning?**
  *Answer:* It is when fine-tuning a model on a specific narrow task degrades its general reasoning, knowledge, or conversational abilities that were present in the base model.

## Further Reading
- [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685) — Understanding how parameter-efficient methods impact performance.
""",
    "05-fine-tuning-evaluation/02-catastrophic-forgetting.md": """</Agent System Instructions>
<Catastrophic Forgetting>
## TL;DR
Catastrophic forgetting occurs when a neural network is fine-tuned on a new task and abruptly forgets the knowledge or capabilities it learned during pre-training. In LLMs, this manifests as a model that excels at a narrow fine-tuned task but loses its ability to hold a normal conversation, follow general instructions, or reason.

---

## The Mechanism of Forgetting

During pre-training, an LLM's weights are carefully balanced across billions of parameters to encode a vast array of concepts. When you fine-tune the model on a narrow dataset (e.g., 10,000 examples of translating English to SQL), the gradient updates forcefully shift those weights to optimize for SQL generation. 
Because the model has finite capacity, the weights that previously encoded French translation or historical facts get overwritten.

## How to Detect It

You cannot detect catastrophic forgetting by evaluating the task you fine-tuned on. You must detect it by evaluating the tasks you *didn't* fine-tune on.
- **Baseline Check:** Run standard benchmarks (e.g., MMLU, MT-Bench) on the base model.
- **Post-FT Check:** Run the exact same benchmarks on the fine-tuned model.
- If the MMLU score drops from 70 to 45, catastrophic forgetting has occurred.

## Mitigation Strategies

### 1. Parameter-Efficient Fine-Tuning (PEFT / LoRA)
Instead of updating all billions of parameters (Full Fine-Tuning), techniques like LoRA (Low-Rank Adaptation) freeze the base model and only train a small, separate set of adapter weights.
- **Why it helps:** The base model's knowledge remains perfectly intact. The model is less likely to forget general capabilities because the foundational weights are physically locked.

### 2. Replay Buffers (Data Mixing)
When constructing your fine-tuning dataset, mix in a percentage (e.g., 10-20%) of general instruction-tuning data or data from previous tasks.
- **Why it helps:** It forces the model to calculate gradients that optimize for both the new task (SQL generation) and the old tasks (general conversation) simultaneously, preserving both.

### 3. Lower Learning Rates and Early Stopping
Aggressive learning rates cause massive weight updates, accelerating forgetting. Using a small learning rate and stopping the training process before the validation loss fully plateaus can preserve general knowledge.

### 4. Elastic Weight Consolidation (EWC)
A more advanced algorithmic approach that adds a penalty to the loss function if the model tries to heavily alter weights that were deemed "important" for previous tasks. (Less common in standard LLM fine-tuning, but foundational in continual learning).

## Production Implications
If you deploy a model suffering from catastrophic forgetting to a user-facing chatbot, it might answer domain-specific questions perfectly, but respond with gibberish or SQL code when the user says "Hello" or asks an off-topic question. It destroys the illusion of intelligence.

## Common Mistakes
- Doing full-parameter fine-tuning on a tiny dataset with a high learning rate.
- Only evaluating the fine-tuned model on the target task, hiding the fact that the model is now lobotomized for everything else.
- Assuming PEFT entirely eliminates forgetting (it reduces it significantly, but severe overfitting on the adapter can still hijack the model's outputs).

## Interview Questions
- **What is catastrophic forgetting, and how do you detect it in an LLM?**
  *Answer:* It is the loss of previously learned capabilities when training on new data. You detect it by running general benchmarks (like MMLU or conversational evals) before and after fine-tuning and measuring the degradation.
- **How does mixing data (replay) mitigate catastrophic forgetting?**
  *Answer:* By including examples of general tasks alongside the new domain-specific data, the loss function forces the model to update weights in a way that accommodates both, rather than completely overwriting old knowledge.

## Further Reading
- [Overcoming catastrophic forgetting in neural networks](https://arxiv.org/abs/1612.00796) — The foundational paper on the phenomenon in deep learning.
""",
    "06-evaluation-infrastructure/01-eval-pipelines.md": """</Agent System Instructions>
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
""",
    "06-evaluation-infrastructure/02-dataset-construction.md": """</Agent System Instructions>
<Dataset Construction>
## TL;DR
A model is only as good as the dataset used to evaluate it. Constructing a "golden dataset" requires balancing statistical significance, domain coverage, and real-world noise. While synthetic data generation can bootstrap the process, datasets must be continuously updated to prevent distribution drift and overfitting.

---

## The Golden Dataset

The golden dataset is the immutable ground-truth benchmark for your system. For a RAG or QA system, a single row typically contains:
- `query`: The input from the user.
- `context`: The optimal documents required to answer the query.
- `expected_output`: The ideal response.
- `metadata`: Difficulty level, topic category, or required tools.

## How Many Examples Do You Need?

A common mistake is evaluating on 10 examples. This lacks **statistical significance**. 
- If you have 10 examples, a change in 1 answer swings your score by 10%. You cannot measure incremental progress.
- **Rule of Thumb:** A robust eval set requires a minimum of 100-300 diverse examples. At 300 examples, a 2% improvement is statistically meaningful, indicating systemic progress rather than random variance.

## Synthetic Data Generation

Manually writing 300 highly complex, accurate QA pairs is exhausting. Synthetic generation uses powerful LLMs to bootstrap the dataset.
1. Feed the LLM your raw documents.
2. Prompt it to generate 5 queries of varying difficulty (e.g., factual, comparative, reasoning) based on those documents.
3. Have humans review, edit, and filter the synthetic queries.

*Warning:* If you rely 100% on synthetic data, your eval set will lack the messy reality of human users (typos, slang, ambiguous phrasing). It evaluates how well your model talks to another AI, not to humans.

## Distribution Coverage and Adversarial Examples

A robust dataset must deliberately cover the entire input distribution:
- **Happy Path:** Standard queries that should easily succeed.
- **Edge Cases:** Queries requiring information spread across multiple documents.
- **Adversarial / Out of Bounds:** Queries trying to jailbreak the prompt, or asking questions entirely outside the system's knowledge base. (The correct behavior here is a graceful refusal, which must be evaluated).

## Dataset Drift

In production, user behavior changes over time. If your evaluation dataset is completely static, you will optimize for yesterday's problems.
- **Continuous Updating:** Every week, sample 10 queries from production that the model failed on (e.g., queries that received a thumbs-down from users). Manually write the expected optimal answer and add them to the golden dataset. This ensures the eval suite evolves alongside user behavior.

## Production Implications
Optimizing a prompt to achieve 100% on a poorly constructed, unrepresentative golden dataset guarantees production failure. This is classic "overfitting to the eval." The team celebrates high metrics internally, while users experience a broken product.

## Common Mistakes
- Using the exact same dataset for few-shot prompting and for evaluation (data leakage).
- Focusing only on "happy path" queries and ignoring adversarial or ambiguous inputs.
- Never updating the golden dataset after the initial launch.

## Interview Questions
- **Why is a golden dataset of 10 examples insufficient for evaluating an AI system?**
  *Answer:* It lacks statistical significance. A single random failure or success causes a 10% swing in metrics, making it impossible to confidently measure small, incremental improvements or detect minor regressions.
- **What is the risk of using purely synthetic data to construct an evaluation dataset?**
  *Answer:* Synthetic data often lacks the nuance, ambiguity, and messy formatting of real human queries. It tests how well the system responds to perfectly phrased AI prompts rather than real-world users.

## Further Reading
- [Building a Golden Dataset for Evaluation](https://huggingface.co/blog/evaluation-golden-dataset) — Practical guides on data curation.
"""
}

def ensure_dir(path):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

base_dir = r"G:\CS\ai-engineering\05-evaluation"

for filename, content in files.items():
    full_path = os.path.join(base_dir, filename.replace("/", os.sep))
    ensure_dir(full_path)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Successfully generated {len(files)} files.")
