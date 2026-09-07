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
