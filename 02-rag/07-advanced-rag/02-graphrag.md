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
