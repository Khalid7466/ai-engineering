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
