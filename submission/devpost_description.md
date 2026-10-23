# DevPost Description: ScoutAI

## Inspiration

Students, journalists, and founders spend hours every week verifying information, opening dozens of tabs, reading through irrelevant content, and cross-checking claims. Misinformation spreads quickly, and there's no efficient way to get a trustworthy, cited research report. We wanted to build a tool that automates the entire deep research process - from planning to verification - using the best open source models available.

## What it does

ScoutAI is a multi-model deep research agent that takes any user question and:

1. **Plans** the research by decomposing the question into 3-5 focused sub-queries using Nemotron Nano
2. **Searches** the live web using Tavily's advanced search, collecting sources with URLs, titles, and snippets
3. **Extracts** key facts from each source, running sources in parallel for speed using Nemotron Nano
4. **Verifies** claims by cross-checking against multiple sources, assigning High/Medium/Low confidence ratings, and flagging conflicts using Nemotron Super
5. **Writes** a complete, trustworthy report with executive summary, key findings, citations, and a "conflicting/uncertain" section using Nemotron Ultra

The output is a cited, trustworthy report in about a minute, with a visible verification step showing which claims are supported by 2+ independent sources and which have low confidence.

## How we built it

### Architecture

ScoutAI uses a five-step pipeline orchestrated by a FastAPI backend:

- **PLAN** (Nemotron Nano): Converts user questions into strict JSON with sub-questions and search queries
- **SEARCH** (Tavily): Advanced web search with deduplication and parallel query execution
- **EXTRACT** (Nemotron Nano): Parallel fact extraction from all sources per sub-question
- **VERIFY** (Nemotron Super): Claim verification with confidence ratings and conflict detection
- **WRITE** (Nemotron Ultra): Final report generation with proper citation formatting

All Nemotron models are accessed via the Nebius Token Factory OpenAI-compatible API. The frontend uses SSE (Server-Sent Events) to stream live progress for each pipeline step.

### Model routing strategy

- **Nano** for Plan and Extract: Fast, low-cost model suitable for decomposition and sentence-level fact extraction
- **Super** for Verify: Mid-tier model with good reasoning for claim verification against multiple sources
- **Ultra** for Write: Strongest model for generating high-quality, trustworthy reports with correct citations

### Key technical decisions

- Strict JSON output from the planner to ensure predictable pipeline parsing
- Asyncio parallelism for source extraction to minimize latency
- Graceful failure handling with retry logic and fallback demo mode
- SSE streaming for live UI progress tracking
- Demo mode with cached sample report so the product is never broken, even during API downtime

## Challenges

- Getting strict JSON output from Nemotron models via the Nebius API required careful prompt engineering and post-processing
- Parallel source extraction with asyncio required careful error handling to prevent one dead source from blocking the entire pipeline
- Model routing decisions (which model size for which step) needed extensive testing to balance cost, speed, and report quality
- Tavily API rate limits required implementing query batching and deduplication logic
- SSE connection management and reconnection logic for reliable live progress tracking

## Accomplishments

- End-to-end pipeline that actually works: from user question to cited report in ~60 seconds
- Visible verification step with confidence ratings - the core differentiator that sets ScoutAI apart from other research agents
- Model routing that saves cost by using Nano for simple tasks and Ultra only for final report generation
- Clean, responsive UI that works on mobile and desktop
- Demo mode that ensures the product is never broken, even during API downtime
- Clean codebase with typed models, prompts in dedicated files, and full test coverage

## What's next

- Add caching for previously searched questions and sources
- Support multi-language research queries
- Build browser extension for on-page research
- Integrate document upload for cite-while-you-write workflow
- Add more granular token usage tracking per model
- Implement self-correction loop for claims that fail verification
