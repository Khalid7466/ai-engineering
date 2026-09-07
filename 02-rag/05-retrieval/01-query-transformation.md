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
