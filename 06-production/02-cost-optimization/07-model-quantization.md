# Model Quantization

## TL;DR
Quantization is the process of reducing the mathematical precision of a neural network's weights and activations (e.g., moving from 16-bit floats to 4-bit integers). This drastically reduces the VRAM required to load the model and increases generation speed (by alleviating the memory bandwidth bottleneck), making it possible to deploy massive open-weights models on consumer or cost-effective enterprise hardware, usually with negligible degradation in output quality.

---

## The VRAM Bottleneck

When self-hosting an LLM, the primary constraint is not compute; it is Video RAM (VRAM) capacity and Memory Bandwidth.

A standard LLM weight is stored as a 16-bit floating point number (FP16 or BF16). 
- 1 parameter = 2 bytes (16 bits).
- A 70-Billion parameter model (like Llama-3-70B) requires ~140 GB of VRAM just to load the weights.
- Add the memory needed for the KV Cache and batching, and you need at least two 80GB A100 GPUs (costing tens of thousands of dollars) just to run inference on one instance.

**Quantization solves this.** By mapping the 16-bit numbers to lower precision formats (8-bit or 4-bit integers), you compress the model. A 4-bit quantized 70B model requires only ~35 GB of VRAM, allowing it to run comfortably on a single, much cheaper GPU.

## How Quantization Works

In its simplest form, quantization finds the minimum and maximum values of a tensor (a block of weights) and divides that range into a set number of "buckets."
- **FP16** gives you 65,536 possible values.
- **INT8** gives you 256 possible values.
- **INT4** gives you only 16 possible values.

When you quantize to INT4, you round the original high-precision weight to the nearest of the 16 available buckets. This inherently introduces **Quantization Error** (loss of precision).

However, LLMs are incredibly robust to this noise. Because they have billions of parameters, the slight rounding error on individual weights rarely changes the final semantic trajectory of the output.

## Common Quantization Techniques

### 1. Post-Training Quantization (PTQ)
Quantizing a model *after* it has been fully trained. This is what most AI engineers do when downloading models from HuggingFace.
- **GPTQ & AWQ (Activation-Aware Weight Quantization):** The current industry standards for 4-bit quantization. They don't just round numbers blindly; they analyze which specific weights are most "important" (activations) and keep those at higher precision while aggressively compressing the rest. This preserves quality much better than naive quantization.
- **GGUF / llama.cpp:** A format specifically designed for running quantized models on CPU and Apple Silicon (MacBooks). 

### 2. Quantization-Aware Training (QAT)
Training (or fine-tuning) the model with quantization in mind from the start. The model learns to compensate for the rounding errors during the backpropagation process. This yields the highest quality but is computationally expensive.

### 3. QLoRA (bitsandbytes)
A technique used for **Fine-Tuning**. You quantize the base model to 4-bit to fit it on a single GPU, but you add small, high-precision (FP16) adapter weights (LoRA) on top. You freeze the 4-bit weights and only train the adapters. This democratized fine-tuning, allowing developers to fine-tune massive models on cheap hardware.

## Production Implications: Speed vs. Quality

Quantization reduces memory footprint, which in turn **increases generation speed**. Generation is memory-bandwidth bound (the GPU spends time moving weights from VRAM to compute cores). Moving 4-bit weights is 4x faster than moving 16-bit weights.

**The Tradeoff:** While general chat and summarization suffer almost no quality loss at 4-bit (INT4), highly sensitive tasks do.
- **Safe to Quantize (INT4):** Creative writing, summarization, general Q&A, basic code generation.
- **Risky to Quantize (Stick to FP16 or INT8):** Complex mathematics, highly specific factual retrieval, advanced logical reasoning. Extreme quantization can cause models to fail spectacularly on math problems they could solve at FP16.

## Common Mistakes

- **Assuming 4-bit is always fast:** Some hardware (especially older CPUs) does not natively support INT4 math. The engine has to de-quantize the weights back to FP16 in real-time to do the math, which actually *slows down* inference despite saving memory. Modern GPUs and Apple Silicon handle this well.
- **Quantizing small models:** A 70B model handles 4-bit quantization beautifully. A tiny 3B model will degrade severely at 4-bit because every parameter is doing heavy lifting. Smaller models should generally be kept at 8-bit or FP16.
- **Ignoring the prompt length:** Quantization compresses the *weights*. It does not compress the KV Cache. If you pass a 100,000 token context window, the KV cache might consume more VRAM than the weights themselves, causing an OOM regardless of quantization.

## Interview Questions

**Q: Why does quantization not completely destroy the intelligence of a Large Language Model?**
**A:** LLMs are massively over-parameterized. The knowledge and logic are distributed across billions of weights. The slight numerical rounding error introduced by moving from FP16 to INT4 acts as a minor form of noise, which the neural network's dense connections are highly robust against, especially when using techniques like AWQ that protect the most critical weights.

**Q: You want to run inference on a 70B parameter model, but you only have a single GPU with 40GB of VRAM. How is this possible?**
**A:** By using 4-bit Post-Training Quantization (like AWQ or GPTQ). At 16-bit, the model requires ~140GB of VRAM. Quantizing it to 4-bit reduces the weight footprint to roughly 35GB, allowing it to fit (with a small context window) on the 40GB GPU.

## Further Reading
- [AWQ: Activation-aware Weight Quantization](https://arxiv.org/abs/2306.00978) — The research paper explaining how protecting salient weights preserves quality.
- → See [04-deployment/02-self-hosted-inference.md](../04-deployment/02-self-hosted-inference.md) for deploying these models with vLLM.
