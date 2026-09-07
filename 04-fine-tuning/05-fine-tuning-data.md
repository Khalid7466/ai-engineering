# Fine-Tuning Data

## TL;DR
In fine-tuning, data quality is paramount. A small dataset of 1,000 perfectly curated examples will drastically outperform 100,000 noisy, scraped examples. Modern fine-tuning relies on synthetic data generation, rigorous deduplication, and establishing a "data flywheel" from production logs rather than brute-force scraping.

---

## Data Quality > Data Quantity

Historically, machine learning focused on massive datasets. The *LIMA (Less Is More for Alignment)* paper shifted this paradigm for LLMs. It proved that because the pre-trained base model already contains vast knowledge, fine-tuning is merely about teaching it the *format and style* of interaction. 

### The Alpaca vs. LIMA Story
- **Alpaca-52k:** Early open-source models were fine-tuned on 52,000 instructions generated cheaply by OpenAI's API. The data was noisy, contained formatting errors, and had repetitive structures.
- **LIMA:** Researchers hand-wrote just 1,000 pristine, diverse, highly complex examples. A model trained on these 1,000 examples outperformed the model trained on 52,000 noisy examples. 

**Rule of Thumb:** Every single example in your SFT dataset should be something you would be proud to show the user. If an example has a typo, the model learns to make typos.

## Synthetic Data Generation

Because human curation is slow and expensive, modern teams use Frontier Models (GPT-4, Claude 3.5) to generate synthetic training data.

1. **Seed Prompts:** You write 50 high-quality seed examples for your specific domain.
2. **Expansion:** You prompt GPT-4: "Here are 50 examples of my domain task. Generate 500 more unique scenarios that are similar in structure but cover different edge cases."
3. **Filtering:** You use a script to ensure the synthetic outputs adhere perfectly to your required JSON schemas or formatting rules, discarding any that fail.

## Deduplication

If your dataset contains duplicate or near-duplicate examples, the model will over-index on those specific patterns, leading to memorization and overfitting. 
- **Exact Deduplication:** Removing exact string matches. Easy but insufficient.
- **MinHash / LSH (Locality-Sensitive Hashing):** An algorithmic approach to find *near-duplicates* (e.g., two documents that are 90% identical except for a few words). This is crucial when scraping data from the web or corporate wikis.

## The Data Flywheel

The most successful AI engineering teams do not rely on static datasets; they build a **Data Flywheel**.

1. **V1 Deployment:** Deploy a heavily prompted model or a basic LoRA fine-tune.
2. **Production Logging:** Log all user inputs and model outputs.
3. **Implicit Feedback:** Track metrics like "Did the user accept the AI suggestion?" or "Did the user immediately regenerate the response?"
4. **Curation:** Take the prompts where the model failed, have a human expert write the *perfect* response, and add it to the SFT dataset.
5. **V2 Deployment:** Re-train the model. 

## Security and Privacy: Data Poisoning and PII

- **Data Poisoning:** If you train on public or crowdsourced data, malicious actors can inject hidden triggers. For example, they might upload training examples where the model outputs malicious code whenever the phrase "Security check" is mentioned.
- **PII Scrubbing:** If you fine-tune on corporate logs or customer emails, the LLM will memorize specific names, SSNs, and API keys, and may regurgitate them to unauthorized users. **Always run a PII scrubbing pipeline (e.g., Microsoft Presidio) before adding text to a fine-tuning dataset.**

## Production Implications

- **Formatting Mismatches:** If your SFT dataset contains spacing inconsistencies (e.g., sometimes `###Response`, sometimes `### Response`), the model's loss will plateau because it is trying to learn random noise.
- **Class Imbalance:** If you are fine-tuning a model to classify emails, and 90% of your dataset is "Spam" and 10% is "Not Spam," the model will just learn to always output "Spam."

## Common Mistakes

- **More is better:** Scraping 100,000 Reddit threads and training on them directly without filtering for toxicity or quality.
- **Lack of Diversity:** Having 1,000 examples that are all 2 sentences long. In production, when a user asks for a long essay, the model will suffer "mode collapse" and only write 2 sentences.
- **Training on the Test Set:** Accidentally including your evaluation benchmarks in your training data, leading to a false sense of high performance.

## Interview Questions

- **Q: Why is deduplication crucial in LLM pre-training and fine-tuning?**
  - **A:** Duplicate data causes the model to over-index on those specific tokens, leading to rote memorization (overfitting) rather than learning generalizable patterns. It also wastes compute.
- **Q: What is the LIMA principle in the context of SFT?**
  - **A:** "Less Is More for Alignment." It posits that a very small amount of incredibly high-quality, diverse data (e.g., 1,000 examples) is superior to massive amounts of noisy, uncurated data.

## Further Reading
- [LIMA: Less Is More for Alignment](https://arxiv.org/abs/2305.11206) — The paper that proved data quality > quantity.
- [Text Deduplication using MinHash](https://ekzhu.com/datasketch/minhash.html) — Technical explanation of near-duplicate removal.
