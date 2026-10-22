# What is an LLM?

## TL;DR
A Large Language Model (LLM) is fundamentally a massive statistical engine optimized for a single task: predicting the most likely next word (token; see [02-tokenization.md](02-tokenization.md)) given a sequence of preceding words. Despite this simple objective, at sufficient scale (billions of parameters and trillions of training tokens), these models develop emergent capabilities like reasoning, summarization, and translation.

---

## The Next-Token Prediction Objective
At its core, an LLM is a function: `f(context) = P(next_token | context)`. The model outputs a probability distribution; a separate step picks the token.
When you type "The quick brown fox jumps over the lazy", the model calculates the probability distribution for the next token and determines that "dog" is highly probable.

This mechanism is iterative (auto-regressive). To generate a paragraph, it predicts one token, appends it to the context, and runs the model again to predict the *next* token.

```python
# Conceptual pseudocode for autoregressive generation
def generate(prompt, max_tokens):
    context = prompt
    for _ in range(max_tokens):
        # The model returns probabilities for all possible next tokens
        probabilities = model.forward(context) 
        
        # We pick the most likely token (simplification)
        next_token = select_highest_probability(probabilities)
        
        context += next_token
        
        if next_token == "<EOS>": # End of Sequence token
            break
    return context
```

> Note: this is a simplification. Real systems do not recompute the whole
> context at every step; they cache previous keys and values (the KV cache,
> see [08-context-window.md](08-context-window.md)). They also usually sample
> instead of always taking the highest probability (see
> [09-output-head-and-sampling.md](09-output-head-and-sampling.md)).

## Scale and Emergent Capabilities
If next-token prediction is just fancy autocomplete, why can LLMs write code or translate between languages? A leading explanation is **scale**.

When researchers scaled up both the model size (parameters) and the dataset size (training data), models became able to do tasks they were never explicitly trained for. To predict the next word well in a physics paper, a Python script, or a logic puzzle, it helps the model to build internal representations of physics, programming syntax, and logic, so the training objective pushes it in that direction. These abilities are often called **emergent capabilities**.

> **Caveat:** whether these abilities appear suddenly at a certain scale is debated. Schaeffer et al. (2023) argue that many apparent jumps come from the metrics used to measure them, and that performance improves more smoothly than it first seems. Treat "emergence" as a useful description, not a settled law.

## The Brain in a Jar Analogy
An LLM is like a highly intelligent brain in a jar. It has read the entire internet, but it has no real-world experience, no sense of time, no persistent memory between sessions, and no active agency unless hooked up to external tools. 

When you ask it a question, it is not "thinking" in the human sense; it is performing a massive sequence of matrix multiplications to satisfy its training objective.

## Training Objective vs. Truth
During pre-training, an LLM's objective is to be **plausible**, not **truthful**: it is rewarded for predicting likely text, not for being correct. Later stages (see [10-training-pipeline.md](10-training-pipeline.md)) push it toward being helpful and honest, but they do not turn it into a fact-checker.

The model does store a lot of knowledge in its weights (see [07-feed-forward-network.md](07-feed-forward-network.md)), but that storage is compressed and approximate. It has no reliable lookup mechanism and no built-in way to know when it does not know. If you ask about a niche topic, it will confidently generate a statistically likely sequence of words that *sounds* like a correct answer, even if the facts are entirely fabricated (→ See [12-hallucination.md](12-hallucination.md)).

## Production Implications
- **Lack of Determinism:** Because it is a probabilistic engine, identical inputs can yield different outputs. Setting temperature to 0 reduces this but does not guarantee identical outputs (GPU floating-point behavior, batching, and some architectures can still change results). Build validation and error handling into your application layer.
- **Latency:** Because generation is auto-regressive, predicting 1000 tokens requires running the massive model 1000 times sequentially. This is why LLMs stream their output token-by-token and why generating long outputs is inherently slow.
- **Statelessness:** The model does not remember your previous API calls. You must pass the entire conversation history back to the model with every request, consuming more context window and driving up costs.

## Common Mistakes
- **Assuming an LLM is a database:** Engineers often expect models to recall specific facts accurately. Use RAG when you need private, recent, or verifiable facts; the model's weights alone are unreliable for exact recall.
- **Expecting human-like reasoning:** LLMs can mimic reasoning, but they fail on simple tasks (like counting letters in a word) (see [02-tokenization.md](02-tokenization.md)) because their internal representation of text is fundamentally different from ours.
- **Ignoring the auto-regressive bottleneck:** Assuming you can quickly generate a massive 10-page report synchronously. Use streaming or background jobs (see [09-output-head-and-sampling.md](09-output-head-and-sampling.md) for how generation proceeds token by token).

## Interview Questions
- **Q: Explain how an LLM generates a paragraph of text.** 
  - *A:* It generates text auto-regressively. It takes the input prompt, calculates the probability distribution for the next token, samples a token, appends it to the prompt, and repeats this process until an End-Of-Sequence token is generated or a length limit is reached.
- **Q: Why does scaling a model improve its ability to perform tasks it wasn't explicitly trained for?**
  - *A:* To predict the next token accurately across diverse, complex data (code, math, logic), it helps the model to learn general patterns and representations instead of memorizing word frequencies. This is why larger models often handle tasks they were not explicitly trained for (zero-shot), although whether these abilities appear suddenly or gradually is still debated.

## Further Reading
- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/) - Visual guide to the underlying architecture.
- [Emergent Abilities of Large Language Models](https://arxiv.org/abs/2206.07682) - Paper discussing how capabilities emerge at scale.
- [Are Emergent Abilities of Large Language Models a Mirage?](https://arxiv.org/abs/2304.15004) - A critique of the emergence claim; read it alongside the paper above.

---
<!-- nav:start -->
[Module Overview](README.md) | [Next: Tokenization](02-tokenization.md)
<!-- nav:end -->
