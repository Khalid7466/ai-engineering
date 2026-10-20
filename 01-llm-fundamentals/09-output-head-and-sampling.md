# Output Head and Sampling

## TL;DR
After a token passes through all Transformer blocks, it ends up as a massive vector of raw numbers. The Output Head and sampling algorithms are responsible for converting this math into the actual text you see. Understanding parameters like Temperature, Top-P, and Top-K allows you to control whether the model behaves like a strict data-extractor or a creative storyteller.

---

## Logits to Probabilities (Softmax)
The final layer of the Transformer is the **Language Modeling Head**. It multiplies the final token vector by an embedding matrix to produce a score for every single token in the vocabulary (e.g., 128,000 scores). 

These raw scores are called **Logits**. They can be positive, negative, large, or small.
To make sense of them, they are passed through a **Softmax** function, which normalizes the logits into a probability distribution that sums to 1.0 (100%).

Example distribution for the next token after "The color of the sky is":
- ` blue`: 90%
- ` gray`: 8%
- ` red`: 1.9%
- ` pineapple`: 0.0001%

## Sampling Parameters
If we always picked the 90% probability token, the model would be deterministic but incredibly boring and prone to repetitive loops. To fix this, we sample from the distribution using algorithms controlled by API parameters.

### 1. Temperature
Temperature rescales the logits *before* the Softmax function is applied.
- `T = 1.0`: Default. The distribution is unchanged.
- `T < 1.0`: The distribution becomes sharper. High probabilities get higher, low probabilities drop near zero. 
- `T = 0.0`: Greedy decoding. The model will *always* pick the most probable token.
- `T > 1.0`: The distribution flattens. Lower probability tokens become much more likely, increasing creativity but also increasing the risk of gibberish.

### 2. Top-K Sampling
Before sampling, sort the probabilities and discard everything except the top $K$ tokens.
If $K=40$, the model can only choose from the 40 most likely next words. This prevents the model from accidentally picking the "pineapple" tail-end token during a high-temperature generation.

### 3. Top-P (Nucleus) Sampling
Instead of a fixed number $K$, Top-P sorts the tokens and keeps adding them to a pool until their cumulative probability equals $P$.
If $P=0.9$, and "blue" is 90%, the pool only contains "blue". 
If the top 10 tokens are 9% each, the pool contains all 10. 
Top-P dynamically adjusts the pool size based on how confident the model is.

*Rule of Thumb: Do not adjust both Temperature and Top-P at the same time. Alter one and leave the other at default.*

## Beam Search
Standard autoregressive generation picks one token, commits to it, and moves on. This can lead to dead ends.
**Beam Search** maintains multiple parallel branches (beams) of generation. It generates the next token for Branch A, B, and C, calculates the total probability of each *sequence*, and drops the least likely branches. It is highly effective for translation or rigid tasks, but rarely used in modern chat APIs because it is computationally expensive and reduces conversational fluency.

## Production Implications
- **Data Extraction & Classification:** When using an LLM to parse JSON, extract entities, or classify text, ALWAYS set `temperature=0.0`. You want maximum determinism. (→ See [use-case.md](use-case.md))
- **Brainstorming & Copywriting:** For creative tasks, use `temperature=0.7` to `1.0`.
- **Caching:** API caching only works reliably if generations are deterministic. High temperature makes identical prompts yield different outputs, breaking cache hits.

## Common Mistakes
- **Assuming `temperature=0` means zero hallucinations:** It only means the model selects the most likely token. If the model's most likely sequence based on its training is a hallucination, it will consistently hallucinate the exact same lie.
- **Using high temperature for RAG:** If you provide context and ask the model to answer *only* from the text, high temperature might cause it to pick a slightly less probable word that deviates from the text, leading to a hallucination.

## Interview Questions
- **Q: What is the difference between Top-K and Top-P sampling?**
  - *A:* Top-K restricts the sample pool to a fixed number of the highest probability tokens. Top-P restricts the pool to the minimum number of tokens whose cumulative probability exceeds P. Top-P is dynamic, adapting the pool size based on the model's confidence distribution.
- **Q: Why would you set Temperature to 0?**
  - *A:* To force greedy decoding, making the model deterministic by always selecting the highest probability token. This is crucial for tasks requiring strict adherence to formats (JSON), factual data extraction, or classification.

## Further Reading
- [How to generate text: using different decoding methods](https://huggingface.co/blog/how-to-generate) - Hugging Face guide on sampling techniques.

---
<!-- nav:start -->
[Previous: Context Window and the KV Cache](08-context-window.md) | [Module Overview](README.md) | [Next: Training Pipeline](10-training-pipeline.md)
<!-- nav:end -->
