# Fine-Tuning Infrastructure

## TL;DR
Fine-tuning LLMs is a memory-bound problem, not a compute-bound problem. Storing the model weights, gradients, and optimizer states requires massive GPU VRAM. Understanding how to calculate these memory requirements and how to use distributed training frameworks (DeepSpeed, FSDP) and Mixed Precision is critical for bringing models to production.

---

## The GPU Memory Math

When training a neural network, you must store four things in GPU memory. Let's calculate this for a **7 Billion parameter** model. 
*(Rule: 1 parameter in 16-bit precision = 2 bytes; in 32-bit = 4 bytes).*

1. **Model Weights (FP16):** 7B * 2 bytes = **14 GB**
2. **Gradients (FP16):** 7B * 2 bytes = **14 GB**
3. **Optimizer States (Adam, FP32):** Adam stores both momentum and variance for every parameter in 32-bit. 7B * 8 bytes = **56 GB**
4. **Activations:** Temporary memory used during the forward/backward pass. (Highly dependent on batch size and context length, but typically ~10-20 GB).

**Total Memory required for Full Fine-Tuning of a 7B model = ~100 GB.**
You cannot run this on a single A100 (80GB). 

*Note: This is why PEFT/LoRA is so popular (see [03-peft-and-lora.md](03-peft-and-lora.md)). LoRA drops the optimizer and gradient memory to near-zero, making a 7B model fit on a 16GB GPU.*

## Mixed Precision Training (BF16 vs FP16)

To save memory, models are not trained in standard 32-bit floats (FP32). We use 16-bit precision.
- **FP16 (Float16):** Older standard. Prone to underflow/overflow issues during training, requiring complex gradient scaling.
- **BF16 (BFloat16):** Developed by Google (Brain Float). It trades precision for a larger dynamic range. It almost entirely eliminates gradient overflow issues. **Always use BF16 if your GPU supports it (Ampere architecture or newer, e.g., A100, H100, RTX 30/40 series).**

## Gradient Checkpointing

Activations (the intermediate outputs of each layer during the forward pass) take up massive memory because they must be saved for the backward pass (backpropagation). 

**Gradient Checkpointing** trades compute for memory. Instead of saving all activations, it only saves a few "checkpoints." During the backward pass, it quickly *recalculates* the missing activations on the fly. 
- **Result:** Drastically reduces activation memory by ~70%, at the cost of training taking ~20% longer. **Always enable this for LLM training.**

## Distributed Training: DeepSpeed and FSDP

When your model requires 100GB of memory but your GPUs only have 80GB, you must split the model across multiple GPUs. 

### DeepSpeed (ZeRO)
Microsoft's DeepSpeed uses the Zero Redundancy Optimizer (ZeRO) to partition memory across GPUs.
- **ZeRO Stage 1:** Partitions only the Optimizer States across GPUs.
- **ZeRO Stage 2:** Partitions Optimizer States AND Gradients. (Most common for fine-tuning 7B-13B models).
- **ZeRO Stage 3:** Partitions Optimizer, Gradients, AND the Model Weights themselves. (Required for 70B+ models). 

### FSDP (Fully Sharded Data Parallel)
PyTorch's native alternative to DeepSpeed. It operates similarly to ZeRO-3, sharding all components across GPUs. FSDP is increasingly preferred by engineering teams because it is built natively into PyTorch and avoids DeepSpeed's complex C++ compilation issues.

## Practical GPU Requirements (Using LoRA/QLoRA)

If you are using QLoRA (4-bit base model + 16-bit adapters):
- **7B / 8B Models (Llama-3-8B):** Fits on 1x 16GB GPU (e.g., T4, RTX 4080).
- **13B / 14B Models (Qwen-14B):** Fits on 1x 24GB GPU (e.g., A10G, RTX 3090/4090).
- **70B Models (Llama-3-70B):** Fits on 2x 40GB GPUs or 1x 80GB A100.

## Production Implications

- **OOM (Out of Memory) Errors:** The most common failure in AI engineering. If you OOM during training, the first steps are: (1) Reduce Batch Size, (2) Enable Gradient Checkpointing, (3) Reduce Context Length, (4) Use LoRA instead of Full Fine-Tuning.
- **Multi-Node Networking:** When scaling beyond 8 GPUs, you must link multiple physical machines (nodes). The bottleneck becomes the network speed between nodes. You must use InfiniBand or high-end RoCE networks; standard AWS ethernet will result in the GPUs sitting idle at 10% utilization waiting for data to transfer.

## Common Mistakes

- **Using FP16 without Gradient Scaling:** Results in `NaN` (Not a Number) loss values because the gradients underflow to zero. Use BF16 instead.
- **Leaving Gradient Checkpointing off:** Wasting massive amounts of VRAM on activations.
- **Using ZeRO-3 unnecessarily:** ZeRO-3 introduces massive communication overhead. If your model fits on a single GPU using ZeRO-2, using ZeRO-3 will dramatically slow down your training.

## Interview Questions

- **Q: Why does the Adam optimizer require so much memory during training?**
  - **A:** Adam tracks two additional values (momentum and variance) for every single trainable parameter. Since these are usually kept in FP32 for stability, it adds 8 bytes of memory per parameter.
- **Q: Explain the concept of Gradient Checkpointing.**
  - **A:** It is a technique to save memory by discarding intermediate activations during the forward pass and recalculating them on-the-fly during the backward pass. It trades a small increase in computation time for a massive decrease in VRAM usage.

## Further Reading
- [DeepSpeed ZeRO Paper](https://arxiv.org/abs/1910.02054) — How memory partitioning works.
- [PyTorch FSDP Tutorial](https://pytorch.org/tutorials/intermediate/FSDP_tutorial.html) — Native distributed training in PyTorch.
