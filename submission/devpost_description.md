# DevPost Description: ScoutAI

**Track:** Best Apps and Agents

**Live demo:** https://evolve-late-vanish.ngrok-free.dev (if ngrok shows a warning page, click **Visit Site**)

**Code:** https://github.com/umar-akhtar-designer/Scout-AI

**Video:** <!-- VIDEO_URL -->

---

## Inspiration

Research is slow in a way that is hard to notice. Students, journalists, and founders open dozens of tabs, skim pages that turn out to be irrelevant, and still cannot say which claims are actually supported. Search engines return links; they do not return a trustworthy answer. We wanted an agent that does the whole loop — plan, search, read, verify, write — and shows its evidence instead of hiding it.

## What it does

ScoutAI is a multi-model deep research agent. You ask a question, and it:

1. **Plans** the research, splitting the question into 3–5 focused sub-queries.
2. **Searches** the live web with Tavily and deduplicates sources.
3. **Reads** links pasted in the question (HTML and PDF) plus attached PDF/DOCX/text files and images.
4. **Extracts** relevant facts from each source in parallel.
5. **Verifies** claims across sources, assigns High/Medium/Low confidence, flags conflicts, and drops claims that do not apply to the user's situation.
6. **Writes** a report with an executive summary, key findings, a confirmed/uncertain section, and numbered citations.

Progress streams into the UI step by step, so the user sees which model is working and what it is doing. Runs typically finish in 20–40 seconds.

## How we built it

### Architecture

A FastAPI backend orchestrates five steps:

- **Plan** (Nemotron 3 Nano): strict JSON with sub-questions and search queries.
- **Search** (Tavily): parallel queries, deduplication, basic search depth.
- **Extract** (Nemotron 3 Nano): parallel fact extraction per source, capped concurrency.
- **Verify** (Nemotron 3 Super): support counts, confidence ratings, conflict flags, relevance filtering.
- **Write** (Nemotron 3 Ultra): final report with citations.

The frontend is vanilla HTML/CSS/JS and consumes Server-Sent Events for live progress and the final payload.

### Model routing

| Step | Model | Why |
| --- | --- | --- |
| Plan | Nemotron 3 Nano 30B-A3B | Fast, cheap decomposition |
| Extract | Nemotron 3 Nano 30B-A3B | High-volume short factual calls |
| Verify | Nemotron 3 Super 120B-A12B | Reasoning across multiple sources |
| Write | Nemotron 3 Ultra 550B-A55B | Best synthesis and citation quality |
| Images | Nemotron 3.5 Super VL | OCR + visual description |

All calls use Nebius Token Factory's OpenAI-compatible API (`https://api.tokenfactory.nebius.com/v1/`). No other inference provider is used.

### Key technical decisions

- **Thinking control:** Nemotron 3 reasoning is disabled for JSON-heavy steps (`chat_template_kwargs.enable_thinking = False`), which prevents empty JSON responses and cuts latency/cost. The writer keeps reasoning enabled, with a no-thinking retry as a fallback.
- **Per-step timeouts:** each model call and each search/extract operation has a hard timeout, so one dead source cannot stall a run.
- **Strict JSON + fallbacks:** planners and extractors validate JSON shape; failures degrade gracefully instead of crashing.
- **SSE progress:** the pipeline publishes a progress object (`step`, `status`, `model`, description) that the API streams to the browser.
- **In-memory runs:** no database, no disk writes for uploads. Runs disappear when the process restarts.
- **Source quality:** the planner targets official program pages, `.edu/.gov`, arXiv, and peer-reviewed sources; the verifier drops claims that do not fit the user's stated situation.

## Challenges

- **Reasoning models vs. structured output.** Nemotron 3 sometimes spent its whole token budget on reasoning and returned empty content, which broke JSON parsing. Disabling thinking for plan/extract/verify fixed both reliability and latency.
- **Citation integrity.** It is easy for a writer to invent a plausible URL. We pass exact ordinals and URLs into the prompt, forbid new sources, and force the citations block if the model omits it.
- **Source relevance.** Early runs confidently answered adjacent questions (e.g., postdoc-only programs for a recent graduate). We added relevance rules to the verifier and writer, and made the planner target authoritative pages.
- **Streaming vs. serverless limits.** A 30-second pipeline does not fit comfortably in short serverless request windows, so the demo is containerized and deployable on Render; the SSE handler polls the run state and emits progress instead of buffering.
- **Uploads without persistence.** PDFs, DOCX, HTML, and images are parsed in memory on the server; images use a vision model. Nothing is written to disk.

## Accomplishments

- End-to-end pipeline that produces a real cited report from a live question in ~20–40 seconds.
- Verification that is visible to the user: confidence tiers, conflicts, and explicit exclusions.
- Link, PDF, DOCX, and image reading integrated into the same evidence pipeline.
- Model routing that keeps costs low by reserving Ultra for the final report.
- A complete product surface: streaming UI, model picker, settings, profile, dark mode, graceful demo fallback.
- Runs entirely on open infrastructure through Nebius Token Factory.

## What we learned

- Small models are excellent at decomposition and extraction when the output schema is strict.
- Reasoning needs to be a per-step decision, not a global default.
- Verification quality depends more on source selection than on model size.
- A visible progress state makes a 30-second wait feel intentional rather than broken.

## What's next

- Cache search results and extracted evidence for repeated questions.
- Add a "compare sources" view for conflicting claims.
- Export reports to Markdown/PDF with citation metadata.
- Add per-run token and cost estimates.
- Persistent research folders (opt-in) with a real database.

## Built with

Python · FastAPI · Uvicorn · Pydantic · OpenAI Python SDK · NVIDIA Nemotron 3 Nano / Super / Ultra · NVIDIA Nemotron 3.5 Super VL · Nebius Token Factory · Tavily · BeautifulSoup · pypdf · python-docx · HTML/CSS/JavaScript · Server-Sent Events · Docker

## What was significantly updated during the submission period

The repository existed before the submission period as an early prototype. During the submission period we rebuilt the pipeline orchestration and reliability (thinking control, timeouts, JSON validation), added link reading, PDF/DOCX/image extraction, model selection, SSE progress, the settings/profile UI, dark mode, and the redesigned responsive interface. The README, Dockerfile, and deployment blueprint were also added for judges to run the project.
