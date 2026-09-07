# Module 02: Retrieval-Augmented Generation (RAG)

## TL;DR
Retrieval-Augmented Generation (RAG) is the dominant architecture for grounding Large Language Models in external knowledge. It solves the critical problems of hallucination, knowledge cutoffs, and context window limits by fetching relevant data at inference time and injecting it into the prompt. This module covers the end-to-end RAG architecture, from data ingestion to advanced retrieval techniques.

---

## The Two-Phase Mental Model

RAG is best understood as two distinct but highly coupled pipelines:
1. **The Indexing Pipeline (Data Ingestion)**: An asynchronous process that loads, cleans, chunks, embeds, and stores documents in a vector database. This phase defines the upper bound of your retrieval quality.
2. **The Query Pipeline (Retrieval & Generation)**: A synchronous process that occurs at inference time. It takes a user query, transforms it, searches the vector database, retrieves the top results, and synthesizes an answer.

If the indexing pipeline produces poor representations, the query pipeline cannot magically retrieve relevant context. 

## When to Use RAG

RAG is not the only way to adapt models. You must evaluate it against alternatives:
- **Fine-Tuning:** Best for changing the *behavior*, *tone*, or *format* of a model. Terrible for injecting new facts (models forget and hallucinate).
- **Long Context Windows:** Great for single-document analysis (e.g., "summarize this 100-page PDF"). Terrible for searching across 10,000 documents due to cost, latency, and the "lost in the middle" problem.
- **RAG:** Best for querying large, dynamic knowledge bases where citations and factuality are critical.

## Module Structure

- **[02-data-ingestion](./02-data-ingestion/)**: Loading, cleaning, chunking, and enriching documents.
- **[03-embedding-models](./03-embedding-models/)**: Translating text into vector representations.
- **[04-vector-databases](./04-vector-databases/)**: Storing and efficiently searching high-dimensional vectors.
- **[05-retrieval](./05-retrieval/)**: Transforming queries, searching, reranking, and assembling context.
- **[06-generation-and-guardrails](./06-generation-and-guardrails/)**: Prompting for grounded answers and validating outputs.
- **[07-advanced-rag](./07-advanced-rag/)**: Agentic RAG, GraphRAG, Multimodal RAG, and semantic caching.

## Production Implications
Failing to understand the full RAG pipeline results in systems that work perfectly in demos but fail spectacularly in production. Common failure modes include retrieving irrelevant chunks due to poor chunking strategies, failing to handle exact keyword searches because of pure semantic retrieval, and serving outdated information due to a lack of cache invalidation.

## Further Reading
- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (Lewis et al., 2020)](https://arxiv.org/abs/2005.11401) — The original RAG paper.
