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
