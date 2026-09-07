# AI Engineering Interview Cheat Sheet

> A condensed, high-yield Q&A reference for last-minute interview prep. Focuses on the real traps candidates fall into, what interviewers are actually probing for, and the production realities behind every technical answer.

---

## Quick Navigation
- [1. LLM Fundamentals](#1-llm-fundamentals)
- [2. Retrieval-Augmented Generation (RAG)](#2-retrieval-augmented-generation-rag)
- [3. Agentic AI](#3-agentic-ai)
- [4. Fine-Tuning](#4-fine-tuning)
- [5. AI Systems Design](#5-ai-systems-design)

---

## 1. LLM Fundamentals

**Q:** Why do state-of-the-art LLMs struggle with basic string operations like counting the letter 'r' in "strawberry" or reversing words?  
**A:** LLMs do not receive raw text or characters; they process integer token IDs emitted by subword tokenizers like Byte-Pair Encoding (BPE). In BPE, the word "strawberry" is tokenized as discrete chunks like `["straw", "berry"]`, hiding individual character positions unless the model is prompted to emit a character-by-character scratchpad.

**Trap:** "The model lacks common sense, reasoning capacity, or sufficient training on English spelling."  
**Correct:** This is an architectural representation limitation of subword tokenization, not a reasoning defect. If an atomic unit of input bundles multiple characters into a single vector ID, character-level spatial indexing is mathematically inaccessible to early attention layers.

---

**Q:** Why does autoregressive token generation slow down as context grows, and how does the KV Cache mitigate this?  
**A:** Self-attention computes quadratic dot products ($O(N^2)$) across all previous tokens; without caching, generating token $N+1$ requires recomputing Key and Value projections for all prior $N$ tokens. The KV Cache persists previously computed Key and Value tensors in GPU VRAM, reducing each generative step to an $O(N)$ vector-matrix multiplication.

**Trap:** "KV Cache is like an HTTP or Redis cache that stores completed model responses to save API costs."  
**Correct:** KV Cache stores intermediate hidden-state activation tensors across layers inside GPU memory for an active sequence. It trades VRAM capacity for compute, transforming autoregressive generation from quadratic to linear time per token while becoming the primary constraint on concurrent batch size.

---

**Q:** If you set `temperature = 0.0`, does that guarantee deterministic, hallucination-free outputs? Why or why not?  
**A:** No. Temperature 0 merely forces greedy argmax selection at each step; if the model's highest-probability continuation is factually inaccurate, it will output that hallucination with 100% confidence. Furthermore, distributed inference engines running across parallel GPU threads introduce non-associative floating-point summation differences, causing occasional non-deterministic token drift even at temperature 0.

**Trap:** "Temperature controls model truthfulness and accuracy, so temperature 0 forces factual correctness."  
**Correct:** Temperature controls the flatness of the next-token probability distribution, not factual grounding. Hallucinations stem from training objectives (cross-entropy loss over web text) and parametric gaps, completely independent of sampling randomness.

---

**Q:** What is the "Lost-in-the-Middle" phenomenon, and why does it occur despite models supporting 1M+ token context windows?  
**A:** LLMs exhibit empirical U-shaped retrieval curves where information placed in the middle 60% of a long prompt context is retrieved with significantly lower accuracy than facts placed near the beginning or end. This stems from positional encoding biases and pre-training data distributions where crucial context (e.g., titles, summaries, conclusions) predominantly occurs at document boundaries.

**Trap:** "The context window was exceeded, so the middle tokens were truncated or dropped from attention."  
**Correct:** All tokens reside within the active context window and are mathematically computed during attention. However, the model's learned attention weights systematically discount non-boundary tokens during multi-layer attention routing.

---

**Q:** What is the practical operational difference between Top-p (Nucleus Sampling) and Top-k sampling in production?  
**A:** Top-k truncates candidates to a static count $k$ regardless of the probability curve, risking gibberish when the model is uncertain or cutting off valid vocabulary when diverse options exist. Top-p dynamically adjusts the candidate pool to the smallest set of tokens whose cumulative probability mass exceeds threshold $p$, naturally expanding when multiple tokens are viable and narrowing to a single token when confident.

**Trap:** "Top-k and Top-p do the same thing and should always be tuned together with high values."  
**Correct:** Top-p is context-adaptive: if a token has 98% probability, the candidate pool is 1 token; if probability is distributed across 20 plausible synonyms, all 20 are considered. Combining high Top-k and Top-p introduces redundant hyperparameters that complicate testing.

---

## 2. Retrieval-Augmented Generation (RAG)

**Q:** Why build a RAG architecture when frontier models offer 1M+ token context windows capable of ingesting entire document sets?  
**A:** Ingesting 1M tokens per query incurs unacceptable latency (15–30s prefill time), unsustainable API costs ($3–$15 per query), and severe "lost-in-the-middle" retrieval degradation over hundreds of documents. RAG delivers sub-second latency, bounded token costs, role-based access control (RBAC), and source-verifiable citations by retrieving only top relevant chunks.

**Trap:** "Large context windows make RAG obsolete because models can just read everything in-context."  
**Correct:** Context windows provide capacity for synthesis over retrieved material, not an efficient replacement for search indices. Querying 10,000 corporate records by stuffing them into prompt context on every user turn is economically, operationally, and latency prohibitive.

---

**Q:** What is the core engineering tradeoff between small chunk sizes (e.g., 128 tokens) and large chunk sizes (e.g., 1024 tokens), and how does Parent-Child chunking resolve it?  
**A:** Small chunks produce precise, noise-free vector embeddings for retrieval but lack sufficient semantic surrounding context for the LLM to generate complete answers. Large chunks preserve narrative context but dilute embedding vector sharpness and clutter prompts with irrelevant text. Parent-Child chunking indexes small child chunks for vector retrieval but passes the encompassing parent chunk to the LLM for synthesis.

**Trap:** "Use a standard 512-token chunk with 50-token overlap because that is the default setting in LangChain."  
**Correct:** Fixed chunking creates an inescapable zero-sum tension between retrieval search precision and LLM generation context. Decoupling the retrieval unit (child) from the generation unit (parent) fundamentally eliminates this tradeoff.

---

**Q:** Why does pure semantic vector search fail on queries like "Error code ERR_502_TIMEOUT in module auth.py", and how does Hybrid Search solve it?  
**A:** Dense embedding models compress text into continuous semantic space, smoothing out rare tokens, alphanumeric error codes, and exact variable names into generic conceptual neighborhoods. Hybrid Search executes dense vector search alongside sparse BM25 keyword search concurrently, using Reciprocal Rank Fusion (RRF) to score exact lexical matches and semantic concepts together.

**Trap:** "Upgrade to a larger or fine-tuned embedding model (like `text-embedding-3-large`) to capture specific error codes."  
**Correct:** Continuous vector embeddings are fundamentally ill-suited for exact alphanumeric string matching because tiny token differences represent massive functional discrepancies. BM25 scores exact inverse document frequency directly, guaranteeing exact-match hits that dense models overlook.

---

**Q:** Why don't we use Cross-Encoders for the initial retrieval pass across the entire vector database?  
**A:** Bi-encoders encode queries and documents independently into static vectors ahead of time, enabling logarithmic $O(\log N)$ approximate nearest-neighbor search. Cross-encoders require concatenating the query with every document candidate and running full multi-layer bidirectional attention across all combined tokens, making an exhaustive search across millions of documents computationally impossible at runtime.

**Trap:** "Bi-encoders are more accurate than cross-encoders for ranking documents."  
**Correct:** Cross-encoders are dramatically more accurate because query and document tokens attend to each other across every transformer layer; they are simply too computationally expensive to run on more than top-50 candidate chunks during a second-stage rerank.

---

**Q:** Your production RAG evaluation reports a spike in hallucinated answers. How do you systematically isolate whether the retrieval pipeline or generation prompt failed?  
**A:** Measure Context Recall and Faithfulness independently using a framework like RAGAS. If Context Recall is low, the retriever failed to surface the necessary grounding chunks (a retrieval failure); if Context Recall is high but Faithfulness is low, the required facts were present in the prompt but the LLM hallucinated anyway (a prompt or model compliance failure).

**Trap:** "Immediately switch to a larger LLM (e.g., upgrade to GPT-4o or Claude 3.5 Sonnet) to stop the hallucinations."  
**Correct:** If the retrieval pipeline fetched irrelevant chunks, even frontier models cannot synthesize correct answers without external knowledge. You must decouple and measure retrieval precision/recall separately from generation faithfulness.

---

## 3. Agentic AI

**Q:** When should an engineering team build an autonomous agent instead of a deterministic prompt chain or workflow pipeline?  
**A:** Use agents only when the problem requires dynamic runtime decision-making, where the next step or tool cannot be predicted ahead of time and depends on intermediate environment observations. If the sequence of steps can be modeled as a deterministic Directed Acyclic Graph (DAG) or standard if/else logic, use Prompt Chaining to guarantee lower latency, lower cost, and high reliability.

**Trap:** "Agents are more intelligent, flexible, and modern, so all production workflows should be agentic."  
**Correct:** Unnecessary autonomy causes unpredictable multi-loop execution, high latency, runaway API costs, and silent failure loops. Production systems should stay as far left (deterministic) on the agency spectrum as possible, introducing autonomy only where hardcoded logic demonstrably fails.

---

**Q:** Why does the ReAct (Reason + Act) loop significantly outperform zero-shot direct tool calling on complex, multi-step tasks?  
**A:** Direct tool calling forces the model to predict tool names and arguments in a single forward pass without intermediate computation tokens. ReAct introduces a natural language scratchpad ("Thought") before each action, allowing the model to decompose complex goals, maintain internal state, critique previous tool observations, and avoid premature or hallucinated tool invocations.

**Trap:** "ReAct is just prompt flavoring that makes logs easier for humans to read."  
**Correct:** Transformers generate tokens autoregressively; emitting reasoning tokens directly alters the hidden states and attention context that predict subsequent tokens, measurably boosting tool selection accuracy and argument validity.

---

**Q:** What is the architectural difference between Working Memory, Episodic Memory, and Semantic Memory in production agents?  
**A:** Working memory is ephemeral in-context state (the current scratchpad, tool payloads, and active turn variables) stored in the prompt context window. Episodic memory captures historical user interactions, past execution traces, and outcomes stored in persistent document/vector stores. Semantic memory stores structured domain facts and external knowledge bases queried via retrieval tools.

**Trap:** "Agent memory is simply passing the entire historical chat array back to the LLM API on every turn."  
**Correct:** Appending raw conversation history causes rapid context window overflow, introduces noise, triggers recency bias, and exponentially inflates token costs. Production agents require distinct memory management lifecycles with summarization and eviction policies.

---

**Q:** What are the two most critical engineering safeguards when exposing data mutation tools (APIs) to an LLM agent?  
**A:** Enforce strict runtime schema validation (e.g., Pydantic) on all JSON arguments with error feedback fed back into the loop, and require idempotency keys, dry-run flags, and human-in-the-loop approval thresholds for state-modifying actions (e.g., sending emails, executing payments, deleting database rows).

**Trap:** "Provide the agent with a generic code interpreter or write tool, and add system prompt instructions asking it to be careful."  
**Correct:** System prompts provide zero deterministic security guarantees against prompt injection or hallucinations. Unconstrained mutation tools without runtime schema enforcement and human approval gates will lead to catastrophic data corruption or unauthorized actions in production.

---

**Q:** Why does giving a single agent 30 different tools degrade its task completion rate, and how does the Orchestrator-Worker pattern resolve this?  
**A:** Supplying dozens of tool schemas bloats prompt context, dilutes the model's attention, and increases tool-selection ambiguity between semantically adjacent tools. The Orchestrator-Worker pattern employs a high-level orchestrator to decompose requests and delegate them to narrow worker agents, each configured with only 2–4 domain-specific tools.

**Trap:** "Models with 128k+ context windows have plenty of room for 50+ tool schemas, so one agent is simpler and better."  
**Correct:** Context capacity does not equal attention focus; empirical benchmarks demonstrate that tool-selection accuracy drops significantly as the number of available candidate schemas increases. Narrow tool scopes preserve precision.

---

## 4. Fine-Tuning

**Q:** A stakeholder requests fine-tuning Llama 3 on 5,000 internal PDF policy documents so employees can query company rules. Why is this an anti-pattern?  
**A:** Fine-tuning adjusts model behavior, tone, style, and syntax, but is an unreliable and lossy mechanism for injecting factual knowledge. Parametric memory lacks source citations, suffers from hallucinations, and cannot be updated dynamically without recurring expensive training runs; dynamic internal knowledge retrieval is the canonical use case for RAG.

**Trap:** "Fine-tuning is superior to RAG because the knowledge is permanently baked into the model's neural network weights."  
**Correct:** Neural weights are probabilistic associative memories, not databases. Querying facts learned solely through fine-tuning produces confident hallucinations, offers zero RBAC access control, and cannot provide auditable document line citations.

---

**Q:** How does LoRA (Low-Rank Adaptation) achieve training quality comparable to full fine-tuning while using a fraction of the GPU memory?  
**A:** LoRA freezes the original weight matrix $W_0 \in \mathbb{R}^{d \times k}$ and models weight updates as two low-rank matrices $B \in \mathbb{R}^{d \times r}$ and $A \in \mathbb{R}^{r \times k}$ (where $r \ll \min(d, k)$), such that $W = W_0 + B \times A$. This eliminates optimizer states and gradients for 99% of parameters, slashing VRAM footprint while allowing the adapter weights to be merged into base weights at inference with zero added latency.

**Trap:** "LoRA compresses the model weights so inference runs faster and uses less VRAM in production."  
**Correct:** LoRA is a parameter-efficient training technique. Once training finishes, the adapter $\Delta W$ is mathematically added to $W_0$, resulting in an identical parameter count and inference latency to the original base model.

---

**Q:** When does Supervised Fine-Tuning (SFT) fail to correct undesired model behaviors, and what alignment technique is required instead?  
**A:** SFT trains models exclusively on positive demonstration pairs using next-token cross-entropy loss, teaching the model what to say in ideal scenarios without teaching it what *not* to say or how to navigate adversarial inputs. Correcting stubborn refusal failures, sycophancy, or safety violations requires preference optimization (DPO or RLHF) using paired chosen vs. rejected examples.

**Trap:** "When SFT fails, collect 5,000 more positive examples of the correct behavior and train for more epochs."  
**Correct:** Models trained only on positive examples suffer from exposure bias. Without negative preference penalties (unlearning the rejected path), the model cannot establish strict decision boundaries between compliant and non-compliant generations.

---

**Q:** What is QLoRA, and what is the engineering catch when choosing it over standard LoRA?  
**A:** QLoRA quantizes base model weights to 4-bit NormalFloat (NF4), using Double Quantization and paged optimizers to backpropagate gradients into 16-bit LoRA adapters. This enables fine-tuning 70B models on a single 24GB consumer GPU; the catch is that on-the-fly dequantization of 4-bit weights to 16-bit during forward and backward passes increases training wall-clock time by 20–40%.

**Trap:** "QLoRA produces 4-bit adapters that reduce inference latency in production serving."  
**Correct:** QLoRA is strictly a memory-saving training strategy; adapters are trained in 16-bit precision and can be merged into unquantized base models or quantized separately for deployment using engines like AWQ or GPTQ.

---

**Q:** What is Catastrophic Forgetting during fine-tuning, and how do you prevent it when training a model for a specific enterprise domain?  
**A:** Catastrophic Forgetting occurs when gradient updates on a narrow domain dataset overwrite the model's pre-trained general linguistic, coding, or reasoning capabilities. It is mitigated by using parameter-efficient methods like LoRA (which keep base weights frozen) and mixing a 10–20% replay buffer of general domain instructions into the fine-tuning dataset.

**Trap:** "Increase the learning rate and train for more epochs so the model memorizes the domain data thoroughly."  
**Correct:** High learning rates and excessive epochs aggressively accelerate catastrophic forgetting by driving parameter weights far outside their pre-trained manifold. Domain specialization requires low learning rates, early stopping, and data regularization.

---

## 5. AI Systems Design

**Q:** How do you determine whether an incoming enterprise use case belongs in Prompt Chaining, Standard RAG, Agentic RAG, or an Autonomous Agent?  
**A:** Evaluate two orthogonal dimensions: is the execution path fixed or dynamic, and is retrieval needed?  
1. Fixed path + No retrieval $\rightarrow$ Prompt Chaining  
2. Fixed path + Single search pass $\rightarrow$ Standard RAG  
3. Dynamic path + Multi-step / iterative search $\rightarrow$ Agentic RAG  
4. Dynamic path + Open-ended tool execution and planning $\rightarrow$ Autonomous Agent  
Always choose the simplest pattern that satisfies the SLA.

**Trap:** "Default to an Autonomous Agent framework because it can dynamically handle all lower-level patterns automatically."  
**Correct:** Autonomous agents introduce variable latency, non-deterministic failure states, and high API costs. Over-engineering a fixed problem with an autonomous agent degrades reliability and user trust.

---

**Q:** What are the three primary optimization targets in production AI systems, and why is it impossible to maximize all three simultaneously?  
**A:** The three targets are Quality (Accuracy/Evals), Latency (TTFT/TBT), and Cost ($/token). Improving quality via multi-turn Agentic RAG, large frontier models, and deep reasoning traces directly inflates latency and token spend; conversely, slashing latency and cost using small quantized models, prompt caching, and single-pass pipelines limits reasoning depth. Production architecture requires explicit SLA trade-offs.

**Trap:** "A properly optimized system using modern frameworks can achieve maximum accuracy, sub-second latency, and near-zero cost."  
**Correct:** The fundamental trade-off space is rigid. Every additional token generated or retrieved increases latency and compute cost; optimizing a system means balancing tradeoffs against the specific business SLA.

---

**Q:** A user submits a multi-hop query: "Compare the Q3 revenue growth rate of the top 3 EV manufacturers mentioned in our 2024 Market Outlook." Why does standard RAG fail, and what architecture solves it?  
**A:** Standard RAG fails because a single retrieval query cannot resolve the dependency: the system cannot retrieve the Q3 filings for the top 3 manufacturers until it has first retrieved the Market Outlook document and extracted their names. The solution is an Agentic RAG or Prompt Chaining pipeline: Step 1 retrieves the Market Outlook to identify the 3 companies; Step 2 spawns parallel retrieval queries for each company's Q3 filing; Step 3 synthesizes the comparative analysis.

**Trap:** "Set vector search top-$k = 50$ so the retriever pulls in all possible documents in one shot."  
**Correct:** Stuffing 50 chunks into prompt context causes severe token bloat, triggers the "lost-in-the-middle" problem, increases cost, and rarely pulls the exact multi-hop evidence needed. Multi-hop queries require structured, sequential decomposition.

---

**Q:** What system bottlenecks do PagedAttention and Speculative Decoding solve in production inference infrastructure?  
**A:** PagedAttention (pioneered by vLLM) solves GPU memory fragmentation by storing KV cache tensors in partitioned, non-contiguous virtual memory blocks, maximizing concurrent batching throughput. Speculative Decoding solves GPU memory bandwidth bottlenecks during autoregressive generation by using a small draft model to generate candidate tokens verified in parallel by the target model, reducing Time Between Tokens (TBT) by 2–3x.

**Trap:** "Speculative decoding reduces model weight size so large models can fit onto smaller GPUs."  
**Correct:** Speculative decoding requires loading *both* the target model and draft model into VRAM; its benefit is accelerating decoding wall-clock speed without altering output precision or reducing parameter size.

---

**Q:** How do you engineer an enterprise LLM system to gracefully handle API rate limits (429s), latency spikes, and provider outages?  
**A:** Implement an ingress API gateway incorporating:  
1. Distributed token-bucket rate limiters with jittered exponential backoff  
2. Semantic caching for repeated queries  
3. Automated circuit breakers that fall back across providers (e.g., Anthropic Claude 3.5 $\rightarrow$ OpenAI GPT-4o $\rightarrow$ local self-hosted vLLM)  
4. Tiered feature degradation (e.g., falling back from multi-step Agentic RAG to single-pass RAG or cached answers).

**Trap:** "Wrap the API call in a basic Python `try/except` block with a `time.sleep(1)` retry loop."  
**Correct:** Naive sleep loops under high concurrency produce thundering herd catastrophes that deepen rate limit locks. Production resilience requires distributed rate management, multi-provider failover, and graceful functional degradation.
