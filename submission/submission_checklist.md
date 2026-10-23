# Submission Checklist: Nebius x NVIDIA Global AI Hackathon

Deadline: **30 Oct 2026, 10:00pm GMT+5** · Track: **Best Apps and Agents**

## Hard requirements

- [x] **Nebius Token Factory**: every model call uses `https://api.tokenfactory.nebius.com/v1/`
- [x] **NVIDIA open-source model**: Nemotron 3 Nano, Super, Ultra, and 3.5 Super VL
- [x] **Tavily**: live web search is core to every run (also eligible for Best Use of Tavily)
- [x] **Working project**: verified end-to-end locally (20–40s runs, real citations)
- [x] **Public code repository**: https://github.com/umar-akhtar-designer/Scout-AI
- [x] **Open-source license**: MIT, `LICENSE` at repo root, license badge in README
- [x] **README**: setup, env vars, usage, architecture, deployment
- [x] **Project description**: `submission/devpost_description.md`
- [x] **Feedback**: `submission/feedback.md`
- [x] **Pre-existing project note**: "What was significantly updated during the submission period" in the description
- [x] **Live demo URL**: https://evolve-late-vanish.ngrok-free.dev (temporary tunnel — see note below)
- [ ] **Demo video**: record from `submission/demo_video_script.md`, upload to YouTube (public, ≤ 3:00), add URL to Devpost
- [ ] **Submit the Devpost form** (project, track, demo URL, video URL, repo URL, description, feedback)
- [ ] **Keep the demo alive during judging** (or deploy permanently with `render.yaml`)

## Demo URL note

The current demo runs through an ngrok tunnel on the development machine:

- ngrok may show a one-time "You are about to visit" page — click **Visit Site**.
- The URL stops working if the machine sleeps, loses network, or the `ngrok` process stops.
- For a durable URL, deploy with `render.yaml` (Render → New → Blueprint) and replace the link on Devpost.

## Judging criteria — where to point judges

| Criterion | Evidence |
| --- | --- |
| Technological implementation | Token Factory for all inference; per-step model routing; reasoning toggles for JSON reliability; SSE pipeline; timeouts/fallbacks |
| Design | Complete chat product: streaming steps, citations, model picker, attachments, settings, dark mode, mobile layout |
| Potential impact | Students/journalists/founders get a cited answer instead of ten tabs; relevance filtering prevents confidently-wrong answers |
| Quality of the idea | Verification-first research agent: confidence tiers, conflict flags, explicit exclusion of inapplicable claims, evidence from links and uploads |

## Repository structure

- [x] `scoutai/backend/`: FastAPI app, pipeline, planner, searcher, extractor, verifier, writer, prompts, config
- [x] `scoutai/frontend/`: HTML template + CSS/JS + favicon
- [x] `.env.example`: all required variables with real model IDs
- [x] `Dockerfile`: portable image, honors `$PORT`
- [x] `render.yaml`: one-click Render blueprint
- [x] `requirements.txt`: pinned to tested versions
- [x] `LICENSE` (MIT) and `.gitignore`
- [x] `submission/`: description, video script, feedback, this checklist

## Final pass before submitting

- [ ] Run one fresh question in the browser at the public URL
- [ ] Confirm citations open real pages
- [ ] Confirm an attached PDF and an image both return text
- [ ] Confirm the video shows the app actually running and mentions Nebius Token Factory + Nemotron
- [ ] Confirm the repo is public and the license is visible at the top
- [ ] Confirm no `.env` or API keys were committed (`git log --all -- .env` is empty)
