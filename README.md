# ScoutAI

Multi-model deep research agent built for the **Best Apps and Agents** hackathon. Ask a question, and ScoutAI plans the research, searches the web, reads sources and links, verifies claims, and streams back a cited report.

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi&logoColor=white)
![NVIDIA Nemotron](https://img.shields.io/badge/NVIDIA-Nemotron-76B900?logo=nvidia&logoColor=white)

## Features

- **Plan → Search → Extract → Verify → Write** pipeline with live progress over SSE
- **Three Nemotron models** via Nebius Token Factory (Nano / Super / Ultra)
- **Tavily web search** with source deduplication
- **Reads links** pasted in the question (HTML and PDF)
- **Reads attachments**: PDF, DOCX, TXT/MD/CSV, and images (vision model)
- **Citations** for every report, with claim-level verification
- **Chat-style UI** with dark mode, model picker, profile/settings, and conversation cache

## How it works

```
question ──▶ Planner ──▶ Tavily search ──▶ Extractor ──▶ Verifier ──▶ Writer ──▶ report
                 │              │                │             │
                 └── seed links ┘          page text       claim support
```

1. **Plan** — the fast model breaks the question into sub-queries.
2. **Search** — Tavily returns results; URLs in the question are fetched directly and prepended as sources.
3. **Extract** — relevant passages are pulled from each source (in parallel, capped concurrency).
4. **Verify** — the mid model checks claims against the extracted evidence and counts supporting sources.
5. **Write** — the selected model produces the final report + numbered citations.

## Tech stack

| Layer | Technology |
| --- | --- |
| Backend | FastAPI, Uvicorn, Pydantic |
| Models | NVIDIA Nemotron via Nebius Token Factory (OpenAI-compatible API) |
| Search | Tavily |
| Page reading | `requests` + BeautifulSoup, `pypdf` |
| Documents | `python-docx`, `pypdf`, vision model for images |
| Frontend | Vanilla HTML/CSS/JS, Server-Sent Events |

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # add your Nebius + Tavily keys
uvicorn scoutai.backend.app:app --host 0.0.0.0 --port 8000
```

Open <http://localhost:8000>.

### Environment variables

| Variable | Description |
| --- | --- |
| `NEBIUS_API_KEY` | Nebius Token Factory API key |
| `NEBIUS_BASE_URL` | `https://api.tokenfactory.nebius.com/v1/` |
| `MODEL_FAST` | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` |
| `MODEL_MID` | `nvidia/nemotron-3-super-120b-a12b` |
| `MODEL_STRONG` | `nvidia/Nemotron-3-Ultra-550b-a55b` |
| `TAVILY_API_KEY` | Tavily search API key |

## Usage

1. Type a research question and press **Enter**.
2. Pick a model in the top bar (Nano = fastest, Ultra = strongest).
3. Optionally attach a PDF/DOCX/text file or image with the paperclip.
4. Paste a URL in the question to force ScoutAI to read that page.
5. Watch the steps stream in; the final report includes numbered citations.

Example prompts:

- *Compare LoRA, QLoRA, and full fine-tuning for adapting a 7B LLM on a single 24GB GPU, including memory, speed, and quality trade-offs.*
- *Summarize https://arxiv.org/abs/2305.14314 and explain why QLoRA makes 65B fine-tuning feasible on one 48GB GPU.*

## Data handling

ScoutAI has **no database**. A run lives in server memory and is discarded when the process restarts. Uploaded files are processed in memory and never written to disk. The browser stores only your name/avatar, theme, model, and current chat in `localStorage`; **Log out** clears them. API keys live in `.env` and are never sent to the browser.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `GET` | `/api/status` | Demo mode, missing keys, model list |
| `POST` | `/api/run` | Start a run (`{question, model?}`) |
| `GET` | `/api/run/{id}` | Run summary |
| `GET` | `/sse/{id}` | Progress + final report stream |
| `POST` | `/api/extract-file` | Extract text from PDF/DOCX/image |
| `POST` | `/api/demo` | Cached demo report |

## Project structure

```
scoutai/
  backend/
    app.py        FastAPI routes, SSE, file extraction
    pipeline.py   Orchestration + progress events
    planner.py    Query decomposition
    searcher.py   Tavily search + URL fetching
    extractor.py  Evidence extraction
    verifier.py   Claim verification
    writer.py     Final report
    config.py     Environment + model config
  frontend/
    templates/index.html
    static/app.js, style.css, favicon.svg
submission/       DevPost description, demo script, checklist
```

## Docker

```bash
docker build -t scoutai .
docker run --env-file .env -p 8000:8000 scoutai
```

## License

MIT — see [LICENSE](LICENSE).
