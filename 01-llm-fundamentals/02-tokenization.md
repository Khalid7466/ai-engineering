# Tokenization

## TL;DR
Tokenization is the process of breaking text down into smaller chunks (tokens) that an LLM can process. A token is not necessarily a full word; it can be a syllable, a single character, or a common subword. Understanding tokenization is critical because tokens are the atomic unit of cost, latency, and context window limits in production.

---

## The "Token != Word" Trap
A common misconception is that 1 token = 1 word. In reality, for English, 1 token is roughly 4 characters or 0.75 words. 

Consider the word: `unhappiness`
A subword tokenizer might break this into: `['un', 'happi', 'ness']` (3 tokens).

LLMs do not see text; they see arrays of integers representing these tokens. 
"Hello world" might become `[15496, 995]`.

## Byte-Pair Encoding (BPE)
Most modern LLMs (like GPT-4 and Llama 3) use a subword tokenization algorithm called Byte-Pair Encoding (BPE) or similar variants (like Tiktoken or SentencePiece).

**How BPE works conceptually:**
1. Start with a vocabulary of individual characters or bytes.
2. Find the most frequently adjacent pair in the training corpus (e.g., 't' and 'h').
3. Merge them into a new single token ('th') and add it to the vocabulary.
4. Repeat this process thousands of times until you reach a target vocabulary size (e.g., 50,257 for GPT-2, or 128,000 for GPT-4o).

This creates a highly efficient vocabulary where common words ("the", "apple") are single tokens, while rare words or misspellings are broken down into multiple subword tokens.

## Multilingual and Code Tokenization Discrepancies
Tokenizers are biased by their training data. Because early tokenizers were trained predominantly on English text, they are highly efficient for English but horribly inefficient for other languages.

For example, the phrase "Hello world" in English might be 2 tokens. The exact same meaning in Arabic or Korean might cost 8 to 15 tokens. 

**Why Arabic costs more:** The tokenizer didn't see enough Arabic during its vocabulary building phase to create single tokens for common Arabic words. Therefore, it has to fall back to single characters or byte-level representations. 

Newer models like GPT-4o and Claude 3 have expanded their vocabularies specifically to improve multilingual and coding (e.g., handling spaces/tabs) token efficiency.

## Production Implications
- **Cost:** API providers charge per 1,000 tokens, not per word. If you process non-English languages, your API costs will be significantly higher for the same amount of semantic information.
- **Context Limits:** A 128k token context window holds roughly 100k English words, but maybe only 30k words of Japanese.
- **Formatting and Trailing Spaces:** ` " Hello"` (with a leading space) often maps to a completely different token ID than `"Hello"`. This can severely impact prompt formatting and few-shot examples if not handled consistently.
- **Spelling and Math:** Because LLMs see tokens, not letters, they struggle with tasks like "How many 'r's are in strawberry?". The word is represented as a single token (e.g., ID 4938), so the model doesn't inherently "see" the individual characters unless it has learned the spelling through pre-training.

## Common Mistakes
- **String length limits:** Using `len(text) < 8000` to prevent context window overflows. You must use a tokenizer library (like `tiktoken`) to count actual tokens.
- **Assuming API cost scales linearly with word count:** Failing to account for code blocks, JSON formatting (lots of spaces and braces), or multilingual text which heavily inflate token counts.
- **Mismatched tokenizers:** Using the Llama tokenizer to count tokens before sending a payload to the OpenAI API. Always use the exact tokenizer designed for the specific model.

## Interview Questions
- **Q: Why do LLMs struggle to play Wordle or spell words backwards?**
  - *A:* Because they don't see characters. They see integer IDs representing subwords or whole words. Asking them to manipulate characters is like asking a human to describe the atomic structure of a brick they are holding.
- **Q: How would you accurately enforce a context window limit in a Python application calling GPT-4?**
  - *A:* I would use the `tiktoken` library, specifically the encoding for GPT-4 (`cl100k_base` or `o200k_base`), to encode the string into tokens and count the length of the resulting array, rather than relying on string length or word counts.

## Further Reading
- [OpenAI Tiktoken repository](https://github.com/openai/tiktoken) - Fast BPE tokeniser for use with OpenAI's models.
- [Let's build the GPT Tokenizer (Andrej Karpathy)](https://www.youtube.com/watch?v=zduSFxRajkE) - Deep dive into how BPE works.
