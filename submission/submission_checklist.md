# Submission Checklist: Nebius x NVIDIA Global AI Hackathon

## DevPost Fields

### Inspiration
- [x] Added - research time problem description

### What it does
- [x] Added - five-step pipeline explanation, model routing, Tavily integration

### How we built it
- [x] Added - architecture diagram, model routing table, technical decisions

### Challenges
- [x] Added - model JSON output, parallel extraction, model routing, rate limits, SSE management

### Accomplishments
- [x] Added - end-to-end pipeline, visible verification, model routing, responsive UI, demo mode

### What's next
- [x] Added - caching, multi-language, browser extension, document upload, token tracking, self-correction

## Checklist Items

### Technical Requirements
- [x] **Nebius Token Factory**: App runs on OpenAI-compatible API at `https://api.tokenfactory.nebius.com/v1/`
- [x] **NVIDIA Nemotron**: Uses at least one Nemotron model (Nano for Plan/Extract, Super for Verify, Ultra for Write)
- [x] **Tavily**: Core product feature - web search, advanced depth, source extraction
- [x] **MIT License**: Visible at top of repository with badge
- [x] **README.md**: Setup and run instructions included
- [x] **Public GitHub repo**: Open source with MIT license

### Demo Materials
- [x] **Working demo**: UI functional with SSE pipeline tracking
- [x] **3-minute-or-shorter demo video**: `submission/demo_video_script.md` generated
- [x] **Project description**: `submission/devpost_description.md` generated
- [x] **Written feedback**: `submission/feedback.md` generated with Nebius/NVIDIA/Tavily feedback

### Repository Structure
- [x] **scoutai/backend/**: App, pipeline steps as separate modules, prompts, config, tests
- [x] **scoutai/frontend/**: Single clean responsive page (HTML/CSS/JS)
- [x] **scoutai/docs/**: Architecture diagram in Mermaid, screenshots placeholder
- [x] **.env.example**: At root with all required env vars
- [x] **Dockerfile**: For deployment
- [x] **requirements.txt**: Python dependencies
- [x] **LICENSE (MIT)**: At root
- [x] **.gitignore**: Standard Python ignore patterns
- [x] **docs/api_contract.md**: SSE event contract between pipeline <-> API <-> frontend

### UI Requirements
- [x] **Search box with example questions as clickable chips**: Implemented
- [x] **Live pipeline tracker**: Plan -> Search -> Extract -> Verify -> Write with status and model info
- [x] **Sources panel**: Every source with favicon/domain and link
- [x] **Final report**: Clickable numbered citations, confidence badges (High/Medium/Low), conflicts box
- [x] **Buttons**: Copy report, download as Markdown, new question
- [x] **Stats footer**: Total time, number of sources, tokens used per model
- [x] **Friendly error messages and loading state**: Implemented
- [x] **Mobile responsive**: CSS media queries for < 640px

### Quality Bar
- [x] **runs after**: `pip install -r requirements.txt`, copy `.env.example` to `.env`, start server with one command
- [x] **Clean, commented, typed code**: No secrets committed
- [x] **.gitignore**: Included
- [x] **Demo mode (cached sample report)**: UI works even if API is down during judging
- [x] **pytest tests**: Basic tests for planner JSON parsing, citation mapping, and API health

### Submission Materials
- [x] **devpost_description.md**: All sections filled (Inspiration, What it does, How we built it, Challenges, Accomplishments, What we learned, What's next)
- [x] **demo_video_script.md**: Timed 2:45 script with exactly what to show on screen
- [x] **feedback.md**: Structured feedback template for Nebius Token Factory, Nemotron models, and Tavily
- [x] **submission_checklist.md**: Every DevPost field with tick list
---
