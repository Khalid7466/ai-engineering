# Document Loaders

## TL;DR
Document loaders are the foundation of the indexing pipeline. They extract raw text from structured and unstructured sources (PDFs, HTML, Confluence, SQL). The choice of loader dictates whether structural semantics (like tables, charts, and headers) are preserved or destroyed, directly impacting downstream retrieval quality.

---

## The Parsing Challenge

Extracting text from a `.txt` file is trivial. Extracting text from a two-column PDF with embedded images and tables is a complex computer vision and parsing problem. If a loader simply reads left-to-right, top-to-bottom across a two-column PDF, it will interleave text from both columns, creating nonsensical sentences that destroy the semantic value of the document.

### PDF Parsing Strategies
- **Text-based (e.g., PyPDF2):** Fast, cheap, but layout-blind. It extracts text exactly as encoded in the PDF stream. Fails completely on multi-column layouts and complex tables.
- **Layout-aware (e.g., Unstructured.io, PDFMiner):** Uses heuristics or ML models to identify document layout (headers, footers, columns, lists, tables). Significantly slower but essential for complex documents.
- **Vision-based (e.g., LayoutLM):** Treats the document as an image and uses vision models to understand the structure. Highly accurate but computationally expensive.

### Handling Tables and Charts
Standard text extraction often flattens tables into unreadable strings of text separated by spaces. When this text is embedded, the vector represents noise.
- **Solution for Tables:** Use layout-aware parsers to extract tables as Markdown or HTML. This preserves the row/column relationships, allowing the LLM to comprehend the tabular data during generation.
- **Solution for Charts:** Requires a multimodal approach, using a Vision-Language Model (VLM) to generate a text summary of the chart during ingestion, which is then embedded and indexed.

## Production Implications
In production, documents are messy. You will encounter scanned PDFs (requiring OCR), corrupted files, and wildly varying layouts. If your loader fails silently or produces garbage text, your entire RAG pipeline is compromised. 

For instance, if a financial report's balance sheet is parsed as a single run-on paragraph, the LLM will hallucinate the revenue numbers because the context it receives is incomprehensible.

## Common Mistakes
- **Assuming all PDFs are text-based:** Failing to implement OCR for scanned documents.
- **Ignoring Document Structure:** Using naive loaders that destroy tables and multi-column layouts.
- **Failing to Capture Metadata:** Throwing away source URLs, page numbers, and authors during the loading phase.

## Interview Questions
- **Q: Why should you avoid simple text extractors for complex PDFs in a RAG system?**
  - *Answer:* Simple extractors are layout-blind. They fail on multi-column text, headers, and tables, producing mangled text that ruins the semantic embedding and prevents the LLM from understanding the context.

## Further Reading
- [Unstructured.io Documentation](https://unstructured-io.github.io/unstructured/) — The industry standard for layout-aware parsing.
