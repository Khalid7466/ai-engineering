# AI Engineering Knowledge Base — Project Guidelines & Rules

## 1. Project Overview & Philosophy

This repository is a production-first knowledge base for software engineers transitioning into AI Engineering. 

- **Production Consequence First:** Every concept must be tied directly to real-world consequences: latency, token cost, memory/VRAM footprint, determinism, safety, and failure modes. Avoid academic hand-waving or purely theoretical summaries.
- **Interconnected System:** Concepts do not live in isolation. Every module and file is presented as a component in a coherent, end-to-end engineering pipeline.
- **Zero Placeholders:** Every file must contain complete, high-quality, actionable technical content.

---

## 2. Git Workflow & Branching Strategy

To keep review manageable and maintain history hygiene:

1. **One Single Branch Per Module / Scope:**
   - Keep all edits for a module in a single branch (e.g., `docs/01-llm-fundamentals`, `docs/02-rag`).
   - Do NOT create auxiliary sub-branches for individual files or micro-fixes.
   - Always branch off the latest base branch for each module:
     ```bash
     git checkout -b docs/<module-name>  # e.g., docs/01-llm-fundamentals
     ```
2. **One Commit Per File (All File Edits in One Commit):**
   - Every file's edits (content updates, corrections, link additions, navigation footers, formatting) must be consolidated into **one single commit per file**.
   - Do NOT create multiple commits touching the same file across a branch. Stage all changes for that file together and commit atomically:
     ```bash
     git add <path/to/file.md>
     git commit -m "docs(NN): <actionable summary of all edits in file>"
     ```
3. **Human Review & Gating:**
   - Work module by module.
   - The user inspects and reviews changes (locally or remotely).
   - Do NOT push to remote or merge into `main` automatically unless explicitly instructed.

---

## 3. Module README Standards

Each module's `README.md` must give the reader a unified mental model of the entire module before diving into specific topics:

### Required Sections & Structure:

1. **`# Module NN: <Name>`**
2. **`## TL;DR`**: High-level summary of the module's domain and production significance.
3. **`## The Big Picture (Mind Map)`**:
   - A single Mermaid flowchart (`flowchart TD`).
   - Group files/subfolders logically using `subgraph`.
   - For modules with >25 files, provide a top-level subfolder flow plus focused subgraphs.
   - **Node syntax:** Quoted IDs and labels: `ID["NN Name<br/>one-line purpose"]`.
   - **Solid arrows (`-->`):** Sequential execution order, data pipeline flow, or primary conceptual dependencies.
   - **Dotted arrows (`-.->`):** Concepts that shape, constrain, produce weights, or govern a step.
   - **Caption:** 2-3 lines beneath the diagram explaining how to read solid vs. dotted arrows.
   - **Mermaid Syntax Rules:**
     - Always use `flowchart TD`.
     - Quote every label with double quotes (`"..."`).
     - Use `<br/>` for line breaks inside labels.
     - Never leave unquoted brackets, parentheses, slashes, or colons.
     - Ensure every node ID used in an edge is explicitly defined.
     - Maximum 40 nodes per diagram.
4. **`## Learning Path`**:
   - A Markdown table mapping all files in the module:
     ```markdown
     | # | File | The question it answers | Depends on |
     |---|------|------------------------|-----------|
     | 01 | [name](filename.md) | Practical question addressed | prior file IDs |
     ```
   - Must include every numbered `.md` file and `use-case.md`.
   - **"Depends on"** must reflect actual conceptual dependencies based on the content of the files, not merely sequential numbers.
5. **`## Prerequisites`**: Languages, mathematical tools, or concepts assumed known.
6. **`## Production Implications`**: Summary table or key points of operational trade-offs (latency, cost, throughput, edge failure modes).
7. **`## Where This Module Leads` (and `Builds on`):**
   - Concrete relative links to preceding and succeeding modules with 1-line engineering rationales.
8. **`## Further Reading`**: Foundational papers and authoritative production documentation.

---

## 4. Navigation Footers Standard (Previous / Next)

To facilitate smooth book-like reading, every concept file must end with a navigation footer.

### Scope:
- **Included:** Every `.md` file inside `01-*` through `07-*` that has a numeric prefix (e.g., `01-what-is-an-llm.md`) plus `use-case.md`.
- **Excluded:** Do **NOT** add footers to `README.md` files.

### Footer Format:
```markdown
---
<!-- nav:start -->
[Previous: <Title of Previous>](relative/path.md) | [Module Overview](relative/path/to/module/README.md) | [Next: <Title of Next>](relative/path.md)
<!-- nav:end -->
```

### Formatting & Idempotency Rules:
- Preceded by one blank line before the horizontal rule (`---`).
- `<Title>` must be extracted from the target file's primary `# ` H1 heading (read directly from the file, never guessed).
- For `README.md` targets, always use the literal text `"Module Overview"`.
- At boundaries where Previous or Next does not exist, omit that link and its surrounding ` | ` separator (never leave empty links or trailing separators).
- Use relative paths with forward slashes (`/`).
- Idempotent: If `<!-- nav:start -->` already exists, replace the content between markers instead of duplicating.
- **Deduplication:** Never output two links to the same file in one footer. If the `Previous` target resolves to the same file as `Module Overview` (`README.md`), omit the `Previous` link and its separator (e.g., in the first file of a module: `[Module Overview](README.md) | [Next: <Title>](next.md)`). Same for `Next`: if `Next` target equals `Module Overview`, omit the `Next` link.
- Preserve existing file line endings (LF vs CRLF) and trailing newlines. Do not alter any other lines in the file.

### Traversal Order:
1. **Within a folder:** Ascending numeric prefix order (`01`, `02`, `03`...), followed by `use-case.md` last (if present).
2. **Subfolder transitions:**
   - First file of a subfolder: `Previous` points to the last file of the preceding subfolder/file (or to the module `README.md` if it's the very first).
   - Last file of a subfolder: `Next` points to the first file of the next subfolder (or to `use-case.md` if at the end of subfolders).
3. **Module boundaries:**
   - First file of Module 01 (`01-llm-fundamentals/01-what-is-an-llm.md`): `Previous` points to `README.md`.
   - Final file/`use-case.md` of Modules 01 to 06: `Next` points to the next module's `README.md` (e.g. `../02-rag/README.md`).
   - Final file/`use-case.md` of Module 07: Has no `Next` link (the sequence terminates).

---

## 5. Technical Accuracy & Integrity

- **Grep Before You Claim:** Never state that "file X covers concept Y" without inspecting or grepping file X first.
- **No Speculative Dependencies:** If a dependency between two concepts is ambiguous, omit it from the diagram and document it under an "Uncertain" review list for user clarification.
- **Preserve Existing Quality:** Preserve all accurate existing explanations, docstrings, and diagrams. Never strip technical depth for brevity.
- **Reporting Inconsistencies:** If existing text in a module contradicts modern production practice or another file in the repo, report it in the review summary rather than silently rewriting it.

---

## 6. Verification Checklist (Before Finalizing Any Module)

Every module review/update must pass these programmatic checks:
- [ ] **Relative Links:** 100% of markdown links resolve to existing files (strip `#anchors` for path check).
- [ ] **Completeness:** Every single `.md` file in the module folder is referenced in the `Learning Path` table.
- [ ] **Mermaid Linting:** Diagram parses cleanly with no unclosed quotes, undefined node IDs, or syntax errors.
- [ ] **Footer Bidirectionality:** For every link `A -> B` via `Next`, `B -> A` via `Previous` holds true (except at defined module boundaries).
- [ ] **Git Diff Cleanliness:** `git diff` shows only intended README updates and footer appends at end of concept files.
