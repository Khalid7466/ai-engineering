# Supervised Fine-Tuning (SFT)

## TL;DR
Supervised Fine-Tuning (SFT) is the process of taking a base model (which only knows how to predict the next word) and training it on highly curated pairs of Instructions and Responses. This transforms the model into a helpful assistant that follows instructions, adheres to formats, and adopts specific behaviors. In modern pipelines, SFT is the critical first step before alignment techniques like RLHF.

---

## The Mechanics of SFT

A "Base Model" (like `Llama-3-8B-Base`) is trained on a massive corpus of internet text. If you prompt a base model with "What is the capital of France?", it might reply with "What is the capital of Germany?" because it is merely continuing a pattern it saw on a quiz website. 

To make it useful, we must fine-tune it to act as an assistant. This is done via **Supervised Fine-Tuning**.

### 1. Instruction-Response Pairs
SFT requires a dataset of pairs: `(Prompt, Desired Output)`. The model is trained using standard next-token prediction (Cross-Entropy Loss), but crucially, **loss is only calculated on the Response tokens**, not the Prompt tokens. We don't want the model to learn how to generate user prompts; we only want it to learn how to generate the correct answers.

### 2. Chat Templates (Formatting)
Because LLMs only see a flat sequence of tokens, we must use special tokens to differentiate between the System prompt, the User prompt, and the Assistant's response. This is called a Chat Template.

**Example: ChatML Format (used by OpenAI and many OSS models)**
```text
<|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
Write a python function to add two numbers.<|im_end|>
<|im_start|>assistant
def add(a, b):
    return a + b<|im_end|>
```
If you fine-tune a model using ChatML, you **must** use ChatML at inference time in production. Mismatching the chat template between training and inference is a massive cause of degraded performance.

Other common formats include:
- **Alpaca:** `### Instruction: ... ### Response: ...`
- **ShareGPT:** A JSON format handling multi-turn conversations.
- **Llama 3 Format:** `<|start_header_id|>user<|end_header_id|>`

## The Quality vs. Quantity Rule

The most important rule of SFT is: **Data Quality > Data Quantity.**

Historically, engineers believed they needed hundreds of thousands of examples to fine-tune a model. The paper *LIMA (Less Is More for Alignment)* proved this wrong. Training a model on 1,000 perfectly crafted, diverse, human-written examples often outperforms a model trained on 50,000 mediocre, scraped examples.

A high-quality SFT dataset must have:
1. **Diversity:** Not just 1,000 examples of the exact same task, but variations in length, tone, and complexity.
2. **Accuracy:** Zero factual errors or formatting mistakes.
3. **Complexity:** If you only train on short responses, the model will lose the ability to write long, detailed responses (the "mode collapse" problem).

## Overfitting and Catastrophic Forgetting

LLMs are prone to **overfitting** during SFT. Because the model has billions of parameters, it can easily memorize your small dataset of 1,000 examples rather than learning the underlying pattern.

When an LLM overfits, it often suffers from **Catastrophic Forgetting**. It adapts so heavily to your specific dataset that it forgets its general pre-trained knowledge. For example, if you fine-tune a model purely on Python code, it might completely lose its ability to speak French or summarize history.

### Detecting Overfitting
You monitor overfitting using a Validation Dataset (data held out from training).
1. **Training Loss goes down, Validation Loss goes down:** The model is learning and generalizing. (Good)
2. **Training Loss goes down, Validation Loss goes UP:** The model is memorizing the training data and failing on new data. (Overfitting). 

**Mitigations:**
- Stop training early (Early Stopping). SFT usually only requires 1 to 3 epochs.
- Use a lower learning rate.
- Mix in a small percentage of general instruction data (e.g., standard conversational data) with your domain-specific data to preserve general capabilities.

## Production Implications

- **Template Mismatch:** The #1 reason an open-source model performs terribly in production is that the inference engine (like vLLM or Ollama) is applying a different chat template than what the model was trained on. Always verify the `tokenizer_config.json`.
- **Loss Masking:** If your training script calculates loss on the User Prompt tokens (instead of masking them out and only calculating loss on the Assistant tokens), your model will learn to mimic the user's typos and writing style, leading to bizarre generation behavior.

## Common Mistakes
- **Training for too many epochs:** Running SFT for 10 epochs. Most SFT requires only 1-3 epochs; beyond that, you severely risk catastrophic forgetting.
- **Garbage In, Garbage Out:** Scraping thousands of raw customer support logs and training on them directly without cleaning out the "Umm", "Hold on a second", and agent mistakes.
- **Ignoring multi-turn data:** If you only train on single Prompt/Response pairs, the model will not know how to handle follow-up questions in a multi-turn chat UI.

## Interview Questions
- **Q: In Supervised Fine-Tuning of an LLM, do we calculate the loss function over the entire sequence (Prompt + Response)?**
  - **A:** No. We mask out the Prompt tokens. We only calculate cross-entropy loss on the Response tokens, because we want to optimize the model's ability to generate the answer, not the question.
- **Q: What is a chat template and why does it matter?**
  - **A:** A chat template is the specific arrangement of special tokens (like `<|user|>` and `<|assistant|>`) used to structure a conversation. It matters because if the template used during inference doesn't exactly match the one used during SFT, the model will be confused and output degraded text.

## Further Reading
- [LIMA: Less Is More for Alignment](https://arxiv.org/abs/2305.11206) — Essential reading on why 1,000 high-quality examples beat 50,000 mediocre ones.
- [HuggingFace: Chat Templates](https://huggingface.co/docs/transformers/main/chat_templating) — How templates work in code.
