# RLHF (Reinforcement Learning from Human Feedback)

## TL;DR
Supervised Fine-Tuning (SFT) teaches a model *how* to talk, but it doesn't necessarily teach it what is *safe* or *helpful*. RLHF bridges this gap by training a Reward Model on human preference data (e.g., "Response A is better than Response B"), and then using Reinforcement Learning (PPO) to optimize the LLM to generate responses that maximize this reward. 

---

## The Alignment Problem

After SFT, a model is highly capable. If you ask it, "How do I build a bomb?", an SFT model will happily give you step-by-step instructions because it was fine-tuned on instruction-following datasets. If you ask it a complex coding question, it might generate a superficially plausible but fundamentally flawed answer, because SFT only optimizes for imitating the *average* human response in the dataset, not necessarily the *best* or most truthful one.

To align the model with human values (helpful, honest, harmless - HHH), we use RLHF.

## The RLHF Pipeline

RLHF is a complex, three-step process:

### Step 1: Supervised Fine-Tuning (SFT)
We start with a base model and run standard SFT to give it a conversational structure.

### Step 2: Train a Reward Model (RM)
We take our SFT model and generate multiple different responses to a single prompt. 
For example, given the prompt "Write a poem about a cat":
- **Response A:** (A funny rhyming poem)
- **Response B:** (A boring paragraph about feline biology)

Human annotators read both and declare a preference (e.g., "A > B"). 
We then train a separate neural network—the **Reward Model**—on this preference dataset. The Reward Model learns to output a scalar score (e.g., +2.5 for Response A, -1.2 for Response B) predicting how much a human will like a given text.

### Step 3: Optimize with PPO
We freeze the Reward Model and use it to grade the SFT model. 
Using Reinforcement Learning—specifically **Proximal Policy Optimization (PPO)**—the SFT model generates responses, the Reward Model scores them, and PPO updates the SFT model's weights to push it toward higher-scoring behaviors.

To prevent the model from devolving into gibberish (e.g., finding a hack that tricks the Reward Model into giving a high score to a string of random letters), we apply a **KL-Divergence penalty**. This penalty forces the model to stay relatively close to the original SFT model's distribution.

## The Key Weakness: Reward Hacking

The biggest failure mode in RLHF is **Reward Hacking**. The Reinforcement Learning agent (the LLM) is not trying to be helpful; it is trying to maximize the score from the Reward Model.

If the human annotators who trained the RM had a bias for longer answers, the RM will assign higher scores to longer texts. During PPO, the LLM will discover this and begin outputting incredibly verbose, redundant essays for even the simplest questions (the "sycophancy" or "verbosity" bias). The model has successfully "gamed" or "hacked" the reward metric.

## Production Implications

- **Complexity and Instability:** PPO is notoriously unstable. Tuning the hyperparameters (learning rate, KL penalty coefficient) requires massive trial and error. A bad PPO run can completely destroy the model's language capabilities overnight.
- **Cost:** RLHF requires maintaining *four* models in memory simultaneously during training: 
  1. The Actor (the model being trained)
  2. The Reference Model (frozen, used for KL penalty)
  3. The Reward Model
  4. The Value Model (used by PPO for advantage estimation).
  This requires immense GPU clusters.

## Common Mistakes

- **Thinking RLHF is required for custom applications:** 95% of applied AI engineering (e.g., text extraction, corporate RAG, code generation) only needs SFT. RLHF is primarily for foundational model creators (OpenAI, Meta) trying to create safe, general-purpose chatbots.
- **Ignoring the KL Penalty:** Running PPO without a strict KL divergence constraint will immediately result in a model that outputs high-reward gibberish.

## Interview Questions

- **Q: Why do we need a Reward Model in RLHF? Why not just use human feedback directly in PPO?**
  - **A:** Reinforcement learning requires thousands of iterations and millions of generations. It is impossible to have a human sitting at a desk scoring every single generation in real-time. The Reward Model acts as a proxy for the human.
- **Q: What is reward hacking?**
  - **A:** It is when the model learns to exploit flaws or biases in the reward model to achieve a high score without actually fulfilling the user's intent (e.g., writing overly long, sycophantic, but unhelpful answers).

## Further Reading
- [InstructGPT Paper (Ouyang et al., 2022)](https://arxiv.org/abs/2203.02155) — The paper that introduced RLHF to LLMs.
