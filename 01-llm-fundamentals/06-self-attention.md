# Self-Attention

## TL;DR
Self-attention is the mechanism that allows a Transformer to understand context. It lets every word in a sequence look at every other word to determine which ones are relevant to its own meaning. This is how the model knows that the word "it" in "The animal didn't cross the street because it was too tired" refers to the animal, not the street.

---

## The QKV Mechanics
Self-attention operates using a database retrieval analogy: Queries (Q), Keys (K), and Values (V). 
For every token in the sequence, the model creates three distinct vectors by multiplying the token's embedding by three learned weight matrices ($W_q, W_k, W_v$).

1. **Query (Q):** What I am looking for. (e.g., The token "it" creates a query searching for a singular noun).
2. **Key (K):** What I contain. (e.g., The token "animal" creates a key saying "I am a singular noun").
3. **Value (V):** What I actually mean / my core information.

### The Step-by-Step Calculation
1. **Dot Product:** The model calculates the dot product between the Query of token A and the Keys of all other tokens. A high dot product means a strong match.
2. **Scale and Softmax:** The scores are scaled down (divided by $\sqrt{d_k}$) to prevent gradients from exploding, and then passed through a Softmax function. This turns the scores into percentages that sum to 1.0. (e.g., "it" pays 80% attention to "animal", 15% to "street", 5% to other).
3. **Weighted Sum:** The model multiplies the Value (V) of each token by its Softmax score, and adds them all together. 
4. **Update:** The resulting vector becomes the new, updated representation of token A. The token "it" now contains the semantic essence of "animal".

*Formula:* $Attention(Q, K, V) = softmax(\frac{QK^T}{\sqrt{d_k}})V$

## Masked Self-Attention
Because LLMs (like GPT) are Decoder-only, they must predict the *next* token. If a token could look at future tokens during training, it would "cheat." Therefore, a causal mask (a matrix of negative infinities) is applied before the Softmax step, ensuring token $N$ can only pay attention to tokens $1$ through $N$.

## Multi-Head Attention
A single attention mechanism might learn to connect pronouns to nouns. But what about connecting adjectives to nouns? Or verbs to subjects?
Transformers use **Multi-Head Attention**. Instead of one set of Q,K,V matrices, they have many (e.g., 32 heads or 64 heads). 

Each head operates independently in parallel, learning different linguistic, syntactical, or logical relationships. The outputs of all heads are concatenated back together. 

## Production Implications
- **Quadratic Complexity:** The calculation $QK^T$ compares every token to every other token. This creates an $N^2$ matrix (where N is sequence length). If you double the context window, the compute and memory required for self-attention quadruples. This is the primary bottleneck for scaling context windows.
- **Grouped Query Attention (GQA):** To save memory during inference, modern models (like Llama 3) use GQA. Instead of every head having its own Key and Value matrices, multiple Query heads share a single set of Keys and Values. This drastically reduces the VRAM needed for the KV Cache (→ See [08-context-window.md](08-context-window.md)).

## Common Mistakes
- **Assuming attention relies on distance:** Without positional encoding, self-attention treats tokens 1 and 1000 with the exact same proximity. Attention is purely semantic matching unless positional biases (like RoPE/ALiBi) are applied.
- **Thinking Multi-Head Attention scales linearly in time:** The computations are done in parallel across GPU cores, but the memory footprint scales linearly with the number of heads, creating VRAM bottlenecks.

## Interview Questions
- **Q: Explain the roles of Queries, Keys, and Values in self-attention.**
  - *A:* Query is what a token is looking for, Key is what a token represents, and Value is the actual information the token contains. Attention scores are calculated by matching Queries to Keys, and the output is a weighted sum of the Values.
- **Q: Why does the self-attention operation have $O(N^2)$ complexity?**
  - *A:* Because the self-attention mechanism must calculate the dot product between the Query of every token and the Key of every token in the sequence of length N, resulting in an $N \times N$ attention matrix.

## Further Reading
- [FlashAttention](https://arxiv.org/abs/2205.14135) - A hardware-aware algorithm that significantly speeds up the exact attention calculation and reduces memory usage, enabling modern long-context models.

---
<!-- nav:start -->
[Previous: Transformer Architecture](05-transformer-architecture.md) | [Module Overview](README.md) | [Next: Feed-Forward Network (FFN)](07-feed-forward-network.md)
<!-- nav:end -->
