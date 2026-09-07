# A/B Testing and Deploying Models

## TL;DR
Replacing a production LLM with a new version (or a different provider) carries immense risk because outputs are non-deterministic. A model that scores higher on a benchmark might fail on specific edge cases unique to your application. Safe deployment requires sophisticated rollout strategies—Shadow Mode, Canary Releases, and A/B Testing—combined with statistically significant evaluation before replacing the primary system.

---

## The Risk of the "Swap and Pray"

In traditional software, if version 2.0 passes all unit tests, you deploy it. 
In AI engineering, a prompt optimized for `gpt-4-0613` might perform terribly on `gpt-4-turbo`. The new model might be faster and cheaper, but its instruction-following behavior might drift, causing tool-call formats to fail or specific formatting constraints to be ignored.

Because you cannot write a deterministic unit test for every possible user input, you must test the model against live production traffic.

## Deployment Strategies

### 1. Shadow Mode (Dark Launching)
The safest way to evaluate a new model. The application logic routes the user's request to the current production model (Model A), which handles the response. 
Simultaneously, the backend asynchronously sends the exact same request to the new model (Model B). 
- **The Process:** Model B's output is logged but *never shown to the user*. 
- **The Value:** Over a week, you collect thousands of side-by-side outputs (Model A vs. Model B) generated from real production traffic. You can run automated "LLM-as-a-judge" evaluators over this dataset to compare them on cost, latency, and quality before exposing Model B to users.
- **The Cost:** You pay for double the inference.

### 2. Canary Release
Deploying the new model to a tiny subset of real users to monitor for catastrophic failures.
- **The Process:** The router sends 95% of traffic to Model A and 5% of traffic to Model B.
- **Monitoring:** You closely monitor the alerts (see → [05-alerting-and-dashboards.md](05-alerting-and-dashboards.md)) for the 5% group. If TTFT spikes, or the error rate jumps, the automated CI/CD pipeline triggers an immediate rollback to 100% Model A. If stable, traffic is gradually increased (5% -> 20% -> 50% -> 100%).

### 3. A/B Testing (The Scientific Approach)
Used when you want to measure the *business impact* of a new model, not just its technical stability. 
- **The Process:** Traffic is split 50/50. 
- **The Metrics:** You measure explicit or implicit user feedback. Does Model B result in higher conversion rates? Do users click "Thumbs Up" more often? Do users resolve their support tickets faster?
- **Statistical Significance:** Because LLMs are highly variable, you must collect a large enough sample size to ensure the difference in conversion rate is statistically significant (usually a p-value < 0.05), not just random noise.

## Traffic Splitting Architecture

Implementing these strategies requires a dynamic **Router**. 
Instead of hardcoding `OpenAI(model="gpt-4")` into the application logic, production systems use feature flags or configuration endpoints.

```python
# Simplified Traffic Splitter
def get_llm_response(prompt, user_id):
    # Hash the user ID to ensure consistent experience across sessions
    user_hash = hash(user_id) % 100
    
    if user_hash < config.canary_percentage:
        return model_b.generate(prompt) # Canary
    else:
        return model_a.generate(prompt) # Production
```
By linking `config.canary_percentage` to a dynamic feature flag system (like LaunchDarkly), engineers can dial the traffic up or down without deploying new code.

## Production Implications

Shadow mode and A/B testing complicate the data lifecycle. If you run Shadow Mode, you must ensure your observability platform clearly tags traces as `environment: shadow` so they don't skew your primary production metrics. 

Furthermore, A/B testing LLMs requires standardizing tool schemas. If Model A is OpenAI and Model B is Anthropic, the application must be capable of translating OpenAI's tool-call format into Anthropic's tool-call format seamlessly, so the underlying execution logic remains unchanged.

## Common Mistakes

- **Not hashing by user ID:** Splitting traffic per-request instead of per-user. A user asks a question and gets the Model A persona. They ask a follow-up and get the Model B persona. The jarring shift ruins the UX.
- **Ignoring prompt drift:** A/B testing a new model without tweaking the system prompt. Prompts are heavily coupled to models. Model B might fail not because it's worse, but because it needs a slightly different instruction style.
- **Testing on synthetic data only:** Passing a benchmark test and skipping shadow mode. Real users misspell words, use slang, and ask chaotic questions that synthetic benchmarks never cover.

## Interview Questions

**Q: Explain how a Shadow Mode deployment works and why it is particularly valuable for LLMs.**
**A:** In Shadow Mode, production traffic is sent to the new model asynchronously, but the results are logged rather than returned to the user. This is valuable for LLMs because their non-deterministic nature means benchmark tests often fail to predict real-world performance. Shadow mode provides a massive dataset of side-by-side comparisons on actual user edge-cases without risking the user experience.

**Q: When running a Canary deployment for a new LLM, what specific metrics would you configure to trigger an automatic rollback?**
**A:** I would configure automatic rollbacks if the Canary cohort shows a sustained spike in Tool Execution Errors (indicating the new model fails to format JSON correctly), a significant increase in p95 Time To First Token (indicating the new model is too slow), or an increase in the HTTP 429 rate (indicating we've hit API limits for the new model tier).

## Further Reading
- [LaunchDarkly: Feature Flags for AI](https://launchdarkly.com/) — Concepts for managing dynamic configuration and rollouts.
