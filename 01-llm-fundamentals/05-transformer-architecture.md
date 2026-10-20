# Transformer Architecture

## TL;DR
The Transformer is the neural network architecture underlying all modern LLMs. It revolutionized AI by abandoning sequential processing (RNNs) in favor of a highly parallelizable structure built around the "Self-Attention" mechanism. This allowed models to scale massively using GPUs, leading to the AI boom.

---

## Why RNNs Failed
Before 2017, sequence tasks were handled by Recurrent Neural Networks (RNNs) and LSTMs. They processed text one word at a time, updating a "hidden state" (memory) as they went.
**Failures:**
1. **Vanishing Gradients/Forgetting:** By the time an RNN reached the end of a long paragraph, the hidden state had "forgotten" the beginning.
2. **No Parallelism:** Because step $T$ required the output of step $T-1$, training could not be parallelized across GPUs. You had to process sequentially.

## The Transformer Solution
The Transformer (introduced in "Attention Is All You Need") processes the entire sequence of tokens simultaneously. 
Instead of a sequential hidden state, it uses **Self-Attention** to allow every token to look directly at every other token to gather context, regardless of distance. Because it relies on matrix multiplication rather than sequential loops, it is perfectly suited for modern GPU hardware.

## Encoder, Decoder, and Encoder-Decoder Architectures

The original Transformer had two parts, designed for translation tasks:

### 1. Encoder-Only (e.g., BERT)
- **Mechanism:** Tokens can see all other tokens in the sequence (Bidirectional).
- **Use Case:** Great for understanding context, classification, and generating RAG embeddings. 
- **Limitation:** Bad at generating new text.

### 2. Decoder-Only (e.g., GPT series, Llama, Claude)
- **Mechanism:** Tokens can only see previous tokens, not future ones (Causal or Masked Attention). 
- **Use Case:** Perfect for auto-regressive generation (next-token prediction).
- **Dominance:** Almost all modern generative LLMs are Decoder-only architectures. They proved that scaling a simple left-to-right predictor yields better general-purpose models than complex encoder-decoder setups.

### 3. Encoder-Decoder (e.g., T5, BART)
- **Mechanism:** The Encoder reads the input bidirectionally, passes representations to the Decoder, which generates output causally.
- **Use Case:** Translation, summarization.

## How Blocks Stack
A Decoder-only LLM (like Llama 3) consists of many identical "Transformer Blocks" stacked on top of each other (e.g., 32 blocks, 80 blocks).

**Inside a single block:**
1. **Input:** Token vectors (with positional encoding).
2. **Self-Attention Layer:** Tokens share information and update their vectors based on context. (→ See [06-self-attention.md](06-self-attention.md))
3. **Add & Norm (Residual Connection):** The original input is added to the attention output to prevent gradient vanishing, followed by Layer Normalization.
4. **Feed-Forward Network (FFN):** A dense neural network processes each token vector independently. (→ See [07-feed-forward-network.md](07-feed-forward-network.md))
5. **Add & Norm:** Another residual connection.
6. **Output:** The vectors are passed to the next block.

As a token passes through 80 layers, its vector transforms from a simple dictionary definition into a deeply contextualized representation containing logic, syntax, and relational meaning.

## Production Implications
- **VRAM Requirements:** Stacking 80 blocks of massive matrices requires enormous amounts of VRAM just to load the model weights, which is why serving open-source models is expensive and requires multi-GPU setups.
- **Compute vs. Memory Bound:** The pre-fill phase (processing the prompt in parallel) is compute-bound. The generation phase (generating tokens one by one) is memory-bandwidth bound, as the massive weights must be loaded from VRAM to compute cores for every single token.

## Common Mistakes
- **Assuming ChatGPT uses the original Transformer:** People often assume ChatGPT has an Encoder. It does not; it is a purely Decoder-only architecture.
- **Thinking tokens are reduced to a single vector:** The Transformer maintains a sequence of vectors. A 1000-token prompt maintains 1000 distinct vectors as it passes through all layers.

## Interview Questions
- **Q: Why did Transformers replace LSTMs and RNNs?**
  - *A:* Transformers eliminated sequential processing bottlenecks, allowing for massive parallelization on GPUs. They also solved the long-term dependency problem by allowing direct attention between any two tokens, regardless of distance.
- **Q: What is the difference between an Encoder-only and Decoder-only architecture?**
  - *A:* Encoders allow bidirectional attention (tokens see past and future), making them good for classification and embeddings. Decoders enforce causal masking (tokens only see the past), making them suited for next-token generation.

## Further Reading
- [The Annotated Transformer](http://nlp.seas.harvard.edu/2018/04/03/attention.html) - Line-by-line implementation of the original paper in PyTorch.

---
<!-- nav:start -->
[Previous: Positional Encoding](04-positional-encoding.md) | [Module Overview](README.md) | [Next: Self-Attention](06-self-attention.md)
<!-- nav:end -->
