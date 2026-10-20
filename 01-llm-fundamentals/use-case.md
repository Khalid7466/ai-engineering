<Use Case: Medical Q&A Bot>

## Objective
The goal was to build a clinical Q&A bot to assist medical professionals by answering questions based on patient histories and medical guidelines. The system needed to provide accurate, reliable, and evidence-based answers.

## Why The Naive Approach Fails Here
The initial implementation used a standard ChatCompletion call with a default `temperature=1.0` (as used in standard conversational bots) and fed unstructured patient data directly into the prompt. While this produced conversational, fluent, and highly plausible answers during demos, it proved dangerous in production. 

The LLM is inherently a probabilistic engine designed for next-token prediction, not a database lookup. At high temperatures, it favors diversity over determinism, leading to hallucinated dosages or merging patient symptoms across documents. A statistically plausible but medically incorrect dosage can cause severe harm.

## Technical Decisions

### Decision 1: Temperature and Sampling Parameters
- **Chose:** `temperature=0.0`, `top_p=0.1`
- **Rejected:** `temperature=1.0`, default sampling.
- **Rationale:** Medical data requires high precision and determinism. By setting temperature to 0, we force the model to consistently pick the most probable next token (greedy decoding). This drastically reduces the variance and creative "leaps" the model takes, ensuring that it sticks closely to the facts presented in its context.

### Decision 2: Structured Outputs
- **Chose:** Pydantic schemas enforced via API (e.g., OpenAI's structured outputs / JSON mode).
- **Rejected:** Free-text generation.
- **Rationale:** We needed to ensure that the output always contained specific fields: `Diagnosis`, `Recommended_Dosage`, `Contraindications`, and `Citations`. Forcing the model into a rigid JSON structure meant the application layer could parse, validate, and flag missing data programmatically before ever showing it to a user.

### Decision 3: Grounding (Retrieval-Augmented Generation)
- **Chose:** Strict grounding against authoritative clinical guidelines.
- **Rejected:** Relying on the model's internal pre-trained weights.
- **Rationale:** Pre-trained weights are static and prone to hallucination when generating specific factual data. By retrieving exactly the relevant guideline and injecting it into the prompt ("Answer ONLY using the provided text"), we shifted the model's task from "recall from memory" to "reading comprehension."

## Architecture Walkthrough

```python
import openai
from pydantic import BaseModel, Field

client = openai.Client()

class ClinicalResponse(BaseModel):
    diagnosis: str
    recommended_dosage: str = Field(description="Exact dosage from context. If not found, output 'UNKNOWN'")
    citations: list[str] = Field(description="Exact quotes from the provided text")

def query_medical_bot(patient_history: str, clinical_guideline: str, user_question: str) -> ClinicalResponse:
    prompt = f"""
    You are a clinical assistant. Use ONLY the clinical guideline and patient history provided below.
    If the answer is not in the text, you must say 'UNKNOWN'.
    
    Patient History:
    {patient_history}
    
    Clinical Guideline:
    {clinical_guideline}
    
    Question: {user_question}
    """
    
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        response_format=ClinicalResponse
    )
    
    return response.choices[0].message.parsed
```

## Lessons Learned
1. **Context Window Limitations:** In v1, we stuffed entire patient electronic health records (EHR) into the prompt. We experienced the "lost in the middle" phenomenon (→ See [08-context-window.md](08-context-window.md)), where the model ignored critical drug allergies buried in the middle of a 20k-token prompt. We learned to aggressively chunk and summarize patient history before the final QA step.
2. **Plausibility vs. Truth:** We learned that an LLM will confidently lie if forced. Implementing the strict "Say UNKNOWN" escape hatch was crucial for safety.
3. **Structured extraction over generation:** Using the LLM to extract data into a schema is far safer than asking it to generate a narrative summary of a treatment plan.
</Use Case: Medical Q&A Bot>

---
<!-- nav:start -->
[Previous: LLM APIs and SDKs](16-llm-apis-and-sdks.md) | [Module Overview](README.md) | [Next: Module Overview](../02-rag/README.md)
<!-- nav:end -->
