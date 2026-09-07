<Use Case: Legal Document AI>
## Objective
A law firm wants an AI system to analyze massive corporate M&A document dumps (often containing 10,000+ pages of contracts). The system needs to answer specific due diligence questions (e.g., "Are there any change-of-control provisions that trigger upon acquisition by a foreign entity?"). 

**Constraints:**
- Precision is the only thing that matters. A missed clause or hallucinated provision could cost millions and result in malpractice lawsuits.
- **Grounding is non-negotiable.** Every single sentence the AI generates MUST be backed by a specific citation to a specific page and paragraph in the source documents. The lawyers will not trust the AI; they will only use it as a glorified search engine that points them to the exact text.

## Why Standard RAG is Insufficient
Standard RAG embeds chunks and returns the top 5 most similar chunks.
- **Why it failed:** Legal concepts are often split across multiple clauses, amendments, and definitions sections. A standard RAG pipeline will grab a clause mentioning "change of control" but miss the amendment on page 400 that nullifies it. Furthermore, standard generation doesn't enforce strict citation mapping.
- **The Pivot:** We need an **Agentic RAG Pipeline with Strict Citation Grounding**. The system must proactively search for amendments and definitions related to the clauses it finds.

## Technical Decisions

### Decision 1: Chunking Strategy
- **Chose:** Semantic / Structural Chunking (by clause/section).
- **Rejected:** Fixed-size token chunking (e.g., 500 tokens).
- **Rationale:** If you cut a legal sentence in half based on an arbitrary token count, the meaning is destroyed. We used a specialized legal parser to chunk the documents structurally (Clause 1.1, Clause 1.2) so that every chunk is a complete legal thought.

### Decision 2: Grounding and Citation Enforcement
- **Chose:** Prompt chaining with a separate verification step.
- **Rejected:** Asking the generation LLM to "provide citations" in a single prompt.
- **Rationale:** If you just ask an LLM to provide citations, it will often hallucinate the citation itself (e.g., citing "Section 4(b)" when no such section exists). We implemented a two-step chain. Step 1 generates the answer and quotes the text. Step 2 (deterministic code) runs a string-matching algorithm to verify the exact quoted text exists in the retrieved chunks. If it doesn't match perfectly, the generation is rejected.

### Decision 3: Handling Long Documents (Context Window Management)
- **Chose:** Map-Reduce summarization for document-level questions.
- **Rejected:** Stuffing 100k tokens into a single prompt.
- **Rationale:** For global questions ("Summarize the risks across all 50 contracts"), we run a parallel map process. 50 parallel LLM calls extract risks from each contract independently. A final reduce step synthesizes those 50 lists into one master report.

## Architecture Walkthrough

```python
def legal_qa_pipeline(query: str, corpus_id: str) -> dict:
    # 1. Agentic Search (Find definitions and clauses)
    # The agent might issue multiple searches if it finds a capitalized term 
    # that requires looking up the Definitions section.
    retrieved_chunks = agentic_legal_search(query, corpus_id)
    
    # 2. Draft Answer with Quotes
    draft = llm.predict(
        prompt=f"""Answer the query using ONLY the provided chunks. 
        You MUST quote the exact text supporting your answer.
        Chunks: {retrieved_chunks}""",
        schema=DraftResponse # Requires a list of {"claim": str, "exact_quote": str}
    )
    
    # 3. Deterministic Grounding Verification
    verified_claims = []
    for claim in draft.claims:
        # String match the quote back to the original document chunks
        source_chunk = find_exact_match(claim.exact_quote, retrieved_chunks)
        if source_chunk:
            verified_claims.append({
                "text": claim.claim,
                "citation": source_chunk.metadata.location # e.g., "Doc A, Page 12, §4"
            })
        else:
            # If the LLM hallucinated the quote, we silently drop the claim
            log_hallucination(claim)
            
    # 4. Final Formatting
    return format_legal_memo(verified_claims)
```

## Lessons Learned

1. **The "Definitions" Problem:** Legal documents heavily rely on defined terms (e.g., "The 'Subject Entity'"). Standard vector search fails because "Subject Entity" isn't semantically similar to "Acme Corp". We had to implement an upfront extraction pipeline that builds a dictionary of all defined terms in a contract. The query rewriting step then injects these definitions into the search query.
2. **String Matching is Brutal:** PDF extraction often introduces weird spacing or character corruption. Our deterministic string-matching verification step kept failing because the LLM would output "change of control" but the PDF text was "change  of control". We had to implement normalized string matching (stripping whitespace and punctuation) to reliably ground the citations.
</Use Case: Legal Document AI>
