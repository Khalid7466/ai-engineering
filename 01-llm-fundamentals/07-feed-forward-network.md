# Feed-Forward Network (FFN)

## TL;DR
If Self-Attention is how tokens look at each other to gather context, the Feed-Forward Network (FFN) is where individual tokens process that gathered context to make decisions. It acts as a massive key-value memory bank storing facts and learned logic, independently applied to every token position.

---

## "What to do with what you looked at"
Inside a Transformer block, the Self-Attention layer happens first, mixing information between tokens. The output of the attention layer is then passed into the FFN.

While attention is a global operation (tokens interacting with other tokens), the FFN is a local, position-wise operation. The exact same FFN neural network is applied independently to token 1, token 2, token 3, etc. 

**Conceptual flow:**
1. **Attention:** The word "Paris" looks around the sentence and sees "Capital" and "France". Its vector is updated to reflect this context.
2. **FFN:** The updated "Paris" vector enters the FFN. The FFN acts as a non-linear memory and says, "Ah, a vector representing the capital of France? Let me activate the internal weights that associate this with 'Eiffel Tower' or 'Croissant'."

## Architecture of the FFN
The standard FFN consists of two linear transformations (dense layers) separated by a non-linear activation function (like ReLU, GELU, or SwiGLU).

1. **Expansion:** The first layer projects the token vector into a much higher-dimensional space (often 4x the dimension of the embedding). This creates massive capacity to store patterns and facts.
2. **Activation:** The non-linear function filters the information, activating only the relevant pathways.
3. **Compression:** The second layer projects the vector back down to the original embedding dimension.

*Roughly two-thirds of an LLM's parameters (the actual gigabytes of weights on the GPU) live in the Feed-Forward Networks.* They are the primary storage for the model's world knowledge.

## Mixture of Experts (MoE)
As models scale, making the FFN larger becomes too computationally expensive. The modern solution is Mixture of Experts (MoE), famously used by Mixtral 8x7B and GPT-4.

Instead of one massive FFN, an MoE layer has several smaller, specialized FFNs (Experts) and a Router network. 
For every token, the Router decides which 1 or 2 Experts are best suited to process it. 

**Why it matters:** 
- A dense 80B model activates 80B parameters for every token.
- An 8x10B MoE model (80B total parameters) might only route a token to 2 experts, meaning it only activates 20B parameters per token. 
This decoupling of parameter count (knowledge capacity) from active compute (latency/cost) is a massive efficiency breakthrough.

## Production Implications
- **Cost of Knowledge:** Because the FFNs hold the world knowledge and make up the bulk of the parameters, models that know lots of facts are inherently massive, requiring expensive GPUs. 
- **MoE Latency vs. VRAM:** MoE models are fast (low active parameters) but still require massive VRAM because all experts must be loaded into memory. You cannot run Mixtral 8x7B on a laptop with 8GB of VRAM, even though it runs at the speed of a 14B model.

## Common Mistakes
- **Ignoring the FFN:** Focusing entirely on Attention and forgetting that the FFN contains the actual parameters that dictate the model's knowledge.
- **Misunderstanding MoE routing:** Assuming an MoE routes a whole prompt to an expert (e.g., "send this coding prompt to the coding expert"). Routing happens on a *per-token* basis at *every layer*. A single sentence will be processed by many different experts.

## Interview Questions
- **Q: What is the difference between the Self-Attention layer and the Feed-Forward layer in a Transformer block?**
  - *A:* Self-attention allows tokens to interact and share context with each other. The FFN processes each token independently, acting as a massive non-linear memory bank to recall facts and patterns based on the gathered context.
- **Q: Explain the primary benefit of a Mixture of Experts (MoE) architecture.**
  - *A:* MoE decouples a model's total parameter count (its capacity for knowledge) from its active parameter compute cost. It allows for a massive model that runs with the speed and compute cost of a much smaller model.

## Further Reading
- [Transformer Feed-Forward Layers Are Key-Value Memories](https://arxiv.org/abs/2012.14913) - Paper exploring how FFNs store factual knowledge.

---
<!-- nav:start -->
[Previous: Self-Attention](06-self-attention.md) | [Module Overview](README.md) | [Next: Context Window and the KV Cache](08-context-window.md)
<!-- nav:end -->
