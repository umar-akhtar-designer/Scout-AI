# Demo Video Script: ScoutAI (2:45)

## Timing Overview
- 0:00-0:20: Hook - problem demonstration
- 0:20-2:10: Live demo of real question
- 2:10-2:35: Code/model routing and Nebius+Nemotron+Tavily usage
- 2:35-2:45: Impact statement and close

---

### 0:00-0:20 | Hook: The Problem

**On screen:** Split screen showing someone frantically researching, with multiple browser tabs open.

**Voiceover:**
"Students, journalists, and founders spend hours every week verifying information. You open a dozen tabs, read through irrelevant content, and still wonder: 'Is this actually true?' Misinformation spreads unchecked, and there's no efficient way to get a trustworthy, cited research report."

**On screen:** Quick cut to the ScoutAI logo, then the UI landing page.

**Voiceover:**
"Meet ScoutAI. Ask any question, and we plan the research, search the live web, check claims, and deliver a cited report in about a minute."

---

### 0:20-1:00 | Live Demo 1: AI governance trends

**On screen:** User types "What are the latest trends in AI governance?" and clicks Research.

**Voiceover:**
"Let's start with: 'What are the latest trends in AI governance?'"

**On screen:** SSE progress tracker activates step by step:
- Step 1 (Plan): "Decomposing research question..." - Nemotron Nano model shown
- Step 2 (Search): "Web searching..." - Tavily icon shown
- Step 3 (Extract): "Fact extraction..." - Nemotron Nano shown
- Step 4 (Verify): "Claim verification..." - Nemotron Super model shown
- Step 5 (Write): "Report generation..." - Nemotron Ultra model shown

**Voiceover:**
"[Step 1] The question is decomposed into focused sub-queries using Nemotron Nano - the fastest, most cost-effective model. [Step 2] Tavily searches the web with advanced depth, returning authoritative sources. [Step 3] Nemotron Nano extracts key facts from each source in parallel. [Step 4] Nemotron Super cross-checks claims against multiple sources, assigning High, Medium, or Low confidence. [Step 5] Nemotron Ultra writes the final report with executive summary, key findings, and numbered citations."

**On screen:** Final report appears with:
- Executive summary paragraph
- Numbered key findings with citations [1], [2], [3]
- Confidence badges (High/Medium/Low) next to each claim
- Conflicts/uncertain section
- Clickable citations mapping to real URLs

**Voiceover:**
"The report appears in about 60 seconds. Every claim traces to a collected source. Conflicting information is flagged. And the user gets a trustworthy, citable report instead of 10 open tabs."

---

### 1:00-2:00 | Live Demo 2: EV battery comparison

**On screen:** User clicks a chip: "Compare electric vehicle battery technologies"

**Voiceover:**
"Here's another question: 'Compare electric vehicle battery technologies.' The pipeline reuses the same model routing - Nano for planning/extract, Super for verification, Ultra for writing - but with completely different search queries and sources."

**On screen:** Pipeline runs, sources appear, verification badges show, final report generates.

**Voiceover:**
"Notice how the verification step cross-checks claims across independent sources. A claim supported by 2+ sources gets a High confidence badge. A claim with only 1 source gets Medium. And if a claim has no supporting sources, it's flagged as Low - with a note in the uncertain section."

---

### 2:10-2:35 | Model Routing & Nebius+Nemotron+Tavily

**On screen:** Split screen - left side shows the UI with running pipeline, right side shows terminal output or config.

**Voiceover:**
"Behind the scenes, ScoutAI routes work to different Nemotron models by task to save cost and time. Nemotron Nano handles the fast, repetitive work of planning and fact extraction. Nemotron Super does the medium-complexity claim verification. And Nemotron Ultra generates the final report - the only step that needs the strongest model."

**On screen:** API endpoint and config shown.

**Voiceover:**
"All models are accessed through Nebius Token Factory's OpenAI-compatible API. This gives us a familiar Python openai SDK interface, fast inference, and cost efficiency. By not using the strongest model for every step, we reduce token costs by an estimated 60% compared to a single-model approach."

**On screen:** Tavily API usage shown.

**Voiceover:**
"Tavily provides the live web search - advanced search depth, source snippets, and deduplication. Without Tavily, ScoutAI would have no way to access current, verifiable information from the open web."

---

### 2:35-2:45 | Impact and Close

**On screen:** User smiling at the finished report, then the Nebius x NVIDIA hackathon logo.

**Voiceover:**
"ScoutAI turns hours of research into 60 seconds. For students, that means more time learning. For journalists, faster fact-checking. For founders, quicker market intelligence. And the verification step - showing confidence ratings and conflicts - means the report is actually trustworthy."

**On screen:** "Best Apps and Agents track - Nebius x NVIDIA Global AI Hackathon"

**Voiceover:**
"Built with NVIDIA Nemotron models, Nebius Token Factory, and Tavily. Thank you."
