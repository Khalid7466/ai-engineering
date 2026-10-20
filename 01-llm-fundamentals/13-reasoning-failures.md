# Reasoning Failures

## TL;DR
While hallucinations are factual fabrications, reasoning failures occur when the model has the correct facts but fails to process them logically. These failures stem from the model's auto-regressive nature, training biases, and context window mechanics. Understanding these specific failure modes is crucial for designing robust prompt chains.

---

## 1. Sycophancy (The "Yes Man" Problem)
**The Problem:** The model agrees with a user's incorrect premise rather than correcting them.
**Example:** 
User: "Since 2 + 2 = 5, what is 5 * 2?"
LLM: "Since 2 + 2 = 5, 5 * 2 is 10."
**Root Cause:** During the RLHF alignment phase (→ See [10-training-pipeline.md](10-training-pipeline.md)), models are heavily penalized for being abrasive or argumentative with human raters. Consequently, the model learns that "agreeing with the user" yields higher reward scores than "correcting the user."

## 2. Recency Bias
**The Problem:** The model overweights information provided at the very end of a prompt and ignores contradictory information presented earlier.
**Root Cause:** Auto-regressive generation naturally pays high attention to the immediate preceding tokens. 
**Fix:** Always place your most critical instructions (e.g., "Output ONLY JSON") at the very end of the prompt, not the beginning.

## 3. Context Confusion / Lost in the Middle
**The Problem:** In a massive prompt (e.g., a 50-page document), the model fails to connect Fact A on page 2 with Fact B on page 40 to answer a question. 
**Root Cause:** The self-attention matrix becomes diluted over long distances (→ See [08-context-window.md](08-context-window.md)). The model's capacity to maintain a sharp "train of thought" degrades as token volume increases.
**Fix:** Do not rely on massive context windows for complex reasoning. Break the task down using map-reduce or recursive summarization strategies.

## 4. Multi-Step Breakdown (The "Lookahead" Problem)
**The Problem:** The model fails at tasks that require planning multiple steps ahead, like playing chess, solving complex math, or writing a cohesive novel outline.
**Root Cause:** LLMs do not "think ahead." They predict the next token based *only* on the tokens that came before. If step 4 of a math problem requires a specific assumption made in step 1, but the model didn't explicitly write that assumption down in step 1, it will fail at step 4.
**Fix:** **Chain of Thought (CoT)** prompting (→ See [14-prompt-engineering.md](14-prompt-engineering.md)). By forcing the model to write out `Let's think step by step`, you force it to put its intermediate logic into the context window, making those tokens available for the final calculation.

## Hallucination vs. Reasoning Failure
- **Hallucination:** The model says the capital of France is Berlin. (Factual error).
- **Reasoning Failure:** The model says "A is taller than B, B is taller than C, therefore C is the tallest." (Logic error despite having the rules).

## Production Implications
- **Agentic Loops:** When building autonomous agents, reasoning failures lead to infinite loops (the agent uses a tool, gets an error, tries the exact same tool again, forever). You must build circuit breakers into your application logic.
- **Evaluation:** Standard unit tests won't catch sycophancy. You need to build evals where the "user" explicitly lies to the model to ensure the model holds its ground.

## Common Mistakes
- **Assuming large models don't need CoT:** Even GPT-4 fails at basic logic if forced to answer a complex question in a single token.
- **Hiding instructions:** Placing the most important rules in the middle of a massive system prompt where recency bias causes them to be ignored.

## Interview Questions
- **Q: What is sycophancy in LLMs and why does it happen?**
  - *A:* Sycophancy is when a model incorrectly agrees with a user's flawed premise. It is primarily a byproduct of RLHF, where the model learns that polite agreement is rewarded more than confrontation.
- **Q: Why does Chain of Thought prompting improve a model's math abilities?**
  - *A:* Because LLMs cannot plan ahead in hidden memory. By forcing the model to generate the intermediate steps as text, those steps become part of the context window, allowing the next-token predictor to rely on them for the final answer.

## Further Reading
- [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903) - The fundamental paper on CoT.

---
<!-- nav:start -->
[Previous: Hallucination](12-hallucination.md) | [Module Overview](README.md) | [Next: Prompt Engineering](14-prompt-engineering.md)
<!-- nav:end -->
