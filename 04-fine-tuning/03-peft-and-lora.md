# PEFT and LoRA

## TL;DR
Full fine-tuning of Large Language Models is computationally prohibitive due to the massive GPU memory required for optimizer states and gradients. Parameter-Efficient Fine-Tuning (PEFT) methods solve this by freezing the original model weights and training only a tiny number of new parameters. **LoRA (Low-Rank Adaptation)** is the industry standard PEFT method, achieving near-parity with full fine-tuning while reducing hardware requirements by up to 90%.

---

## Why Full Fine-Tuning is Prohibitive

To understand why PEFT is necessary, you must understand GPU memory math. → See [06-fine-tuning-infrastructure.md](06-fine-tuning-infrastructure.md).

For a 7 Billion parameter model (like Llama-3-8B):
- **Model Weights (FP16):** ~14 GB
- **Gradients (FP16):** ~14 GB
- **Optimizer States (Adam, FP32):** ~56 GB (Adam tracks momentum and variance for *every* parameter in 32-bit).

Total memory for full fine-tuning a 7B model exceeds 80GB. This means you cannot train it on a standard consumer GPU (like a 24GB RTX 4090) or a single cloud instance like an A10G (24GB). You would need multiple high-end A100s.

## Enter PEFT: Low-Rank Adaptation (LoRA)

**LoRA (Low-Rank Adaptation)** bypasses this memory bottleneck. Instead of updating the massive original weight matrices of the model, LoRA:
1. **Freezes** the original base model weights.
2. **Injects** two small, trainable matrices (A and B) alongside the original weights.
3. During the forward pass, the input is multiplied by both the frozen original weights and the new A/B matrices. The results are added together.

### The Math Intuition
If a model's original weight matrix ($W$) has dimensions $10,000 \times 10,000$, it contains 100 million parameters.

LoRA represents the weight update ($\Delta W$) as the product of two low-rank matrices: $A$ and $B$.
- Matrix $A$ has dimensions $10,000 \times r$
- Matrix $B$ has dimensions $r \times 10,000$

Where $r$ is the **Rank** (a small number, typically 8, 16, or 64). 
If $r = 8$, matrices A and B combined only have $160,000$ parameters. We are now training $160,000$ parameters instead of $100,000,000$ — a 99.8% reduction in trainable parameters, and proportionally less memory needed for optimizer states.

### QLoRA (Quantized LoRA)
QLoRA takes LoRA a step further. 
1. The frozen base model is loaded into 4-bit precision (NormalFloat4), drastically reducing the base memory footprint (from ~14GB down to ~4GB for a 7B model).
2. The small LoRA matrices are kept in 16-bit (BF16) precision to maintain training stability.

QLoRA allows you to fine-tune a 7B model on a single 16GB GPU, or a 70B model on two 24GB GPUs. It is the de-facto standard for indie developers and resource-constrained engineering teams.

## LoRA Hyperparameters: Rank ($r$) and Alpha ($\alpha$)

When configuring LoRA, you must set several critical hyperparameters:

1. **Rank ($r$):** Determines the size of the injected matrices (the bottleneck). 
   - $r=8$: Good for simple classification or basic style transfer.
   - $r=16$ or $32$: The standard default. Good for most domain adaptations.
   - $r=64$ or $128$: Used for complex reasoning tasks or learning entirely new languages. (Diminishing returns apply heavily past 64).
2. **Alpha ($\alpha$):** A scaling factor that determines how much the LoRA weights influence the base model.
   - **Rule of Thumb:** Usually set $\alpha = 2 \times r$. If $r=16$, set $\alpha=32$.
3. **Target Modules:** Which layers of the neural network get LoRA matrices injected.
   - Originally, people only targeted the Attention matrices (`q_proj`, `v_proj`).
   - **Modern best practice:** Target ALL linear layers (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`). This yields much better performance for a negligible increase in memory.

## Other PEFT Methods

While LoRA is dominant, others exist:
- **Prefix Tuning / Prompt Tuning:** Prepends trainable "virtual tokens" to the input prompt. The model weights are entirely frozen. Fast, but less capable than LoRA for complex tasks.
- **Adapter Fusion:** Injects small feed-forward networks between the transformer layers. Largely superseded by LoRA because standard adapters add latency during inference, whereas LoRA matrices can be merged.

## Production Implications

- **Merging Weights:** In production, having LoRA adapters active adds inference latency because the input must pass through both the base weights and the adapter weights. Before deployment, you **merge** the LoRA weights back into the base weights ($W_{new} = W_{base} + A \times B$). The resulting model has the exact same architecture and speed as the original.
- **Multi-LoRA (Adapter Switching):** A massive production advantage of LoRA is that you can host *one* giant base model in memory, and dynamically swap in different tiny LoRA adapters per-request. For example, User A uses the "Legal Document LoRA" and User B uses the "Marketing Copy LoRA" simultaneously on the same GPU. (Supported by vLLM).

## Common Mistakes
- **Setting Rank ($r$) too high:** Assuming higher rank = better model. Setting $r=256$ often leads to overfitting and wastes compute without improving quality.
- **Forgetting to target MLP layers:** Only targeting `q_proj` and `v_proj` leaves a lot of performance on the table.
- **Incorrect Alpha scaling:** Not adhering to the $\alpha = 2r$ heuristic, leading to unstable training or the LoRA having no measurable effect.

## Interview Questions
- **Q: Why does full fine-tuning require significantly more memory than just storing the model weights?**
  - **A:** Because during backpropagation, you must store the activations, the gradients, and the optimizer states (e.g., Adam maintains momentum and variance for every single parameter, usually in 32-bit precision).
- **Q: Can you explain how LoRA reduces the number of trainable parameters?**
  - **A:** LoRA freezes the original weight matrix and represents the weight update as the product of two low-rank matrices. Instead of updating a massive $N \times M$ matrix, it trains an $N \times r$ and an $r \times M$ matrix, where $r$ is very small.
- **Q: Does using LoRA make inference slower in production?**
  - **A:** No, because the LoRA matrices can be algebraically merged back into the base model weights ($W_{merged} = W_{base} + AB$) prior to deployment, resulting in zero latency overhead.

## Further Reading
- [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685) — The foundational paper.
- [QLoRA: Efficient Finetuning of Quantized LLMs](https://arxiv.org/abs/2305.14314) — How to fine-tune 65B parameter models on a single GPU.
