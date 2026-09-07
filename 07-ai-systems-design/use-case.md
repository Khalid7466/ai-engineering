<Use Case: HR Platform AI Transformation>
## Objective
A fast-growing HR software startup wants to add "AI features" to their platform. The CEO and CTO have a broad mandate: "We want an AI that can answer employee questions about benefits, automatically generate job descriptions based on intake forms, and screen incoming resumes to identify top candidates."

The naive approach is to build one massive "HR Agent" with access to the employee handbook, job creation forms, and candidate databases, and let it figure things out. This is a recipe for a slow, expensive, and error-prone system. We need to decompose this into specific architectural patterns.

## Why a Single Agent Fails Here
If we build a single ReAct agent to handle all three tasks:
1. **Context Pollution:** The system prompt will be bloated with instructions for answering questions, formatting job descriptions, and evaluating resumes. The LLM will lose focus and hallucinate.
2. **Latency:** Answering a simple question like "What is the dental copay?" via an agentic loop (thought -> tool call -> observe -> response) will take 5-10 seconds. Users expect instant answers for simple queries.
3. **Cost and Reliability:** Resume screening needs to be high-throughput, deterministic, and fair. An open-ended agent will process resumes inconsistently, costing a fortune in LLM API calls and risking compliance violations.

## Technical Decisions: Decomposing the Problem

We must break the mandate into three distinct problems and architect a specific solution for each.

### Problem 1: Answering Employee Questions
Employees ask unstructured questions about HR policies, benefits, and company rules.

### Decision 1: Architecture for Q&A
- **Chose:** Standard RAG (Retrieval-Augmented Generation).
- **Rejected:** Autonomous Agent.
- **Rationale:** The execution path is fixed. An employee asks a question -> we retrieve the relevant policy document -> we generate an answer based *only* on that document. There is no need for dynamic tool use or multi-step reasoning. We need sub-2-second latency, which Standard RAG can provide.

### Problem 2: Generating Job Descriptions
Hiring managers fill out a brief 3-question intake form (title, team, 3 key responsibilities). The system needs to output a 500-word job description that matches the company's specific tone, formatting, and diversity guidelines.

### Decision 2: Architecture for Generation
- **Chose:** Fine-tuned Model (or highly constrained Prompt Chain).
- **Rejected:** Standard RAG.
- **Rationale:** We aren't retrieving facts; we are enforcing a specific style and structure. RAG is for injecting knowledge. Fine-tuning is for injecting style and structure. By fine-tuning a smaller, faster model (e.g., Llama 3 8B) on 1,000 past successful job descriptions, we get perfect tone alignment and predictable formatting with very low latency and cost. 

### Problem 3: Screening Resumes
The system receives 500 resumes for a job post. It needs to score them against the job requirements and output a structured JSON evaluation for each.

### Decision 3: Architecture for Screening
- **Chose:** Structured Pipeline with LLM Scoring (Parallel Map).
- **Rejected:** Multi-Agent System.
- **Rationale:** This is a high-throughput batch processing task. An agent would be too slow and unpredictable. We need a fixed pipeline: Extract text from PDF -> Map over all 500 resumes in parallel -> LLM evaluates exactly 5 criteria per resume -> Output structured JSON. This guarantees uniform evaluation and allows for massive parallelization.

## Architecture Walkthrough

Here is how the three systems operate independently within the platform:

```python
# 1. The Q&A RAG Pipeline (Fixed execution, low latency)
def answer_employee_question(user_id: str, query: str) -> str:
    # 1. Check permissions (metadata filtering)
    user_dept = get_user_department(user_id)
    
    # 2. Retrieve relevant chunks from vector DB
    chunks = vector_db.similarity_search(query, filter={"dept": user_dept})
    
    # 3. Generate answer grounded in context
    prompt = f"Answer '{query}' using ONLY this context: {chunks}. If unknown, say so."
    return llm.generate(prompt)

# 2. The Job Description Generator (Fine-tuned style)
def generate_job_description(intake_form_data: dict) -> str:
    # Using a model specifically fine-tuned on our company's JD style
    # We just pass the raw data, the model inherently knows the format
    formatted_input = format_intake(intake_form_data)
    return finetuned_llm.generate(formatted_input)

# 3. The Resume Screening Pipeline (Parallel batch processing)
async def screen_resumes(job_id: str, resumes: list[PDF]) -> list[dict]:
    requirements = db.get_job_requirements(job_id)
    
    # Process all resumes concurrently, not via an agent loop
    tasks = [
        score_resume(resume, requirements) 
        for resume in resumes
    ]
    results = await asyncio.gather(*tasks)
    
    return [r for r in results if r['score'] > MIN_THRESHOLD]

async def score_resume(resume: PDF, requirements: str) -> dict:
    text = extract_text(resume)
    # Force strict JSON output for programmatic downstream use
    return await structured_llm.predict(
        prompt=f"Evaluate this resume against {requirements}",
        schema=ResumeScoreSchema
    )
```

## Lessons Learned
- **V1 Failure:** The startup initially tried a "Langchain Zero-Shot ReAct Agent" with tools for PDF reading, vector search, and drafting. It took 45 seconds to answer a question, frequently hallucinated job descriptions, and crashed when trying to read 50 resumes at once.
- **The Pivot:** By forcing the product team to define the distinct workflows, the engineering team could select the right pattern for the right job. Fixed problems got fixed pipelines; stylistic problems got fine-tuning. 
- **The Result:** Latency dropped by 90%, cost decreased by 95%, and the output quality became predictable enough to trust in production.

→ See [01-architecture-decision-tree.md](01-architecture-decision-tree.md) for the framework used to make these decisions.
</Use Case: HR Platform AI Transformation>
