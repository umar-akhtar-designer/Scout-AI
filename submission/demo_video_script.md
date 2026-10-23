# Demo Video Script — ScoutAI (2:55 max)

Submission requirement: **public YouTube video, 3 minutes or shorter**, showing the project working and how it uses **Nebius Token Factory** + **NVIDIA Nemotron**.

## Before recording

1. Start the app and confirm `/health` returns `{"status":"ok"}`.
2. Prep two files: a short PDF (e.g., an arXiv paper) and a screenshot with visible text.
3. Have a clean browser window at 1080p, sidebar visible, light or dark mode (pick one and stay consistent).
4. Pick **Nemotron Super** for the live run (fast enough for the video; Ultra also works).
5. Close other apps/notifications. Record at 30 fps, 1920×1080.
6. Keep the total under 3:00 — trim dead air while the pipeline runs.

---

## 0:00–0:15 — Hook

**On screen:** 8–10 browser tabs open, then cut to the ScoutAI landing page.

**Voiceover:**
"Research still means opening a dozen tabs, skimming sources, and hoping you did not miss the one claim that matters. ScoutAI does that work for you — with open models and verifiable citations."

---

## 0:15–0:30 — What it is

**On screen:** Cursor over the composer; hover the model picker; briefly show the paperclip and the sidebar.

**Voiceover:**
"ScoutAI is a multi-model research agent. You ask a question, it plans the research, searches the web, reads links and attachments, verifies claims, and streams back a report where every finding is cited."

---

## 0:30–1:20 — Live run (main demo)

**On screen:** Type:

```
Compare LoRA, QLoRA, and full fine-tuning for a 7B LLM on a single 24GB GPU. Cover VRAM, speed, quality trade-offs, and when to use each. Cite recent papers.
```

Then: attach the prepared PDF with the paperclip, paste `https://arxiv.org/abs/2305.14314` into the question, select **Nemotron Super**, and press Enter.

**Voiceover:**
"I will attach a paper and also paste a link, so ScoutAI reads both. Then I pick a model — Nano for speed, Super for balance, Ultra for the strongest report."

**On screen:** Progress steps appear one by one: **Plan → Search → Extract → Verify → Write**, each showing its model. Zoom slightly on "Reading linked pages".

**Voiceover:**
"First, Nemotron Nano decomposes the question into focused sub-queries. Tavily then searches the live web, while the link and the attached PDF are fetched and converted to text. Nano extracts the relevant facts in parallel. Super verifies each claim against the evidence and assigns confidence. Finally, the writer model assembles the report."

**On screen:** Report appears. Scroll slowly through Executive Summary, Key Findings, Confident/Uncertain, then the Citations list. Hover one citation URL.

**Voiceover:**
"Here is the result: a structured report, a confidence section that separates confirmed facts from uncertain ones, and numbered citations that map to real sources. Note that irrelevant claims are dropped instead of being padded into the answer."

---

## 1:20–1:40 — Attachments and links

**On screen:** Open the chat with the attached chip visible; briefly click the image attachment flow (or show the extracted text chip). Show the PDF chip.

**Voiceover:**
"Attachments are not just stored — they are read. PDFs and DOCX files are parsed locally on the server, links are fetched and cleaned, and images go through Nemotron 3.5 Super VL to extract visible text, tables, and chart descriptions. All of it becomes evidence for the same verification pipeline."

---

## 1:40–2:20 — How it is built (judging criteria)

**On screen:** Cut to `README.md` model table, then a terminal showing:
```
uvicorn scoutai.backend.app:app --port 8000
```
Then highlight `.env` **without showing key values**, and the pipeline modules in the editor (`planner.py`, `searcher.py`, `extractor.py`, `verifier.py`, `writer.py`).

**Voiceover:**
"Every model call goes through Nebius Token Factory's OpenAI-compatible endpoint — no other inference provider. Work is routed by cost and difficulty: Nemotron Nano for planning and extraction, Super for verification, Ultra for writing. The backend is FastAPI, the frontend streams progress with Server-Sent Events, Tavily provides search, and the whole app runs in Docker. There is no database: runs live in memory, and uploads are never written to disk."

**On screen:** Show `render.yaml` and the Dockerfile briefly.

**Voiceover:**
"The same Dockerfile deploys to Render with a one-click blueprint, so the demo runs on open infrastructure end to end."

---

## 2:20–2:45 — Why it matters

**On screen:** Return to the finished report; highlight the confidence section and a citation.

**Voiceover:**
"Students get literature reviews they can actually check. Journalists get faster fact-checking. Founders get market research with sources attached. The verification step is the point: ScoutAI shows what is supported, what is uncertain, and what it ignored."

---

## 2:45–2:55 — Close

**On screen:** ScoutAI logo, then text:
**Nebius x NVIDIA Global AI Hackathon — Best Apps and Agents**

**Voiceover:**
"Built with NVIDIA Nemotron models on Nebius Token Factory, with Tavily for search. Thanks for watching."

---

## YouTube upload checklist

- [ ] Public visibility (not unlisted/private)
- [ ] Title: `ScoutAI — Multi-model deep research with NVIDIA Nemotron on Nebius`
- [ ] Description: repo URL, live demo URL, and a one-line list of models used
- [ ] Duration ≤ 3:00
- [ ] 1080p, audio audible, no copyrighted music
- [ ] Show the app actually running (no mockups)
