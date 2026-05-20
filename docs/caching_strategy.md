# Semantic Caching Strategy

This service uses a **semantic caching mechanism** to reduce unnecessary LLM calls when incoming support tickets are similar to previously processed ones. Instead of caching only exact text matches, the system compares the **semantic meaning** of tickets using vector embeddings.

This approach reduces both **latency and compute cost**, which is especially valuable in support systems where many tickets are repetitive or very similar.

---

# How the Semantic Cache Works

The caching workflow operates as follows:

1. **Embedding generation**
   - The incoming ticket text is converted into a vector embedding using an embedding model.
   - The vector represents the semantic meaning of the ticket.

2. **Similarity search**
   - The embedding is compared with previously stored ticket embeddings.
   - The similarity between vectors is computed using **cosine similarity**.

3. **Threshold evaluation**
   - If the similarity score between the new ticket and a cached one is **≥ 0.85**, the tickets are considered semantically equivalent.

4. **Cache hit**
   - The previously stored `TicketAnalysis` result is returned directly without calling the LLM.

5. **Cache miss**
   - If no cached embedding passes the threshold, the ticket is processed by the LLM.
   - The resulting analysis and embedding are stored in the cache for future reuse.

This mechanism allows the system to reuse previous results for semantically similar tickets.

---

# Embedding Model Choice

This project uses `sentence-transformers/all-MiniLM-L6-v2` as the embedding model for semantic cache lookup.

The model converts each ticket into a dense vector representation that captures its semantic meaning. These vectors are then compared using cosine similarity to determine whether a cached response can be reused.

### Why `all-MiniLM-L6-v2`

This model is well-suited for short support-ticket text because it offers a strong balance between accuracy and efficiency:

- Designed for **sentence similarity tasks**
- **Fast inference**, suitable for real-time systems
- **Lightweight** compared to larger transformer models
- Widely adopted and well-tested in production use cases

### Vector Size and Efficiency

`all-MiniLM-L6-v2` produces **384-dimensional embeddings**.

This relatively small vector size provides practical benefits:

- Lower memory usage for storing cached embeddings
- Faster cosine similarity computations
- Reduced storage overhead as the cache grows

### Fit for This Use Case

Support tickets are typically short, repetitive, and intent-focused. For this type of workload, `all-MiniLM-L6-v2` provides sufficient semantic quality while keeping latency and infrastructure costs low.

If higher precision is required in the future, the embedding model can be upgraded. However, for a production-ready semantic caching system, this model provides a reliable and efficient default choice.

---

# Similarity Threshold (0.85)

The system uses a **cosine similarity threshold of 0.85** to decide whether a new ticket is similar enough to an existing cached one.

Cosine similarity measures how close two embeddings are in meaning:

- **1.0** → identical meaning  
- **0.0** → unrelated  
- **-1.0** → opposite meaning  

A threshold of **0.85** represents a strong semantic match while still allowing small wording differences.

Example likely above 0.85:

- "I cannot log into my account"
- "Login to my account is not working"

Example likely below 0.85:

- "I cannot log into my account"
- "I want to cancel my subscription"

Only tickets that pass this threshold reuse a cached response.

---

# Trade-offs

The similarity threshold balances **cache efficiency** and **accuracy**.

### Lower threshold (e.g., 0.75)

Pros:
- More cache hits  
- Fewer LLM calls  
- Lower latency and cost  

Cons:
- Higher chance of incorrect matches  

### Higher threshold (e.g., 0.90–0.95)

Pros:
- More precise matches  
- Lower risk of wrong cached responses  

Cons:
- Fewer cache hits  
- More LLM calls and higher cost  

---

# False Positives vs Cost

A **false positive** occurs when a cached result is reused for a ticket that is not actually equivalent.

Example:

Cached ticket:  
> "My payment was charged twice"

New ticket:  
> "I want to change my payment method"

If the similarity threshold is too low, the system may reuse an incorrect cached result, leading to wrong classifications or summaries.

On the other hand, avoiding LLM calls saves **GPU compute time, latency, and operational cost**. Since many support tickets are repetitive (login issues, billing problems, password resets), semantic caching can significantly reduce the number of LLM requests.

---

# Why 0.85 Is a Practical Default

A threshold of **0.85** provides a good balance between accuracy and efficiency. It captures small wording variations while avoiding most unrelated matches.

For structured tasks like ticket classification and summarization, this value typically yields useful cache hit rates without significantly increasing the risk of incorrect results. The threshold can be adjusted later based on production metrics or offline evaluation.

---

# Summary

The semantic caching strategy improves system efficiency by avoiding redundant LLM calls for semantically similar tickets.

Key aspects of the approach:

- ticket text is converted to **vector embeddings**
- similarity is measured using **cosine similarity**
- a **0.85 similarity threshold** determines cache hits
- cached results bypass the LLM and return immediately

This design reduces latency and infrastructure cost while maintaining reliable classification results.
