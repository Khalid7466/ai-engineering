# Tokenization

## TL;DR
Tokenization is the process of breaking text down into smaller chunks (tokens) that an LLM can process. A token is not necessarily a full word; it can be a syllable, a single character, or a common subword. Understanding tokenization is critical because tokens are the atomic unit of cost, latency, and context window limits in production.

---

## The "Token != Word" Trap
A common misconception is that 1 token = 1 word. In reality, for English, 1 token is roughly 4 characters or 0.75 words. 

Consider the word: `unhappiness`
A subword tokenizer might break this into: `['un', 'happi', 'ness']` (3 tokens).

LLMs do not see text; they see arrays of integers representing these tokens. 
With the `cl100k_base` encoding (used by GPT-4), "Hello world" becomes `[9906, 1917]`. Different models use different vocabularies, so the same text gets different IDs.
These IDs are the input to the next stage, where each one is turned into a vector: see [03-embeddings.md](03-embeddings.md).

## Byte-Pair Encoding (BPE)
Most modern LLMs (like GPT-4 and Llama 3) use a subword tokenization algorithm called Byte-Pair Encoding (BPE), usually in its byte-level form. Libraries such as `tiktoken` and SentencePiece implement it (other algorithms exist too, such as WordPiece and Unigram).

**How BPE works conceptually:**
1. Start with a vocabulary of individual characters or bytes.
2. Find the most frequently adjacent pair in the training corpus (e.g., 't' and 'h').
3. Merge them into a new single token ('th') and add it to the vocabulary.
4. Repeat this process thousands of times until you reach a target vocabulary size (e.g., about 50k for GPT-2, about 100k for GPT-4's `cl100k_base`, and about 200k for GPT-4o's `o200k_base`).

This creates a highly efficient vocabulary where common words ("the", "apple") are single tokens, while rare words or misspellings are broken down into multiple subword tokens.

Tokenizers also reserve **special tokens**, such as an end-of-sequence marker (see [01-what-is-an-llm.md](01-what-is-an-llm.md)), that mark boundaries rather than represent text.

## Multilingual and Code Tokenization Discrepancies
Tokenizers are biased by their training data. Because early tokenizers were trained predominantly on English text, they are highly efficient for English but horribly inefficient for other languages.

For example, with `cl100k_base`, "Hello world" is 2 tokens, while the same greeting in Arabic (`مرحبا بالعالم`) is 10 and in Korean (`안녕하세요 세계`) is 9. The ratio depends on the tokenizer and the sentence, so measure your own text.

**Why Arabic costs more:** The tokenizer didn't see enough Arabic during its vocabulary building phase to create single tokens for common Arabic words. Therefore, it has to fall back to single characters or byte-level representations. 

Newer tokenizers, such as GPT-4o's `o200k_base` (about twice the size of `cl100k_base`), were built to improve token efficiency, including for non-English text. For the examples above it needs 4 and 3 tokens instead.

## Production Implications
- **Cost:** API providers charge per token (pricing pages typically quote a price per 1 million tokens), not per word. If you process non-English languages, your API costs will be significantly higher for the same amount of semantic information.
- **Context Limits:** A 128k token context window holds roughly 100k English words, and noticeably fewer for languages that tokenize less efficiently, such as Japanese or Arabic (see [08-context-window.md](08-context-window.md)). Measure with your own text.
- **Leading and Trailing Spaces:** `" Hello"` (with a leading space) usually maps to a different token than `"Hello"`. A prompt that ends with a trailing space can also change what the model predicts next. This can affect prompt formatting and few-shot examples if not handled consistently.
- **Spelling and Math:** Because LLMs see tokens, not letters, they struggle with tasks like "How many 'r's are in strawberry?". In `cl100k_base` the word is split into these subword tokens: `['str', 'aw', 'berry']`, so the model never directly sees the individual letters unless it has learned the spelling indirectly during pre-training.

## Common Mistakes
- **String length limits:** Using `len(text) < 8000` to prevent context window overflows. You must use a tokenizer library (like `tiktoken`) to count actual tokens.
- **Forgetting the output budget:** The context window covers input plus output. Reserve room for `max_tokens`, and remember that chat formats add a few tokens of overhead per message.
- **Assuming API cost scales linearly with word count:** Failing to account for code blocks, JSON formatting (lots of spaces and braces), or multilingual text which heavily inflate token counts.
- **Mismatched tokenizers:** Using the Llama tokenizer to count tokens before sending a payload to the OpenAI API. Always use the exact tokenizer designed for the specific model.

## Interview Questions
- **Q: Why do LLMs struggle to play Wordle or spell words backwards?**
  - *A:* Because they don't see characters. They see integer IDs representing subwords or whole words. Asking them to manipulate characters is like asking a human to describe the atomic structure of a brick they are holding.
- **Q: How would you accurately enforce a context window limit in a Python application calling GPT-4?**
  - *A:* I would use the `tiktoken` library (`tiktoken.encoding_for_model("gpt-4")`, which resolves to `cl100k_base`; GPT-4o uses `o200k_base`) to encode the string into tokens and count the length of the resulting array, rather than relying on string length or word counts. I would also reserve room for the output (`max_tokens`) and the per-message overhead of the chat format.

## Further Reading
- [OpenAI Tiktoken repository](https://github.com/openai/tiktoken) - Fast BPE tokeniser for use with OpenAI's models.
- [Let's build the GPT Tokenizer (Andrej Karpathy)](https://www.youtube.com/watch?v=zduSFxRajkE) - Deep dive into how BPE works.

---
<!-- nav:start -->
[Previous: What is an LLM?](01-what-is-an-llm.md) | [Module Overview](README.md) | [Next: Embeddings](03-embeddings.md)
<!-- nav:end -->
