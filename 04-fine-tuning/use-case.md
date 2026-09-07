<Use Case: E-commerce Product Description Generator>
## Objective
An e-commerce company sells 50,000 SKUs across various categories (apparel, electronics, home goods). They need to generate compelling, brand-aligned product descriptions automatically from raw specs (dimensions, materials, features). The output must strictly adhere to their distinct brand voice: enthusiastic but concise, using specific formatting (a short hook paragraph, followed by exactly three bullet points, and a closing sentence).

## Why Fine-Tuning?
The engineering team initially tried simpler approaches, all of which failed in production:

1. **Zero-Shot & Few-Shot Prompting (GPT-4):**
   - They provided a detailed system prompt describing the brand voice and included 3-5 examples of good descriptions.
   - **Failure:** While technically functional, the output was generically "AI-sounding." It overused words like "unleash," "elevate," and "seamless." It occasionally broke the strict formatting rules (giving 4 bullets instead of 3). It was also extremely expensive to pass 5 examples in the prompt for every single one of the 50,000 SKUs.

2. **RAG (Retrieval-Augmented Generation):**
   - They embedded their existing human-written catalog and retrieved the top 3 most similar products to use as in-context examples for the generation.
   - **Failure:** RAG is designed to retrieve *knowledge*, not to enforce *style*. The model often hallucinated features from the retrieved examples into the new product description (e.g., a cotton shirt suddenly inherited "waterproof zippers" because the retrieved example was a jacket).

Only **Supervised Fine-Tuning (SFT)** solved this. Fine-tuning fundamentally shifted the model's internal probability distribution toward the specific syntax, vocabulary, and structure of the brand.

## Technical Decisions

### Decision 1: Full Fine-Tuning vs. PEFT (LoRA)
- **Chose:** PEFT (LoRA) on Llama-3-8B.
- **Rejected:** Full Fine-Tuning of a 7B+ model.
- **Rationale:** Full fine-tuning requires updating all 8 billion parameters, necessitating multiple A100 GPUs due to optimizer state and gradient memory overhead. LoRA (Low-Rank Adaptation) freezes the base model and only trains a small set of injected matrices (around 1-2% of total parameters). LoRA achieved 95% of the performance of full fine-tuning at 10% of the compute cost, running on a single A10G GPU.

### Decision 2: Data Quantity vs. Quality
- **Chose:** 2,000 highly curated, human-written examples.
- **Rejected:** Scraping 50,000 existing descriptions from their legacy CMS.
- **Rationale:** The "LIMA principle" (Less Is More for Alignment). Many of their legacy 50k descriptions were poorly written, inconsistent, or didn't follow the new formatting rules. Training on garbage produces garbage. They hired three copywriters to perfectly format 2,000 examples spanning all product categories.

### Decision 3: LoRA Target Modules
- **Chose:** Targeting all linear layers (Q, K, V, O, up_proj, down_proj, gate_proj).
- **Rejected:** Targeting only Attention (Q, V) layers.
- **Rationale:** While early LoRA papers suggested only targeting Query and Value matrices, modern practice shows that targeting all linear layers (including MLP layers) significantly improves style adaptation and formatting adherence without a huge increase in compute.

## Architecture Walkthrough

### 1. Data Preparation
The data was formatted into JSONL using the ChatML format, mapping the raw specs (User) to the perfect description (Assistant).

```json
{"messages": [
  {"role": "system", "content": "You are a brand copywriter for [Company]. Write concise, enthusiastic descriptions: 1 paragraph, 3 bullets, 1 closing sentence."},
  {"role": "user", "content": "Product: Classic Cotton Tee. Specs: 100% organic cotton, crew neck, pre-shrunk, relaxed fit. Color: Navy."},
  {"role": "assistant", "content": "Meet your new everyday essential. The Classic Cotton Tee combines effortless style with unparalleled comfort, perfect for lazy Sundays or casual Fridays.\n- Crafted from 100% organic cotton for a breathable feel.\n- Classic crew neck design with a versatile relaxed fit.\n- Pre-shrunk fabric ensures it stays true to size, wash after wash.\nUpgrade your wardrobe basics today."}
]}
```

### 2. LoRA Configuration
They configured the LoRA adapter using the `peft` library.
```python
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=16, # Rank of the update matrices
    lora_alpha=32, # Scaling factor
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(base_model, lora_config)
```

### 3. Training and Merging
The model was trained for 3 epochs using a cosine learning rate scheduler. After training, the LoRA weights were merged back into the base model weights to avoid latency overhead during inference.

## Lessons Learned
- **Catastrophic Forgetting is Real:** In their early runs, they trained for 10 epochs. The model learned the formatting perfectly but forgot how to form coherent English sentences (e.g., "The cotton is very the good the wear."). They had to reduce epochs and lower the learning rate.
- **Evaluation is Hard:** You cannot use standard accuracy metrics for text generation. They built a pipeline using a larger model (Claude 3.5 Sonnet) as an "LLM-as-a-Judge" to score the fine-tuned model's outputs on brand voice, formatting adherence, and factual accuracy against the raw specs.
- **The Data Flywheel:** They built a UI where human reviewers could accept, edit, or reject the AI-generated descriptions. Edited descriptions were fed back into the training dataset for the next LoRA iteration, constantly improving the model over time.
</Use Case: E-commerce Product Description Generator>
