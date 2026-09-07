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
