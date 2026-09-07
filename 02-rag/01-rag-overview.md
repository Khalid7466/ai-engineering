# RAG Overview

## TL;DR
Retrieval-Augmented Generation (RAG) is a framework that improves the quality of LLM responses by fetching relevant information from an external knowledge base and providing it to the model as context. It addresses the fundamental limitations of LLMs: hallucinations, outdated knowledge (training cutoffs), and the inability to access private or proprietary data.

---

## The Core Problem

Large Language Models are static artifacts. Once training is complete, they cannot learn new facts without retraining or fine-tuning. When asked a question outside their training data, or about recent events, they confidently hallucinate. 

While fine-tuning can alter a model's style, it is highly ineffective for injecting new knowledge. The model will often forget or conflate fine-tuned facts. Long context windows (e.g., 1 million tokens) offer an alternative, allowing you to pass entire document troves into the prompt. However, stuffing a massive context window is slow, extremely expensive, and suffers from the "lost in the middle" phenomenon where the model ignores information located in the center of the prompt.

## The RAG Solution

RAG solves these issues by treating the LLM not as a database of knowledge, but as a reasoning engine. 

1. **Retrieval:** When a user asks a question, the system searches an external database (usually a vector database) for relevant documents.
2. **Augmentation:** The retrieved documents are appended to the user's prompt as context.
3. **Generation:** The LLM reads the context and the user's query, and generates an answer strictly based on the provided information.

## The Two Pipelines

RAG consists of two decoupled pipelines:

### 1. The Indexing Pipeline (Asynchronous)
This pipeline prepares your data for search.
- **Loaders:** Extract text from PDFs, HTML, Word docs, etc.
- **Chunking:** Split long documents into smaller, semantically coherent pieces.
- **Embedding:** Convert each chunk into a high-dimensional vector.
- **Indexing:** Store the vectors and original text in a vector database.

### 2. The Query Pipeline (Synchronous)
This pipeline runs in real-time when a user makes a request.
- **Query Transformation:** Rewrite the user's query for better search performance.
- **Retrieval:** Search the vector database for chunks similar to the query.
- **Reranking:** Order the retrieved chunks by actual relevance.
- **Generation:** Pass the top chunks to the LLM to generate the final response.

## Production Implications
The most common mistake in RAG is treating it as a solved problem by calling an API. RAG in production is highly sensitive to the quality of data ingestion. Garbage in, garbage out. If your chunking strategy breaks a sentence in half, or your PDF loader fails to parse a table correctly, the LLM will receive garbled context and generate a poor answer, regardless of how advanced the model is.

## Common Mistakes
- **Ignoring Data Quality:** Throwing raw PDFs into a vector DB without cleaning boilerplate text.
- **Relying Solely on Vector Search:** Vector search struggles with exact keyword matches (IDs, names).
- **Over-chunking:** Making chunks so small they lose all context, or so large they dilute the relevance score.
- **Neglecting Reranking:** Fetching 5 documents and passing them directly to the LLM without a secondary scoring step.

## Interview Questions
- **Q: Why use RAG instead of fine-tuning for a company's internal wiki?**
  - *Answer:* Fine-tuning is for teaching a model new behaviors or formats, not facts. Models are prone to hallucinating fine-tuned knowledge. RAG allows deterministic retrieval, factual grounding, citations, and easy updating (just update the vector DB without retraining).
- **Q: What is the difference between the Indexing and Query pipelines?**
  - *Answer:* Indexing is offline/async preparation of data (chunking, embedding). Querying is the real-time process of taking user input, fetching data, and generating a response.

## Further Reading
- [Building RAG Applications for Production](https://docs.smith.langchain.com/) — LangChain's guide to production RAG.
