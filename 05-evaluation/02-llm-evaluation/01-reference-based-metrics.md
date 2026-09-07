</Agent System Instructions>
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
