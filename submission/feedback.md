# Feedback on Nebius Token Factory, Nemotron Models, and Tavily

## Nebius Token Factory

### What worked well

- OpenAI-compatible API interface was intuitive and required minimal learning curve
- The `https://api.tokenfactory.nebius.com/v1/` endpoint was reliably accessible throughout development
- API key management was straightforward; no complex authentication flow required
- Response times were consistent for Nemotron Nano and Super models
- Documentation was clear about base URL format and request structure

### What was confusing

- Initial setup lacked clear examples of model naming conventions specific to Token Factory
- Rate limit headers weren't immediately obvious; took some trial and error to understand retry behavior
- Some Python SDK version mismatches caused import issues (solved by pinning openai==1.35.0)

### Suggestions

- Add a "model gallery" or auto-discovery feature that lists available Nemotron models for a given account
- Provide sample notebooks for common patterns (SSE streaming, parallel calls, error handling)
- Include rate limit information directly in API response headers with clearer documentation

## Nemotron Models (Nano / Super / Ultra)

### What worked well

- Nano was extremely fast and cost-effective for planning and extraction tasks; response latency under 500ms
- Super hit the sweet spot for claim verification - good reasoning capability without the cost of Ultra
- Ultra generated high-quality report prose with correct citation formatting on the first try
- Model switching via environment variables was seamless; no code changes needed
- All three models followed the same OpenAI chat completions interface

### What was confusing

- Model naming inconsistency between Token Factory UI and the environment variable names (had to check documentation to confirm `nemotron-nano` vs other variants)
- Token usage varied significantly between models for the same prompt size; needed to calibrate expectations

### Suggestions

- Standardize model environment variable names across all NVIDIA services
- Provide token usage estimates per model for common prompts
- Add a "model selector" endpoint that recommends the optimal model size for a given task type

## Tavily

### What worked well

- `search_depth="advanced"` returned significantly more relevant results for complex research questions compared to basic depth
- `include_raw_content=True` provided useful snippets for the extraction step without needing to parse HTML
- Parallel query execution worked well; multiple searches ran concurrently without errors
- Source deduplication by URL prevented redundant processing of the same article

### What was confusing

- The distinction between `include_answer`, `include_raw_content`, and `include_extracted_content` was not always clear from the documentation; needed to test each flag
- Max_results parameter interaction with search_depth required some experimentation to optimize for cost vs. completeness

### Suggestions

- Add a "search preview" mode that shows top results before committing to a full search
- Provide more detailed flag documentation with use-case-specific recommendations
- Add optional entity extraction or key phrase identification in search results
