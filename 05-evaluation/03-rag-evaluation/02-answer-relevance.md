</Agent System Instructions>
<Answer Relevance>
## TL;DR
Answer Relevance measures how well the generated answer addresses the user's specific query. It is distinct from faithfulness: an answer can be perfectly faithful to the retrieved context but completely irrelevant to what the user actually asked. 

---

## Faithfulness vs. Answer Relevance

- **Faithfulness:** Does the answer match the *context*?
- **Answer Relevance:** Does the answer match the *query*?

**Scenario:**
- **Query:** "How do I reset my password?"
- **Retrieved Context:** "To update your billing info, go to settings. To reset your password, click 'Forgot Password' on the login screen."
- **LLM Answer:** "To update your billing info, go to settings."

This answer is **100% faithful** (the information is in the context), but it has **0% answer relevance** (it didn't answer the user's question).

## How to Measure Answer Relevance

Measuring relevance directly with LLM-as-a-judge (e.g., "Score how relevant this is from 1-10") can be noisy. The RAGAS framework uses an ingenious reverse-engineering approach:

1. Take the generated answer.
2. Prompt an LLM to generate *N* potential questions that this answer would be a good response for.
3. Compute the semantic similarity (using embeddings) between the user's *original query* and the *generated questions*.
4. **Relevance Score:** The mean cosine similarity across the *N* generated questions.

If the answer was truly relevant to the original query, the reverse-generated questions will closely match the original query. If the answer went on a tangent, the generated questions will diverge from the original query, resulting in a low score.

## Penalizing Incompleteness and Redundancy

High answer relevance requires being concise and direct. 
- **Incompleteness:** Failing to answer all parts of a multi-part query lowers relevance.
- **Redundancy:** Including massive amounts of irrelevant information (even if the correct answer is buried inside) lowers relevance. 

## Production Implications

Low answer relevance in production usually stems from two issues:
1. **Poor Retrieval (Context Precision):** The retriever pulled irrelevant documents, forcing the LLM to either say "I don't know" or hallucinate an answer based on the irrelevant docs.
2. **Poor Prompting:** The LLM is instructed to summarize everything in the context, rather than extracting only the specific answer the user requested.

## Common Mistakes
- Combining faithfulness and relevance into a single "quality" score. They diagnose different failure modes and must be tracked separately.
- Ignoring verbosity. An LLM that regurgitates 500 words to answer a yes/no question is providing an irrelevant experience, even if the "yes" is in there somewhere.

## Interview Questions
- **Can a RAG answer be faithful but irrelevant? Provide an example.**
  *Answer:* Yes. If the user asks for a password reset, and the context contains both password reset and billing info, the LLM might only summarize the billing info. The output is faithful to the context but irrelevant to the query.
- **How does the RAGAS framework calculate answer relevance without relying on subjective 1-10 scoring?**
  *Answer:* It uses an LLM to reverse-generate questions based on the generated answer, then calculates the embedding cosine similarity between the generated questions and the original user query.

## Further Reading
- → See [04-ragas-framework.md](./04-ragas-framework.md) for how this metric fits into the broader RAGAS suite.
