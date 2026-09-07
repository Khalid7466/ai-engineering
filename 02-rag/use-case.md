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
</Use Case: Legal Entity Search>
