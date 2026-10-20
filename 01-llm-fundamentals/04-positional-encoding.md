# Positional Encoding

## TL;DR
Unlike older RNNs which read text sequentially, Transformers process all tokens in a prompt simultaneously (in parallel). Without positional encoding, a Transformer would see "Dog bites man" and "Man bites dog" as the exact same "bag of words." Positional encoding injects information about the order of tokens into their embeddings so the model can understand sequence and syntax.

---

## Why Order Matters
Self-attention (→ See [06-self-attention.md](06-self-attention.md)) compares every token to every other token at the same time. The operation is mathematically permutation-invariant. If you shuffle the words in a sentence, the standard attention mechanism would output the same representations, just shuffled. 

To fix this, we must add a "timestamp" or "position index" to each token's embedding before it enters the Transformer blocks.

## Absolute Positional Encoding (The Original Approach)
In the original "Attention Is All You Need" paper, researchers used sine and cosine functions of different frequencies to generate a unique vector for every position (1st word, 2nd word, etc.). 
This position vector is literally *added* (element-wise) to the word embedding vector. 
`Final_Input = Token_Embedding + Positional_Encoding`

**The problem:** Absolute positioning struggles to generalize to sequences longer than what it saw during training, and it rigidly ties a word to an absolute index (e.g., index 5) rather than its relative distance to other words.

## Modern Approaches: RoPE and ALiBi
Modern LLMs have shifted away from absolute encodings to relative encodings, which care more about the *distance* between two tokens rather than their absolute position in the document.

### Rotary Positional Embedding (RoPE)
Used by Llama, PaLM, and many modern models. Instead of adding a vector, RoPE *rotates* the token embeddings in the multi-dimensional space based on their position. The dot product (attention score) between two tokens then naturally becomes a function of their relative distance. RoPE is highly effective and allows for easier extension of context windows via techniques like "RoPE scaling."

### ALiBi (Attention with Linear Biases)
Instead of modifying the embeddings, ALiBi directly modifies the attention matrix. It applies a penalty (a negative bias) to the attention scores between tokens that is proportional to the distance between them. Tokens far away pay less attention to each other. ALiBi is extremely good at extrapolating to longer context windows without fine-tuning.

## Positional Encoding and Context Length
The context window limit of an LLM (e.g., 8k, 128k) is heavily tied to its positional encoding. If a model was trained on 4k token sequences using standard RoPE, feeding it 8k tokens means it encounters position indices it has never seen before, causing catastrophic failure (gibberish output).

## Production Implications
- **Context Window Extension:** When open-source communities take a Llama model (8k context) and release a "128k context" version, they are usually applying RoPE scaling (interpolating the rotational angles) and doing a light fine-tune.
- **RAG Document Ordering:** Because of positional biases, LLMs pay more attention to the beginning and end of a sequence than the middle (the "Lost in the Middle" phenomenon). The type of positional encoding used influences how severe this bias is.

## Common Mistakes
- **Assuming Transformers read left-to-right:** They process the entire prompt in a single parallel forward pass. Only the generation phase is sequential.
- **Ignoring sequence length limits:** Pushing tokens beyond the model's trained positional encoding limit will not result in a graceful degradation; it results in immediate mathematical breakdown and hallucinated gibberish.

## Interview Questions
- **Q: Why do Transformers need positional encoding?**
  - *A:* Because the core self-attention mechanism processes all tokens in parallel and is permutation-invariant. Without positional encoding, the model cannot distinguish between "Dog bites man" and "Man bites dog."
- **Q: What is the difference between absolute positional encoding and RoPE?**
  - *A:* Absolute encoding adds a fixed sine/cosine vector representing the exact index (1, 2, 3) to the token embedding. RoPE rotates the vectors in space such that the attention between two tokens depends only on their relative distance to one another, which generalizes better to longer sequences.

## Further Reading
- [RoPE Paper (RoFormer)](https://arxiv.org/abs/2104.09864) - The mathematical foundation of Rotary Positional Embeddings.

---
<!-- nav:start -->
[Previous: Embeddings](03-embeddings.md) | [Module Overview](README.md) | [Next: Transformer Architecture](05-transformer-architecture.md)
<!-- nav:end -->
