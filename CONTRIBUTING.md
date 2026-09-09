# Contributing to AI Engineering Knowledge Base

Thank you for contributing! This knowledge base grows through community expertise.

---

## What We're Looking For

### High-Value Contributions
- **Corrections** — Technical inaccuracies, outdated information, wrong claims
- **New use-case.md files** — Real engineering scenarios that illustrate module concepts
- **New `use-case.md` files** — Real engineering scenarios that illustrate module concepts
- **Deeper explanations** — Where an existing file is too shallow
- **Production examples** — Code snippets and real failure modes
- **Updated tooling references** — APIs, pricing, and libraries change frequently

### Low-Priority (please check first)
- Rewrites of files that are already complete
- Adding more content to files that are already long
- Style/formatting changes without content improvement

---

## Git Workflow

### For small additions (a file or two) — push directly to `main`

```bash
# 1. Make sure you're on the latest version
git pull origin main

# 2. Make your changes in the correct directory

# 3. Commit with a clear message
git add <file>
git commit -m "feat(02-rag): add advanced multimodal RAG techniques"

# 4. Push
git push origin main
```

### For large additions (multiple files or a new module) — use a branch

```bash
# Create a branch
git checkout -b feat/add-module-08-multimodal

# Work on it...

# Merge when done
git checkout main
git merge feat/add-module-08-multimodal
git push origin main
```

---

## Commit Message Convention

```
feat(module):     New content
fix(module):      Correction to existing content
expand(module):   Adding to an existing file
refactor(module): Restructuring without new content
```

**Examples:**
```
feat(03-agentic-ai): add LangGraph state machines deep dive
fix(01-llm-fundamentals): correct RoPE formula in positional encoding
expand(06-production): add Redis Cluster setup to caching strategies
feat(resources): update further-reading with 2025 papers
```

---

## Where to Put New Content

```
Adding something new?
│
├── New file inside an existing module
│   └── Place it in the correct subfolder, follow the numbering
│       e.g. if the last file is 04-xxx.md → yours is 05-xxx.md
│
├── New subsection inside an existing module
│   └── Add the new directory + update that module's README.md
│
└── Entirely new module
    └── Use a branch + follow the same structure:
        README.md + use-case.md + numbered files
```

---

## File Standards

Every file should follow the format in each module's `README.md`. Key rules:

1. **No placeholders** — Every file must have real content
2. **Production-first** — Frame concepts through what breaks in production
3. **One concept per file** — Don't expand scope
4. **600–1500 words** — Deep but focused. Not a textbook chapter.
5. **Cross-link** — Reference related files in other modules

## Pull Request Process
---

1. Fork the repo
2. Create a branch: `feature/add-xyz` or `fix/correction-in-xyz`
3. Write your content
4. Submit a PR with a description of what you changed and why

## Reporting Issues

Open a GitHub issue with:
Open a GitHub Issue with:
- Which file the problem is in
- What is wrong or missing
- A suggested correction if you have one

---

## Pull Request Process

1. Fork the repo
2. Create a branch: `feat/add-xyz` or `fix/correction-in-xyz`
3. Write your content following the file standards above
4. Submit a PR with a description of what you changed and why
