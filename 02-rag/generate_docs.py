import os

base_dir = r"G:\CS\ai-engineering\02-rag"

files = {
    "README.md": """
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
""",
    "use-case.md": """
<Use Case: Legal Entity Search>
## Objective
A large law firm needs to search millions of case files to find specific mentions of entities, such as the exact name "Ahmed Mahmoud Ali Hassan". The system must accurately retrieve documents containing this specific entity amidst millions of pages of legal jargon.

## Why Standard RAG Fails
Standard RAG relies on pure semantic search (vector embeddings). Dense embeddings are notoriously bad at exact keyword or name matching. To an embedding model, "Ahmed Mahmoud Ali Hassan", "Ahmed Mahmoud", and "Mahmoud Hassan" might map to nearly identical points in the vector space because they share semantic characteristics (they are all Arabic names). If a user queries for "Ahmed Mahmoud Ali Hassan", the vector database might return documents about "Ahmed Mahmoud" simply because they are closer in the vector space, leading to missed evidence and hallucinations.

## Technical Decisions
### Decision 1: Agentic RAG vs Standard Pipeline
- **Chose:** Agentic RAG
- **Rejected:** Standard Query Pipeline
- **Rationale:** We need an LLM agent to analyze the query, detect that it contains an exact entity name, and decide to use an exact match filter rather than a pure semantic search.

### Decision 2: Entity Tokenization Array vs Exact String Storage
- **Chose:** Tokenized Entity Arrays with NER Metadata
- **Rejected:** Exact String Matching on the full text
- **Rationale:** Storing exact strings and relying on string matching is slow across millions of files. Instead, during ingestion, we run Named Entity Recognition (NER) to extract entities, tokenize them (e.g., `["Ahmed", "Mahmoud", "Ali", "Hassan"]`), and store them as metadata arrays. At query time, the system can use array intersection operations in the vector DB (like PostgreSQL's array operators or Qdrant's payload filters) to find exact subsets, which is exponentially faster and handles slight variations better than full-text string matching.

## Architecture Walkthrough
1. **Ingestion (NER Extraction):** As PDFs are processed, an NER model extracts names. The name "Ahmed Mahmoud Ali Hassan" is tokenized to `["Ahmed", "Mahmoud", "Ali", "Hassan"]` and stored in the vector database payload under the key `entities`.
2. **Query Processing:** The user asks: "Show me cases involving Ahmed Mahmoud Ali Hassan."
3. **Agentic Router:** The LLM agent intercepts the query, uses tool-calling to extract the entity `["Ahmed", "Mahmoud", "Ali", "Hassan"]`, and determines this is an entity-specific search.
4. **Hybrid Retrieval:** The system issues a vector search query for the semantic context, but adds a hard metadata filter: `payload.entities contains_all ["Ahmed", "Mahmoud", "Ali", "Hassan"]`.
5. **Context Assembly:** Only documents containing the exact entity are retrieved. The LLM then answers the question based purely on those documents.

## Lessons Learned
In v1, we used pure semantic search, resulting in lawyers getting cases for completely unrelated people with similar names. We learned that **metadata is often more important than the embedding itself**. We accepted the storage redundancy of storing large entity arrays because the retrieval accuracy improvement was a strict business requirement.
""",
    "01-rag-overview.md": """
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
""",
    r"02-data-ingestion\01-document-loaders.md": """
# Document Loaders

## TL;DR
Document loaders are the foundation of the indexing pipeline. They extract raw text from structured and unstructured sources (PDFs, HTML, Confluence, SQL). The choice of loader dictates whether structural semantics (like tables, charts, and headers) are preserved or destroyed, directly impacting downstream retrieval quality.

---

## The Parsing Challenge

Extracting text from a `.txt` file is trivial. Extracting text from a two-column PDF with embedded images and tables is a complex computer vision and parsing problem. If a loader simply reads left-to-right, top-to-bottom across a two-column PDF, it will interleave text from both columns, creating nonsensical sentences that destroy the semantic value of the document.

### PDF Parsing Strategies
- **Text-based (e.g., PyPDF2):** Fast, cheap, but layout-blind. It extracts text exactly as encoded in the PDF stream. Fails completely on multi-column layouts and complex tables.
- **Layout-aware (e.g., Unstructured.io, PDFMiner):** Uses heuristics or ML models to identify document layout (headers, footers, columns, lists, tables). Significantly slower but essential for complex documents.
- **Vision-based (e.g., LayoutLM):** Treats the document as an image and uses vision models to understand the structure. Highly accurate but computationally expensive.

### Handling Tables and Charts
Standard text extraction often flattens tables into unreadable strings of text separated by spaces. When this text is embedded, the vector represents noise.
- **Solution for Tables:** Use layout-aware parsers to extract tables as Markdown or HTML. This preserves the row/column relationships, allowing the LLM to comprehend the tabular data during generation.
- **Solution for Charts:** Requires a multimodal approach, using a Vision-Language Model (VLM) to generate a text summary of the chart during ingestion, which is then embedded and indexed.

## Production Implications
In production, documents are messy. You will encounter scanned PDFs (requiring OCR), corrupted files, and wildly varying layouts. If your loader fails silently or produces garbage text, your entire RAG pipeline is compromised. 

For instance, if a financial report's balance sheet is parsed as a single run-on paragraph, the LLM will hallucinate the revenue numbers because the context it receives is incomprehensible.

## Common Mistakes
- **Assuming all PDFs are text-based:** Failing to implement OCR for scanned documents.
- **Ignoring Document Structure:** Using naive loaders that destroy tables and multi-column layouts.
- **Failing to Capture Metadata:** Throwing away source URLs, page numbers, and authors during the loading phase.

## Interview Questions
- **Q: Why should you avoid simple text extractors for complex PDFs in a RAG system?**
  - *Answer:* Simple extractors are layout-blind. They fail on multi-column text, headers, and tables, producing mangled text that ruins the semantic embedding and prevents the LLM from understanding the context.

## Further Reading
- [Unstructured.io Documentation](https://unstructured-io.github.io/unstructured/) — The industry standard for layout-aware parsing.
""",
    r"02-data-ingestion\02-text-cleaning.md": """
# Text Cleaning

## TL;DR
Text cleaning removes noise, boilerplate, and semantic pollution from extracted text before it is embedded. Clean data ensures that vector representations accurately reflect the core meaning of the document, leading to higher precision during retrieval.

---

## Semantic Pollution

"Semantic pollution" occurs when irrelevant text dominates a chunk, skewing its vector embedding away from its true meaning. 

### Boilerplate Removal
Web pages and PDFs are full of boilerplate: navigation menus, copyright notices, headers, footers, and repetitive legal disclaimers. If every chunk from a website includes the string "© 2024 Acme Corp. All Rights Reserved. Home | About | Contact," the embeddings for all those chunks will cluster together in the vector space, driven by the boilerplate rather than the unique content of the page.

- **Solution:** Use DOM parsing (e.g., BeautifulSoup) to target specific HTML tags (`<article>`, `<main>`) and strip out `<nav>`, `<footer>`, and `<aside>`. For PDFs, use layout-aware loaders to identify and strip headers/footers.

### Unicode Normalization and Mojibake
Extracted text often contains bizarre characters, non-breaking spaces, or mojibake (garbled text resulting from character encoding issues).
- **Normalization:** Convert all text to a standard Unicode form (e.g., NFKC) to ensure consistency.
- **Regex Cleaning:** Strip out excessive whitespace, sequential newlines, and unprintable characters.

### PII Masking
In enterprise RAG, you often cannot send raw documents to external embedding APIs (like OpenAI's) due to data privacy regulations.
- **Masking:** Use lightweight NER models (like Presidio) to detect and redact Personally Identifiable Information (PII) — emails, phone numbers, SSNs — replacing them with tokens like `[EMAIL]` or `[SSN]` before the text leaves your infrastructure.

## Production Implications
Failing to clean text leads to a bloated vector database and degraded search accuracy. If boilerplate isn't removed, a query about "contact information" might retrieve 50 identical footer chunks instead of the actual "Contact Us" page. If PII isn't masked, you risk compliance violations and data leaks when using third-party APIs.

## Common Mistakes
- **Embedding HTML tags:** Leaving `<script>`, `<style>`, and raw HTML tags in the text, which confuses the embedding model.
- **Ignoring Whitespace:** Embedding chunks with hundreds of sequential newline characters, wasting token limits.
- **Skipping PII checks:** Accidentally sending customer data to public LLM APIs.

## Interview Questions
- **Q: What is semantic pollution and how does it affect RAG?**
  - *Answer:* Semantic pollution is the inclusion of repetitive, irrelevant text (like headers or footers) in a document chunk. It skews the embedding vector, causing chunks to be retrieved based on the boilerplate rather than the actual content.

## Further Reading
- [Microsoft Presidio](https://microsoft.github.io/presidio/) — Data protection and PII anonymization SDK.
""",
    r"02-data-ingestion\03-chunking-strategies.md": """
# Chunking Strategies

## TL;DR
Chunking is the process of splitting long documents into smaller segments for embedding and retrieval. The goal is to maximize semantic density—ensuring each chunk contains a complete, self-contained thought. The choice of strategy heavily impacts both retrieval accuracy and generation context.

---

## Why Chunking Matters

Embedding models have finite context windows (e.g., 512 or 8192 tokens). You cannot embed a 100-page book as a single vector. Even if you could, a single vector representing an entire book would be so semantically diluted that it would be useless for answering specific queries. 

### Strategy 1: Fixed-Size Chunking
- **Mechanism:** Split text every N characters or tokens.
- **Pros:** Simple, fast to implement.
- **Cons:** "Dumb." It routinely cuts sentences or paragraphs in half, destroying context. 

### Strategy 2: Recursive Character Splitting (The Standard)
- **Mechanism:** Tries to split on logical boundaries (paragraphs `\n\n`, then sentences `\n`, then words) until the chunks are below the maximum size. It uses a sliding window (overlap) to ensure context isn't lost at the edges.
- **Pros:** Preserves sentence boundaries, good default choice.
- **Cons:** Still fundamentally structural, not semantic.

### Strategy 3: Semantic Chunking
- **Mechanism:** Uses a small embedding model or statistical method to calculate the similarity between sequential sentences. It creates a chunk boundary only when there is a significant shift in topic (a drop in similarity score).
- **Pros:** Highly coherent chunks.
- **Cons:** Computationally expensive during ingestion.

### Strategy 4: Parent-Child Chunking (Auto-merging)
- **Mechanism:** Document is split into large parent chunks, which are further split into small child chunks. Only the child chunks are embedded and indexed. When a child chunk is matched during retrieval, the system returns the larger parent chunk to the LLM.
- **Pros:** Optimizes for both high-precision retrieval (small chunks) and rich context for generation (large chunks).

## Production Implications
Choosing the wrong chunking strategy leads to the "context fragmentation" problem. If a chunk contains the answer, but the subject of the sentence was in the previous chunk, the LLM cannot answer the question. Overlap helps, but Parent-Child chunking is often required in production to ensure the LLM has enough surrounding context to formulate a robust answer.

## Common Mistakes
- **No Overlap:** Using fixed-size chunks without overlap, guaranteeing broken sentences.
- **Chunks Too Small:** Creating 50-token chunks. They retrieve well but lack enough context for the LLM to generate a coherent answer.
- **Chunks Too Large:** Creating 2000-token chunks. The embedding becomes diluted, making retrieval imprecise.

## Interview Questions
- **Q: Explain the Parent-Child chunking strategy and why it is useful.**
  - *Answer:* It embeds small child chunks for precise vector search, but retrieves the larger parent chunk for the LLM prompt. This solves the tradeoff between needing small chunks for high retrieval accuracy and large chunks for sufficient generation context.

## Further Reading
- [LlamaIndex: Node Parsers & Chunking](https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/) — Excellent overview of advanced chunking implementations.
""",
    r"02-data-ingestion\04-metadata-enrichment.md": """
# Metadata Enrichment

## TL;DR
Metadata enrichment involves attaching structured data (dates, authors, entities, categories) to unstructured text chunks before indexing. This enables hybrid search capabilities, allowing systems to perform exact filtering before applying semantic similarity search, drastically improving precision and speed.

---

## The Limitations of Pure Vector Search

Vector search is probabilistic. It excels at finding conceptually similar text, but fails miserably at exact constraints. 
If a user asks: "What did the CEO say about Q3 revenue in the 2023 annual report?"
A pure vector search might return a highly relevant quote about Q3 revenue from the *2022* report, because the semantic similarity of the quote outweighs the chronological difference in the vector space.

## Enabling Deterministic Filtering

Metadata allows you to apply deterministic pre-filters to your vector search.
- **Temporal Filtering:** Filter by `date >= 2023-01-01`.
- **Source Filtering:** Filter by `document_type == "annual_report"`.
- **Entity Filtering:** Filter by `author == "CEO"`.

### Strategies for Enrichment
1. **Source Metadata:** Extract structural data during parsing (file name, URL, page number, section header).
2. **LLM/NER Extraction:** Run the text chunk through a lightweight LLM or Named Entity Recognition (NER) model during ingestion to extract key entities (companies, people, product names) and append them to the chunk's metadata payload.
3. **Summary Injection:** Use an LLM to generate a 1-sentence summary of the chunk, and store that as metadata.

## Production Implications
Without metadata, you cannot build a reliable RAG system for enterprise use cases. Users expect traditional search features (filtering by date, author, or category) combined with semantic search. Storing robust metadata enables you to partition your vector database, applying hard filters before the KNN (K-Nearest Neighbors) search, which reduces the search space, lowers latency, and guarantees exact constraint matching.

## Common Mistakes
- **Losing Source Context:** Failing to store the original document URL or page number, making it impossible to generate citations in the final output.
- **Over-extracting:** Running expensive LLM calls to extract metadata on every single chunk, blowing up ingestion costs.
- **Not Indexing Metadata:** Storing metadata in the vector DB but failing to configure indices on those fields, resulting in slow query performance.

## Interview Questions
- **Q: How does metadata solve the problem of temporal queries in RAG?**
  - *Answer:* Vector search cannot reliably distinguish between a 2022 report and a 2023 report. By enriching chunks with a `timestamp` metadata field, the system can apply a hard filter (e.g., `year == 2023`) before executing the semantic search, guaranteeing only recent documents are retrieved.

## Further Reading
- [Pinecone: Metadata Filtering](https://docs.pinecone.io/docs/metadata-filtering) — How vector databases implement metadata filters.
""",
    r"03-embedding-models\01-embedding-fundamentals.md": """
# Embedding Fundamentals

## TL;DR
Embedding models translate human language into high-dimensional numerical vectors, mapping semantic meaning to geometric space. The quality of the external embedding model dictates the ceiling of your RAG system's retrieval performance. 

---

## Internal vs External Embeddings

**CRITICAL DISTINCTION:** Do not confuse the internal embeddings inside an LLM (like GPT-4) with the external embedding models used for RAG (like `text-embedding-3-large`).
- **Internal Embeddings:** The hidden states inside an LLM used for next-token prediction.
- **External Embedding Models:** Purpose-built models (often BERT-based encoders) trained explicitly to map sentences/paragraphs into a shared vector space for similarity comparison. 

## Capturing Semantic Meaning

An embedding is an array of floating-point numbers (e.g., a 1536-dimensional vector). Models are trained using contrastive learning (e.g., pulling similar text pairs closer together and pushing dissimilar pairs apart).
In this vector space, concepts that are semantically related are geometrically close. 
- "The dog barked" and "The hound howled" will have vectors that are very close to each other, even though they share no words.

## Measuring Similarity

To find the most relevant chunks, we measure the distance between the query vector and the document vectors.
1. **Cosine Similarity:** Measures the angle between two vectors. It focuses on the direction (semantic meaning) rather than the magnitude (length of the text). The standard metric for most text embeddings.
2. **Dot Product:** Measures both angle and magnitude. Faster to compute, and mathematically equivalent to Cosine Similarity *if* the vectors are normalized to a length of 1.

## Production Implications
The embedding model is the ultimate bottleneck. If the model fails to map the query and the relevant document to the same region in vector space, the vector database will never retrieve it, and the LLM will never see it. You cannot prompt your way out of a bad embedding model.

## Common Mistakes
- **Mixing Models:** Using `text-embedding-ada-002` for indexing and `Cohere-embed-v3` for querying. Vectors from different models exist in entirely different geometric spaces and are incompatible.
- **Ignoring Normalization:** Using Dot Product on unnormalized vectors, leading to skewed similarity scores based on text length rather than semantic relevance.

## Interview Questions
- **Q: Why use Cosine Similarity instead of Euclidean Distance for text embeddings?**
  - *Answer:* Cosine similarity measures the angle between vectors, capturing semantic orientation regardless of magnitude. Euclidean distance is sensitive to magnitude, meaning a long document and a short document with the same meaning might be far apart in Euclidean space but close in Cosine space.

## Further Reading
- [Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks](https://arxiv.org/abs/1908.10084) — The foundational paper on sentence embeddings.
""",
    r"03-embedding-models\02-embedding-model-selection.md": """
# Embedding Model Selection

## TL;DR
Selecting an embedding model requires balancing performance (accuracy), latency, cost, and language support. The MTEB benchmark is the standard for evaluating models, but domain-specific testing is essential before committing to a model for production.

---

## The MTEB Benchmark

The Massive Text Embedding Benchmark (MTEB) is the industry standard leaderboard for embedding models. It evaluates models across various tasks: retrieval, classification, clustering, and semantic textual similarity (STS). 
When building RAG, you should look specifically at the **Retrieval** tab on MTEB, not just the overall average.

## Model Ecosystem Overview

### API-Based Models
- **OpenAI (`text-embedding-3-large` / `small`):** The default choice. Excellent performance, native Matryoshka support (variable dimensions), and very cheap.
- **Cohere (`embed-v3-english` / `multilingual`):** Top-tier performance. Uniquely trained to measure the relevance of a document to a query, rather than just raw semantic similarity.

### Open-Source / Local Models
- **BGE (BAAI General Embedding, e.g., `bge-m3`):** State-of-the-art open-source models. The `M3` variant supports Multi-linguality, Multi-granularity (different chunk sizes), and Multi-Functionality (dense and sparse embeddings).
- **E5 (e.g., `e5-large-v2`):** Microsoft's open-source powerhouse. Requires specific prefixes (e.g., adding "query: " or "passage: ") to function correctly.

## Selection Criteria

1. **Domain Specificity:** If you are working in medical or legal domains, generic models might fail. You may need domain-adapted models (e.g., MedCPT).
2. **Multilingual Needs:** If your documents are in German but queries are in English, you must use a strong multilingual model (like `Cohere-multilingual` or `bge-m3`).
3. **Data Privacy:** If you cannot send data to cloud APIs, you must deploy an OSS model like BGE locally.

## Production Implications
Switching embedding models in production requires re-embedding your entire knowledge base. If you have 50 million documents, this will cost significant time and money. Choose your model carefully during the prototyping phase.

## Common Mistakes
- **Chasing the MTEB Leaderboard:** Switching models every time a new one tops the MTEB leaderboard, wasting resources on re-indexing for a 0.5% gain in accuracy.
- **Forgetting Prefixes:** Using E5 models without the required "query: " or "passage: " prefixes, destroying retrieval performance.

## Interview Questions
- **Q: Why might you choose a local, open-source embedding model over OpenAI's API?**
  - *Answer:* Data privacy compliance (keeping sensitive data on-premise), avoiding API latency, removing vendor lock-in, and the ability to fine-tune the model on domain-specific vocabulary.

## Further Reading
- [MTEB Leaderboard (HuggingFace)](https://huggingface.co/spaces/mteb/leaderboard) — The current rankings for embedding models.
""",
    r"03-embedding-models\03-embedding-in-production.md": """
# Embedding in Production

## TL;DR
Deploying embedding models in production involves managing throughput for batch ingestion, optimizing vector dimensions for storage costs, and implementing caching layers to reduce latency and API usage.

---

## Batch Ingestion at Scale

When indexing millions of documents, calling an embedding API synchronously one-by-one is unacceptably slow.
- **Batching:** Send requests in batches (e.g., 2048 chunks per API call) to maximize throughput.
- **Concurrency & Rate Limiting:** Implement robust retry logic with exponential backoff. Cloud APIs (like OpenAI) enforce strict tokens-per-minute (TPM) limits. You must orchestrate ingestion workers to stay just below these limits to prevent `429 Too Many Requests` errors.

## Dimensionality Reduction and Matryoshka Embeddings

High-dimensional vectors (e.g., 3072 dimensions) are highly accurate but incredibly expensive to store and slow to search in memory.
- **Matryoshka Representation Learning (MRL):** Modern models (like OpenAI's `text-embedding-3`) are trained such that the most important information is front-loaded in the first N dimensions.
- **Truncation:** You can truncate a 3072-dimensional vector down to 256 dimensions simply by slicing the array. You lose a small fraction of accuracy but reduce storage costs and memory usage by 12x.

## Caching Strategies

Embeddings are deterministic for a given model version. 
- **Ingestion Caching:** Hash the raw text chunk. Before sending it to the API, check if the hash exists in your cache. This prevents re-embedding the entire knowledge base if you tweak your vector DB schema.
- **Query Caching:** Cache the exact user queries. If a user asks the same question twice, bypass the embedding API and vector search entirely.

## Production Implications
Vector databases hold indices in RAM for fast search. Storing 1 billion 1536-dimensional vectors requires terabytes of expensive memory. Leveraging Matryoshka embeddings to reduce dimensions before indexing can save hundreds of thousands of dollars in infrastructure costs without severely impacting retrieval quality.

## Common Mistakes
- **No Rate Limiting:** Crashing ingestion pipelines against API rate limits.
- **Overpaying for Storage:** Using maximum dimension vectors for simple datasets where 256 dimensions would yield identical user-facing results.

## Interview Questions
- **Q: What are Matryoshka embeddings and how do they save costs?**
  - *Answer:* They are embeddings trained to store the most critical semantic information in the earliest dimensions. This allows engineers to truncate the vectors (e.g., from 1536 to 256 dimensions) while retaining most of the accuracy, drastically reducing the memory required by the vector database.

## Further Reading
- [Matryoshka Representation Learning](https://arxiv.org/abs/2205.13147) — The research behind variable-dimension embeddings.
""",
    r"04-vector-databases\01-vector-db-fundamentals.md": """
# Vector DB Fundamentals

## TL;DR
Vector databases are specialized storage systems designed to efficiently search high-dimensional vector spaces. Because exact Nearest Neighbor search is impossible at scale, they rely on Approximate Nearest Neighbor (ANN) algorithms to trade a marginal loss in accuracy for massive gains in speed.

---

## The Scale Problem

If you have 10 million vectors, finding the most similar document requires calculating the distance between the query vector and every single vector in the database (Exact Search / Flat Index). This is an $O(N)$ operation that becomes unacceptably slow in real-time applications.

## Approximate Nearest Neighbor (ANN)

To achieve low-latency search (milliseconds), vector databases use ANN algorithms. They do not guarantee finding the absolute closest vector, but they guarantee finding a "good enough" vector extremely fast.

### HNSW (Hierarchical Navigable Small World)
The dominant ANN algorithm used by nearly all modern vector databases (Pinecone, Qdrant, Weaviate).
- **How it works:** It builds a multi-layered graph. The top layers are sparse, containing long-range connections. The bottom layers are dense.
- **Search Process:** A search starts at the top layer, making massive jumps across the vector space to quickly locate the general neighborhood of the query. It then drops down to lower, denser layers, refining the search until it finds the local nearest neighbors.
- **Pros:** Blazing fast, highly accurate.
- **Cons:** High memory usage (the graph structure must be kept in RAM).

### IVF (Inverted File Index)
- **How it works:** Clusters vectors into groups (Voronoi cells) using K-means. 
- **Search Process:** Compares the query to the cluster centroids, selects the closest clusters, and only searches the vectors within those clusters.

### PQ (Product Quantization)
Not a search algorithm, but a compression technique. PQ compresses high-dimensional vectors into shorter codes, drastically reducing the memory footprint, often used in tandem with IVF or HNSW.

## Production Implications
Understanding your index type is critical for capacity planning. HNSW provides the best search experience but requires massive amounts of RAM. If you run out of memory, the database will crash or thrash against disk, destroying latency. 

## Common Mistakes
- **Using Flat Index in Production:** Deploying exact search on large datasets, resulting in 10+ second query latencies.
- **Misconfiguring HNSW parameters:** Ignoring `m` (number of links) and `ef_construction` (search depth during indexing), leading to either bloated memory usage or poor recall.

## Interview Questions
- **Q: How does HNSW achieve sub-millisecond search times on millions of vectors?**
  - *Answer:* It uses a hierarchical graph structure. It starts at a sparse top layer to make large jumps toward the target region, then descends through increasingly dense layers to find the local nearest neighbors, avoiding a brute-force scan.

## Further Reading
- [Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs](https://arxiv.org/abs/1610.02415) — The HNSW paper.
""",
    r"04-vector-databases\02-vector-db-comparison.md": """
# Vector Database Comparison

## TL;DR
The vector database market is highly fragmented. Choosing the right one depends on your team's expertise, infrastructure requirements, need for complex metadata filtering, and whether you prefer a managed SaaS solution or open-source self-hosting.

---

## Market Overview

### Pinecone
- **Type:** Fully Managed SaaS (Closed Source)
- **Best For:** Teams that want zero infrastructure management and blazing-fast setup.
- **Pros:** Serverless architecture, highly reliable, easy to use.
- **Cons:** Expensive at scale, no local self-hosting option, vendor lock-in.

### Qdrant
- **Type:** Open Source (Rust) / Managed Cloud
- **Best For:** Heavy metadata filtering and hybrid search.
- **Pros:** Written in Rust (highly performant), exceptional payload (metadata) filtering capabilities, allows storing vectors on disk (quantized) to save RAM.
- **Cons:** Slightly steeper learning curve than Pinecone.

### Weaviate
- **Type:** Open Source (Go) / Managed Cloud
- **Best For:** Schema-first, object-oriented data modeling.
- **Pros:** Built-in modules for embedding and cross-encoding, strong GraphQL interface.
- **Cons:** Rigid schema requirements can be cumbersome for simple projects.

### PGVector (PostgreSQL Extension)
- **Type:** Open Source Database Extension
- **Best For:** Teams already heavily invested in PostgreSQL.
- **Pros:** ACID compliance, joint SQL + Vector queries, no new infrastructure to maintain.
- **Cons:** Not as fast or scalable as purpose-built vector databases for pure ANN workloads at massive scale (100M+ vectors).

### Chroma
- **Type:** Local / Open Source
- **Best For:** Prototyping, local development, and local-first applications.
- **Pros:** Runs in-memory or via SQLite, zero setup required.
- **Cons:** Lacks enterprise-grade distributed clustering features (currently).

## Decision Framework

1. **Do you already have massive PostgreSQL infrastructure?** Use `pgvector` first. Only migrate if performance bottlenecks.
2. **Do you have zero DevOps resources?** Use Pinecone or Qdrant Cloud.
3. **Do you need advanced keyword + semantic (Hybrid) search out of the box?** Use Qdrant or Weaviate.

## Production Implications
Vector databases are sticky. Once you upload 50 million embedded chunks, migrating to a new database requires re-indexing everything or writing complex migration scripts. Choose based on your 12-month scaling trajectory, not just what is easiest to `pip install` today.

## Common Mistakes
- **Deploying Local DBs to Prod:** Using Chroma in-memory on a stateless serverless function (like AWS Lambda) and losing all data on cold start.
- **Over-engineering:** Paying for enterprise Pinecone when a simple `pgvector` index on an existing RDS instance would suffice.

## Interview Questions
- **Q: When would you recommend using PGVector over a dedicated vector database like Pinecone?**
  - *Answer:* When the application relies heavily on relational data alongside vector data (e.g., joining user profiles with semantic search results), the dataset is moderately sized, and the engineering team wants to minimize infrastructure complexity by keeping everything in an existing Postgres database.

## Further Reading
- [Vector DB Benchmarks (ANN-Benchmarks)](http://ann-benchmarks.com/) — Standardized performance metrics for ANN algorithms.
""",
    r"04-vector-databases\03-hybrid-search.md": """
# Hybrid Search

## TL;DR
Hybrid search combines the semantic understanding of dense vector embeddings with the exact keyword matching of sparse retrieval (like BM25). It bridges the gap where pure vector search fails: acronyms, unique identifiers, names, and highly specific industry jargon.

---

## The Two Retrieval Paradigms

### Dense Retrieval (Vector Search)
- **Mechanism:** Neural embeddings (e.g., `text-embedding-3`).
- **Strengths:** Understands concepts, synonyms, and context. (e.g., maps "automobile" to "car").
- **Weaknesses:** Terrible at exact string matching. Will struggle to distinguish between "Model X-412" and "Model Y-412" because the semantic meaning is identical.

### Sparse Retrieval (Keyword Search / BM25)
- **Mechanism:** TF-IDF variants like BM25 count the frequency of exact tokens in a document relative to the whole corpus.
- **Strengths:** Perfect for exact matches, names, error codes, and IDs.
- **Weaknesses:** No semantic understanding. Fails if the user queries "car" but the document uses "automobile".

## How Hybrid Search Works

Hybrid search executes both dense and sparse queries simultaneously, then merges and re-ranks the results.

### Reciprocal Rank Fusion (RRF)
Because dense scores (Cosine similarity: 0.0 to 1.0) and sparse scores (BM25: 0 to arbitrary high numbers) are mathematically incompatible, you cannot simply add them together.
RRF merges the lists based on *rank* rather than *score*. 
Formula: `RRF Score = 1 / (k + Rank)` 
(where `k` is a smoothing constant, usually 60).
If a document is ranked #1 in BM25 and #3 in Vector Search, it gets a high combined RRF score.

## Production Implications
Pure vector search is rarely sufficient for production enterprise applications. Users instinctively search using keywords (e.g., "Invoice #49281"). If your system only uses dense embeddings, it will fail to retrieve the exact invoice, destroying user trust. Hybrid search is mandatory for most real-world RAG systems.

## Common Mistakes
- **Normalizing Incompatible Scores:** Trying to manually normalize and add BM25 scores to Cosine scores instead of using rank-based fusion (RRF).
- **Ignoring Tokenization for Sparse Search:** Failing to configure the BM25 tokenizer for domain-specific jargon, ruining the keyword search aspect.

## Interview Questions
- **Q: Why is Reciprocal Rank Fusion (RRF) used in hybrid search?**
  - *Answer:* Dense vector scores and sparse BM25 scores are on completely different, non-comparable scales. RRF ignores the raw scores and instead assigns a new score based on the item's rank in both respective lists, allowing for safe and effective merging of the results.

## Further Reading
- [Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) — The foundational RRF paper.
""",
    r"05-retrieval\01-query-transformation.md": """
# Query Transformation

## TL;DR
Users write terrible queries. Query transformation uses an LLM to rewrite, expand, or abstract the user's raw input before passing it to the vector database. This bridges the gap between conversational human language and optimal search semantics.

---

## The Problem with User Queries

A user might ask a chatbot: *"What about the second one?"* 
In the context of the conversation, this makes sense. But if you pass "What about the second one?" directly to a vector database, it will retrieve documents about "second ones," which is utterly useless. 

## Transformation Techniques

### 1. Query Rewriting (Contextualization)
- **Mechanism:** The LLM looks at the chat history and the current user input, and rewrites the query into a standalone, fully contextualized search string.
- **Example:** User says "How do I install it?". LLM rewrites to: "How do I install PostgreSQL 15 on Ubuntu?"

### 2. Multi-Query (Query Expansion)
- **Mechanism:** The LLM generates 3-5 variations of the user's query using synonyms and different phrasing. All variations are searched in the vector DB, and the results are aggregated and deduplicated.
- **Why it works:** Vector spaces are sensitive to exact phrasing. Generating multiple angles increases the chance of hitting the right semantic neighborhood.

### 3. HyDE (Hypothetical Document Embeddings)
- **Mechanism:** The LLM is prompted to write a *fake, hallucinated answer* to the user's query. This hallucinated document is embedded and used to search the vector DB.
- **Why it works:** Searching a vector space using a "document-like" vector often yields better results than searching with a "question-like" vector, because the embedding space is populated with documents, not questions.

### 4. Step-Back Prompting
- **Mechanism:** The LLM extracts higher-level, abstract concepts from a highly specific query.
- **Example:** User asks "Why did TSLA drop 5% on Tuesday?". The LLM generates a step-back query: "General factors affecting Tesla stock price volatility." Both are searched.

## Production Implications
Query transformation adds latency (an extra LLM call before the search even begins). To maintain a snappy UX, use small, fast, cheap models (like GPT-4o-mini or Claude Haiku) specifically fine-tuned or prompted for query rewriting. Do not use your heaviest model for this step.

## Common Mistakes
- **Passing Raw Chat Input:** Feeding conversational fragments directly into the embedding model.
- **Slow Transformations:** Using GPT-4 for query rewriting, adding 2 seconds of latency before retrieval starts.
- **Over-expansion:** Generating 10 query variants, blowing up the vector database load and retrieving too much noise.

## Interview Questions
- **Q: Explain how HyDE works in a RAG system.**
  - *Answer:* HyDE uses an LLM to generate a hypothetical answer to the user's question. This fake answer is then embedded and used to search the vector database. It works well because the vector of a hypothetical answer is geometrically closer to real answers in the database than the vector of the raw question.

## Further Reading
- [Precise Zero-Shot Dense Retrieval without Relevance Labels (HyDE)](https://arxiv.org/abs/2212.10496)
""",
    r"05-retrieval\02-semantic-search.md": """
# Semantic Search at Query Time

## TL;DR
Semantic search is the process of executing the transformed query against the vector database. It involves calculating similarity, setting dynamic thresholds, and retrieving the top-K chunks. Understanding how to filter and bound these results is critical to preventing irrelevant context from poisoning the LLM.

---

## The Search Execution

Once the user's query is embedded into a dense vector, the system queries the vector database using the Approximate Nearest Neighbor (ANN) index (like HNSW).

### Top-K Selection
- **Definition:** `K` is the number of results to return. 
- **The Tradeoff:** If `K` is too low (e.g., K=2), you might miss the critical document. If `K` is too high (e.g., K=20), you bloat the context window, increase latency/cost, and risk the LLM getting confused by irrelevant "distractor" chunks.

### Similarity Score Thresholds
Vector databases will always return `K` results, even if the documents are completely irrelevant to the query. They just return the *closest* vectors, even if the closest vector is still very far away.
- **Implementation:** Set a similarity threshold (e.g., Cosine Similarity > 0.75). If the top results fall below this threshold, the system should intercept and return "I don't have enough information to answer that," rather than passing garbage to the LLM.

## Pre-Filtering vs Post-Filtering

When combining metadata filters (e.g., `department = 'HR'`) with semantic search:
- **Pre-filtering:** The database filters down to only HR documents first, then runs the vector search. (Preferred, guarantees K results, but can be slow if the filter yields a very small subset and the index isn't optimized).
- **Post-filtering:** The database runs a vector search for the top 100 results, then removes those that aren't in the HR department. (Dangerous: if only 2 of the top 100 are HR, you return K=2 instead of K=10, degrading quality).

## Production Implications
Never blindly trust the Top-1 result. Semantic similarity does not equal factual relevance. The vector representing "User login failed" is almost identical to "User login succeeded". If the system relies purely on similarity without thresholds, it will confidently hallucinate using the wrong context.

## Common Mistakes
- **No Thresholds:** Passing retrieved chunks to the LLM even when the similarity score is extremely low.
- **Static K Values:** Always returning exactly 5 documents, regardless of whether 1 or 10 documents are actually highly relevant.

## Interview Questions
- **Q: Why will a vector database always return results, even if the user asks a completely irrelevant question?**
  - *Answer:* Vector databases perform nearest-neighbor searches. There is always a "nearest" vector in the geometric space, even if the absolute distance is large. Without setting a similarity threshold, the system will return the least irrelevant chunks and treat them as fact.

## Further Reading
- [Nearest Neighbor Search (Wikipedia)](https://en.wikipedia.org/wiki/Nearest_neighbor_search)
""",
    r"05-retrieval\03-reranking.md": """
# Reranking

## TL;DR
Reranking is a secondary filtering stage. A vector database retrieves a broad set of candidates (e.g., Top 20) very quickly using bi-encoders, and then a heavy, highly accurate cross-encoder scores and reorders them, sending only the absolute best (e.g., Top 5) to the LLM.

---

## Bi-Encoders vs Cross-Encoders

### Bi-Encoders (The Vector Database)
- **How it works:** The query and the document are embedded separately. Their similarity is computed using a simple dot product or cosine distance.
- **Pros:** Incredibly fast. Document embeddings can be pre-computed and indexed.
- **Cons:** Shallow understanding. The model never looks at the query and the document at the same time.

### Cross-Encoders (The Reranker)
- **How it works:** The query and the document are concatenated (e.g., `[CLS] Query [SEP] Document [SEP]`) and passed through a Transformer model *together*. The model outputs a relevance score from 0 to 1.
- **Pros:** Deep, highly accurate understanding of the relationship between the exact query and the document text.
- **Cons:** Too slow to run on millions of documents. Cannot be pre-computed.

## The Two-Stage Retrieval Pipeline

To get the best of both worlds, modern RAG systems use a two-stage pipeline:
1. **Stage 1 (Retrieval):** The Vector DB uses Bi-Encoders to instantly retrieve the Top 20-50 candidates from millions of records.
2. **Stage 2 (Reranking):** A Cross-Encoder model (like Cohere Rerank or BGE-Reranker) scores those 20-50 candidates against the specific query. 
3. **Selection:** The system discards the lowest scorers and passes only the Top 3-5 to the LLM context window.

## Production Implications
Reranking is arguably the highest ROI addition to a standard RAG pipeline. Dense vector search is noisy. A document might rank #1 in vector search because it shares vocabulary, but rank #15 in actual usefulness. A cross-encoder fixes this alignment. The latency cost (typically 50-200ms) is well worth the dramatic increase in prompt context quality.

## Common Mistakes
- **Reranking Too Many Docs:** Passing 1,000 documents to a cross-encoder will cause massive latency spikes and API costs.
- **Skipping Reranking:** Relying solely on the raw Cosine Similarity score from the vector database to order context for the LLM.

## Interview Questions
- **Q: Why can't we use Cross-Encoders for the initial database search?**
  - *Answer:* Cross-encoders must process the query and the document simultaneously. You cannot pre-compute cross-encoder scores. Running a heavy transformer model in real-time against millions of documents for every user query would take hours and immense compute.

## Further Reading
- [Cohere Rerank Documentation](https://docs.cohere.com/docs/reranking) — Excellent explanation of the two-stage pipeline.
""",
    r"05-retrieval\04-context-assembly.md": """
# Context Assembly

## TL;DR
Context assembly is the art of combining retrieved chunks, user queries, system instructions, and formatting into the final prompt sent to the LLM. Poor assembly leads to the "Lost in the Middle" phenomenon, where the model ignores critical facts, causing hallucinations despite perfect retrieval.

---

## Prompt Structure

A robust RAG prompt must clearly demarcate instructions from context. Use XML tags or Markdown to separate them, preventing prompt injection and confusion.

```text
You are a factual assistant. Answer the question using ONLY the provided <context>. 
If the context does not contain the answer, say "I don't know."

<context>
[Document 1: ...]
[Document 2: ...]
</context>

Question: {user_query}
```

## The "Lost in the Middle" Problem

LLMs have an attention distribution problem. Research shows that models exhibit a "U-shaped" attention curve:
- They perfectly recall information at the **very beginning** of the prompt.
- They perfectly recall information at the **very end** of the prompt.
- They severely degrade at recalling information stuck in the **middle** of the prompt.

### Ordering Strategies
Because of this phenomenon, chronological or arbitrary ordering of chunks is dangerous.
- **Optimal Ordering:** Place the highest-scoring (most relevant) chunks at the extreme ends of the context window.
  - Chunk #1 (Highest score) -> Placed at the very top.
  - Chunk #2 -> Placed at the very bottom.
  - Chunks #3, #4, #5 -> Placed in the middle.

## Context Window Budgeting

Just because a model has a 128k token context window doesn't mean you should fill it.
- **Cost:** API costs scale linearly with tokens.
- **Latency:** Time-to-first-token (TTFT) degrades as prompt length increases.
- **Distraction:** More chunks mean more irrelevant noise, increasing hallucination rates.
- **Rule of Thumb:** Cap your context to the Top 3-5 highly relevant, reranked chunks unless synthesizing across a massive dataset is explicitly required.

## Production Implications
Failing to structure the prompt with clear delimiters allows the LLM to confuse user input with retrieved context. If a retrieved document contains a hypothetical question, the LLM might answer the document's question instead of the user's question.

## Common Mistakes
- **Blind Concatenation:** Smushing chunks together without document boundaries (e.g., `Doc 1`, `Doc 2`), preventing the model from citing sources.
- **Context Stuffing:** Passing 50 chunks into GPT-4 just because it fits, leading to slow, expensive, and degraded responses.
- **Ignoring Attention Curves:** Putting the best document in the middle of a 20k token prompt.

## Interview Questions
- **Q: What is the "Lost in the Middle" phenomenon in LLMs, and how do you mitigate it in RAG?**
  - *Answer:* It's the tendency of LLMs to ignore or forget information located in the center of a long prompt, focusing instead on the beginning and end. To mitigate this, RAG systems should place the most highly relevant retrieved chunks at the very beginning and very end of the context section.

## Further Reading
- [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)
""",
    r"06-generation-and-guardrails\01-grounded-generation.md": """
# Grounded Generation

## TL;DR
Grounded generation is the process of forcing the LLM to synthesize an answer strictly based on the retrieved context, suppressing its parametric (internal) memory. This is the final defense against hallucinations and requires strict system prompting and citation enforcement.

---

## Suppressing Parametric Memory

LLMs naturally want to use their training data to answer questions. If the retrieved context says "The sky is green," but the LLM knows the sky is blue, a poorly prompted model will answer "The sky is blue," violating the grounding principle.

### Strict System Prompting
You must explicitly command the model to defer to the context.
- **Bad:** "Answer the user's question based on the context."
- **Good:** "You are a strict data synthesizer. Answer the question using ONLY the provided text. Do not use outside knowledge. If the context contradicts your internal knowledge, use the context. If the context does not contain the answer, reply exactly with 'I cannot answer this based on the provided documents'."

## Forcing Citations

Citations are critical for user trust and verifiability. 
- **Inline Citations:** Prompt the model to append source tags to sentences (e.g., "The revenue grew by 10% [doc_1].").
- **Post-hoc verification:** By forcing the model to cite the exact chunk, you enable downstream validation scripts to check if `doc_1` actually contains the claim.

## Handling "No Context" Scenarios

If the retrieval pipeline fails to find relevant chunks, the LLM will often try to "be helpful" and guess the answer anyway.
- **Mitigation:** The prompt must define an explicit failure state. The LLM must be given permission to fail gracefully.

## Production Implications
An ungrounded RAG system is just an expensive hallucination engine. If users cannot verify *where* the model got its answer, they will not trust the application for high-stakes enterprise decisions. Citations transform a black-box LLM answer into an auditable research report.

## Common Mistakes
- **Weak System Prompts:** Not being aggressive enough in commanding the LLM to ignore its training data.
- **Fake Citations:** The model hallucinating a citation like `[doc_4]` when only 3 documents were provided (often fixed by formatting the context strictly and using lower temperature).
- **High Temperature:** Using a high temperature (e.g., 0.8) for RAG generation. Fact retrieval should use low temperatures (0.0 - 0.1) for deterministic synthesis.

## Interview Questions
- **Q: How do you prevent an LLM from answering a question when the retrieved documents do not contain the relevant information?**
  - *Answer:* Set the temperature to 0. Use strict system prompts explicitly stating "If the context does not contain the answer, output exactly 'Insufficient context'." Additionally, implement similarity score thresholds in the retrieval step to prevent irrelevant documents from reaching the prompt in the first place.

## Further Reading
- [Evaluating RAG Systems (RAGAS)](https://github.com/explodinggradients/ragas) — Metrics for measuring groundedness and faithfulness.
""",
    r"06-generation-and-guardrails\02-output-validation.md": """
# Output Validation

## TL;DR
Output validation is a post-generation safeguard that evaluates the LLM's response before showing it to the user. It systematically checks for hallucination, faithfulness to the source text, and policy adherence, ensuring the system fails safely rather than lying confidently.

---

## The Three Pillars of Validation

### 1. Faithfulness (Hallucination Detection)
Does the generated answer logically follow from the retrieved context, or did the model invent facts?
- **Implementation:** Use a secondary, smaller LLM as a "Judge." Pass it the retrieved context and the generated answer, and ask: "Does the answer contain any claims not supported by the context? Output TRUE or FALSE." 
- **NLI (Natural Language Inference):** Some systems use specialized NLI models to check for entailment vs contradiction between the context and the answer.

### 2. Answer Relevance
Does the generated answer actually address the user's query?
- Sometimes a model perfectly summarizes the context, but the context didn't actually answer the user's question. The model evaded the question rather than admitting it didn't know.

### 3. Toxicity and Policy Guardrails
Checking the output against company policies, preventing PII leakage, and ensuring the tone is appropriate.

## The Validation Loop (Self-Correction)

Validation is most powerful when tied to a self-correction loop.
1. Generate Answer.
2. Run Faithfulness Check.
3. If `FALSE` (hallucination detected), append the Judge's feedback to the prompt and ask the primary LLM to regenerate the answer, fixing the errors.
4. If it fails 3 times, return a fallback message to the user.

## Production Implications
LLMs will hallucinate. It is not an "if", it is a "when." In high-stakes domains (healthcare, legal, finance), a hallucination can cause catastrophic damage. Output validation acts as the safety net, intercepting lies before they reach the user interface. It increases latency (due to the secondary LLM call), but this is a necessary tradeoff for reliability.

## Common Mistakes
- **No Validation:** Trusting the generative model blindly.
- **Validating on the Client Side:** Exposing the raw, unvalidated stream to the user, meaning they see the hallucination before it can be intercepted.
- **Overly Strict Judges:** Using prompt templates for the Judge that flag perfectly accurate paraphrasing as "unsupported claims," causing endless regeneration loops.

## Interview Questions
- **Q: What is "LLM-as-a-Judge" in the context of RAG validation?**
  - *Answer:* It's the pattern of using a separate LLM call to evaluate the output of the main generation step. The Judge LLM compares the generated answer against the retrieved chunks to detect hallucinations, contradictions, or lack of relevance before the final response is shown to the user.

## Further Reading
- [NeMo Guardrails (NVIDIA)](https://github.com/NVIDIA/NeMo-Guardrails) — Open-source toolkit for adding programmable guardrails to LLM applications.
""",
    r"07-advanced-rag\01-agentic-rag.md": """
# Agentic RAG

## TL;DR
Standard RAG is a rigid, linear pipeline (Retrieve -> Generate). Agentic RAG gives the LLM autonomy (tool calling) to decide *whether* to retrieve, *what* to retrieve, and when to execute *multiple* retrieval hops to synthesize an answer. It solves complex, multi-part questions that break standard vector search.

---

## When Standard RAG Fails

Standard RAG fails on "Multi-hop" reasoning.
**Query:** "Did the company that acquired WhatsApp have higher revenue in 2023 than the company that acquired GitHub?"
A single vector search for this query will fail. The vector DB doesn't know who acquired WhatsApp or GitHub. 

## The Agentic Solution

In Agentic RAG, the LLM acts as an orchestrator with access to search tools.
1. **Planning:** The LLM decomposes the query: 
   - Step 1: Find who acquired WhatsApp.
   - Step 2: Find who acquired GitHub.
   - Step 3: Find 2023 revenue for Company A.
   - Step 4: Find 2023 revenue for Company B.
   - Step 5: Compare.
2. **Execution (Tool Calling):** The LLM issues discrete search queries to the vector DB (or SQL DB) iteratively, digesting the results of one search to formulate the next.

## Routing and Fallbacks

Agents can dynamically route queries to different data sources.
- If the query is "What is my vacation balance?", the agent routes to the HR SQL database via an API tool.
- If the query is "How do I setup the VPN?", the agent routes to the Vector DB containing IT wikis.

### CRAG (Corrective RAG)
An agentic pattern where an evaluator assesses the quality of the retrieved documents. If the vector DB returns poor results, the agent falls back to searching the public web (via a tool like Tavily or Bing) to fill the knowledge gap.

## Production Implications
Agentic RAG is vastly more powerful but much slower and harder to control. A standard RAG pipeline takes 1-2 seconds. An Agentic RAG workflow might require 5 sequential LLM calls, taking 15 seconds. It also introduces the risk of infinite loops if the agent fails to find the data and keeps re-searching.

## Common Mistakes
- **Using Weak Models for Agents:** Agentic tool-calling requires advanced reasoning capabilities. GPT-3.5 or small open-source models often get stuck in loops or format tool calls incorrectly.
- **No Timeout Constraints:** Letting an agent execute 20 sequential searches, blowing up API costs and leaving the user hanging.

## Interview Questions
- **Q: How does Agentic RAG handle a query that spans both unstructured PDF data and structured SQL data?**
  - *Answer:* The LLM is provided with multiple tools (e.g., `search_pdfs` and `query_database`). The agent analyzes the user's intent, calls the SQL tool to fetch structured data, calls the vector tool to fetch unstructured context, and synthesizes a final answer combining both sources.

## Further Reading
- [LangGraph](https://langchain-ai.github.io/langgraph/) — Framework for building stateful, multi-actor LLM agents.
""",
    r"07-advanced-rag\02-graphrag.md": """
# GraphRAG

## TL;DR
GraphRAG augments vector databases with Knowledge Graphs. Instead of just searching for semantically similar text, GraphRAG traverses extracted relationships (Nodes and Edges) to answer global questions about a dataset that scatter across hundreds of documents.

---

## The Blindspot of Vector Search

Vector databases are excellent for localized questions: "What is the penalty for breaching clause 4?" (The answer is neatly contained in one chunk).
They are terrible at global, holistic questions: "What are the common themes connecting the key figures across all these incident reports?"
Vector search cannot connect the dots across 50 disparate documents.

## How GraphRAG Works

### 1. Ingestion (Graph Construction)
During data ingestion, an LLM processes every text chunk to extract Entities (Nodes: People, Places, Organizations) and Relationships (Edges: "Invested In", "Reports To"). 
This data is stored in a Graph Database (like Neo4j).

### 2. Community Detection
Algorithms (like Leiden) group the extracted entities into hierarchical communities (e.g., a cluster of people involved in a specific project). The system then generates LLM summaries for each community.

### 3. Retrieval
When a user asks a global question, the system retrieves the relevant community summaries and traverses the graph relationships, providing a synthesized, top-down view of the dataset that a vector search could never piece together.

## When to use GraphRAG

- **Investigative Journalism / Legal Discovery:** Mapping out complex webs of corporate ownership or communication.
- **Medical Research:** Tracing relationships between genes, proteins, and diseases across thousands of papers.

## Production Implications
GraphRAG is highly computationally expensive during the ingestion phase. Extracting entities and relationships from every chunk requires massive LLM API usage. Microsoft’s GraphRAG pipeline can take hours and significant cost to process a medium-sized corpus. It should only be used when topological, relationship-based querying is a strict business requirement.

## Common Mistakes
- **Using GraphRAG for Simple Lookups:** Over-engineering a system with a knowledge graph when the user just wants to find specific factual sentences.
- **Entity Resolution Failures:** Failing to merge duplicate nodes (e.g., "Apple Inc." and "Apple") during construction, resulting in a fragmented, useless graph.

## Interview Questions
- **Q: What specific type of query does GraphRAG solve that standard Vector RAG fails at?**
  - *Answer:* Global, holistic queries that require connecting concepts spread across many documents, such as "Summarize the overarching relationship between Company A and its subsidiaries based on all meeting notes."

## Further Reading
- [Microsoft GraphRAG](https://microsoft.github.io/graphrag/) — Microsoft's open-source system for hierarchical knowledge graph extraction and retrieval.
""",
    r"07-advanced-rag\03-multimodal-rag.md": """
# Multimodal RAG

## TL;DR
Multimodal RAG extends the retrieval and generation pipeline beyond text, allowing systems to ingest, search, and reason over images, charts, diagrams, and audio alongside traditional text documents. 

---

## The Multimodal Ingestion Challenge

Standard RAG strips out images during PDF parsing, destroying the value of documents heavily reliant on charts (e.g., financial earnings reports, medical records).

### Two Approaches to Multimodal Indexing

**1. Text-Summary Indexing (The Practical Approach)**
- **How it works:** During ingestion, every image/chart is passed to a Vision-Language Model (VLM like GPT-4o). The VLM generates a detailed text summary of the image. This text summary is embedded and stored in the vector database. A reference to the original image URL is stored in the metadata.
- **Retrieval:** The query hits the text summary. The system retrieves the metadata URL and passes the actual raw image to the VLM during the final generation step.

**2. Direct Multimodal Embedding (The Future)**
- **How it works:** Models like CLIP or ColPali can embed images and text into the exact same vector space. You embed the image directly.
- **Retrieval:** A user's text query is embedded and directly retrieves the most similar image vector. No intermediate text summarization is required. 

## ColPali and Vision-First Retrieval

Recent architectures like ColPali bypass traditional OCR and text extraction entirely. They treat document pages as raw images, embed the visual patches using Vision Transformers, and retrieve pages visually. This perfectly preserves complex layouts, tables, and nested charts without error-prone PDF parsing.

## Production Implications
Multimodal generation is significantly more expensive and slower than text-only generation. Passing 5 high-resolution retrieved images into GPT-4o for context assembly consumes massive token budgets. Furthermore, VLM accuracy on complex data visualizations (like dense scatter plots) is still imperfect.

## Common Mistakes
- **Embedding Base64 Images:** Trying to store massive Base64 strings directly in the vector database payload, crashing the database memory. Store URLs/paths instead.
- **Ignoring Image Context:** Summarizing a chart without providing the VLM the surrounding text, resulting in a summary that misses the point of the visualization.

## Interview Questions
- **Q: Explain how you would implement RAG over a dataset of slide decks containing complex charts.**
  - *Answer:* I would extract the images during ingestion and use a VLM to generate textual descriptions of the charts. I embed these text descriptions in a vector DB, keeping the image S3 URLs in the metadata. At query time, I search the text vectors, retrieve the image URLs, and pass the raw images and the user query to a multimodal model to generate the final answer.

## Further Reading
- [ColPali: Efficient Document Retrieval with Vision Language Models](https://arxiv.org/abs/2407.01449)
""",
    r"07-advanced-rag\04-semantic-caching.md": """
# Semantic Caching

## TL;DR
Semantic caching stores the results of previous LLM generations based on the semantic meaning of the user query, rather than an exact string match. It drastically reduces API costs, cuts latency to milliseconds, and scales RAG systems for high traffic.

---

## The Inefficiency of Exact Caching

Traditional caching (e.g., Redis) uses exact string matching. 
If User A asks: *"How do I reset my password?"* and User B asks *"How can I change my password?"*, an exact-match cache treats these as a cache miss, triggering the entire RAG pipeline (embedding, vector search, LLM generation) twice for the exact same intent.

## How Semantic Caching Works

Semantic caching uses a fast vector database layer in front of the main RAG pipeline.
1. User asks a question.
2. The question is embedded.
3. The system searches the Semantic Cache (a vector DB containing previous questions and their LLM answers).
4. If a stored question is semantically identical (e.g., Cosine Similarity > 0.95), the system returns the cached answer instantly.
5. If no match is found, the system runs the full RAG pipeline, then stores the new question and answer in the cache.

## Popular Implementations

- **GPTCache:** An open-source library specifically designed for LLM caching.
- **Redis + Vector Similarity:** Using Redis Enterprise or Redis Stack to store strings with HNSW indices for rapid semantic lookup.

## Cache Invalidation Challenges

In traditional software, you invalidate the cache when the underlying data changes. In RAG, this is harder.
If the underlying document outlining the password reset policy is updated, the semantic cache still holds the old LLM answer.
- **TTL (Time to Live):** The simplest solution. Expire cached answers after 24 hours.
- **Dependency Tracking:** Complex systems map cached answers back to the specific chunk IDs they were generated from. If a chunk is updated, all cached answers citing that chunk are invalidated.

## Production Implications
LLM generation is the slowest and most expensive part of RAG. In customer support chatbots, the Pareto principle applies: 80% of users ask the same 20% of questions. Semantic caching intercepts these repetitive queries, reducing cloud compute costs by massive margins and delivering instant responses to end users.

## Common Mistakes
- **Threshold Too Low:** Setting the similarity threshold to 0.85, causing the cache to return answers to vaguely related but factually different questions.
- **Caching Personalized Data:** Accidentally caching an answer that includes User A's specific account details, and serving it to User B because their questions were semantically similar.

## Interview Questions
- **Q: What is the risk of using semantic caching in a highly dynamic RAG environment?**
  - *Answer:* Serving stale data. If the underlying knowledge base changes, the semantic cache will continue to serve outdated generated answers until the cache expires or is explicitly invalidated. 

## Further Reading
- [GPTCache Repository](https://github.com/zilliztech/GPTCache) — A library for creating semantic caches for LLMs.
"""
}

for rel_path, content in files.items():
    full_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

print("All docs generated successfully.")
