# Feedback on Nebius Token Factory, NVIDIA Nemotron, and Tavily

## Nebius Token Factory

### What worked well

- The OpenAI-compatible API made migration to the `openai` Python SDK (2.x) straightforward: only `base_url` and `api_key` changed.
- The endpoint was stable during development; no authentication or networking issues.
- Model availability in one place made A/B testing across Nano, Super, and Ultra trivial.
- Error responses were fast and readable, which made timeout handling easier.

### What was confusing

- Reasoning output is returned separately from `content`, and some models can spend the entire `max_tokens` budget on reasoning and return empty `content`. This is easy to miss and looks like a silent failure.
- There is no obvious, documented way to discover which toggle disables thinking per model. We ended up using `chat_template_kwargs: {"enable_thinking": false}` after trial and error.
- Model naming differs between marketing pages, the catalog, and the API (`nemotron-nano` vs `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`), which caused early configuration mistakes.

### Suggestions

- Document reasoning controls (`enable_thinking`, thinking budgets) alongside each model, with an example of a JSON-only workload.
- Return a clear warning when a response finishes with empty `content` because the reasoning budget was exhausted.
- Add a `/models` response that includes capabilities (reasoning, vision, tool calling) and the exact model ID.
- Provide one minimal notebook showing parallel requests, timeouts, and streaming.

## NVIDIA Nemotron Models (Nano / Super / Ultra / Super VL)

### What worked well

- **Nano 30B-A3B** was excellent for planning and extraction when thinking was disabled: fast, cheap, and reliable at strict JSON.
- **Super 120B-A12B** handled multi-source claim verification well and was noticeably better than Nano at judging relevance.
- **Ultra 550B-A55B** produced the best final reports: correct citation formatting, clean structure, and sensible prioritization.
- **Nemotron 3.5 Super VL** read screenshots, tables, and chart labels accurately enough for research context.
- All models share the same chat-completions interface, so routing is a one-line change.

### What was confusing

- Reasoning behavior is inconsistent across prompts: the same JSON prompt sometimes returned valid JSON and sometimes only reasoning.
- Output limits interact with reasoning in ways that are hard to predict; a 700-token limit is not enough headroom for a JSON task if thinking is on.
- Model sizes and active-parameter counts are easy to confuse when choosing a default.

### Suggestions

- Publish recommended `max_tokens` and thinking settings per task type (JSON extraction, verification, long-form writing).
- Make `enable_thinking` a first-class parameter in the OpenAI-compatible schema rather than a chat-template kwarg.
- Document vision input limits (resolution, file size, supported formats) for the VL model.

## Tavily

### What worked well

- Search results were relevant and returned clean `url`, `title`, and `content` fields.
- Parallel query execution worked without rate-limit problems at our volume (3–5 queries per run).
- URL deduplication is simple because results are stable and well-formed.

### What was confusing

- The difference between `include_answer`, `include_raw_content`, and extracted content is not obvious from the docs, and the cost/latency trade-offs are not stated.
- `search_depth` has a large effect on latency and result quality; "advanced" is better for hard questions but slower than we wanted for a 30-second pipeline.
- There is no built-in source-quality signal, so we had to add our own rules to avoid blogs and job boards.

### Suggestions

- Add a quality or authority score per result (official domains, `.edu/.gov`, arXiv) that callers can filter on.
- Document expected latency and credit cost for each `search_depth` value.
- Provide a "fetch and extract" endpoint so callers do not need a separate HTML parser for the top results.

## Overall

Nebius Token Factory plus Nemotron is a strong combination for an agent that must run several different model sizes in one request. The main friction was reasoning-control and model naming, both of which are documentation problems rather than infrastructure problems. Tavily remains the simplest way to add live web evidence, and its result shape is easy to feed into a verification step.
