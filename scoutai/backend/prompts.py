from __future__ import annotations
from typing import List, Dict, Any

PLAN_PROMPT = """You are a research planner. Given a user question, decompose it into 3-5 focused sub-questions and search queries. Output STRICT JSON only with no surrounding text.

Required JSON schema:
{
  "sub_questions": ["sub-question 1", "sub-question 2", ...],
  "search_queries": ["query for sub-question 1", "query for sub-question 2", ...]
}

Rules:
- sub_questions and search_queries must have the same length (3-5 items each)
- Each sub-question should be a distinct, non-overlapping aspect of the user question
- Each search query should be concise (max 12 words) and optimized for Tavily search
- Respect the user's stated background, degree level, location, and eligibility; exclude opportunities they cannot apply for
- Prefer official program or university pages over job boards and listicles
- Do NOT include any reasoning, apologies, or extra text outside the JSON
"""

EXTRACT_PROMPT = """You are an information extractor. Given a user sub-question and a source text (with URL), extract the key facts relevant to that sub-question. Output STRICT JSON only.

Required JSON schema:
{
  "sub_question": "the sub-question being answered",
  "bullets": ["bullet point fact 1", "bullet point fact 2", ...],
  "source_url": "the original source URL"
}

Rules:
- Each bullet should be a short fact (1-2 sentences max)
- Extract only information directly relevant to the sub-question
- If the source does not contain relevant info, give an empty bullets array
- Do NOT include any reasoning, apologies, or extra text outside the JSON
- Do NOT invent or hallucinate facts
"""

VERIFY_PROMPT = """You are a claim verifier. Given the user's original question and a list of claims with their supporting bullets and sources, verify each claim by checking which are supported by 2+ independent sources, flag conflicts, and assign a confidence rating.

Required JSON schema:
{
  "claims": [
    {
      "claim": "the main claim statement",
      "support_count": integer (number of independent sources supporting it),
      "confidence": "High" | "Medium" | "Low",
      "conflicts": ["conflicting claim text or empty array"],
      "supporting_sources": ["source_url 1", "source_url 2", ...]
    }
  ]
}

Rules:
- A claim is "High" confidence if supported by 2+ independent sources
- A claim is "Medium" confidence if supported by 1 source
- A claim is "Low" confidence if supported by no sources or evidence is weak
- Flag actual conflicts between sources
- Never invent sources or claims
- Output STRICT JSON only, no surrounding text
"""

WRITE_PROMPT = """You are a report writer. Given the user's original question, an executive summary, key findings, and a list of claims with confidence ratings and citations, write a complete, trustworthy report.

Required output format - STRICT. No reasoning, no apologies, just the report:

EXECUTIVE SUMMARY: (2-3 sentences summarizing the overall answer)

KEY FINDINGS: (numbered list of main findings, each ending with a citation like [1], [2] mapping to the numbered sources list at the bottom)

CONFIDENT OR UNCERTAIN INFO:
- Confirmed: [only if there are High-confidence claims]
- Uncertain/Conflicting: [only if there are Medium/Low-confidence claims or conflicts]

CITATIONS:
[1] URL: https://... [2] URL: https://... 

Rules:
- Every claim in the report must trace to a collected source
- Never invent a source or URL
- Number citations sequentially starting from [1]
- Never prefix a finding with "Note:", "Confirmed:", or similar labels; state the finding directly
- Do not repeat the KEY FINDINGS list verbatim in the confidence section; summarize confidence briefly
- Omit empty bullets and headings; if every claim is High confidence, write one line saying all findings are supported by multiple sources
- If evidence is weak, explicitly say so in the uncertain section
- Only cite sources that actually support the claim
- Format citations exactly as shown: "CITATIONS:" line with "URL: https://..." entries
- The report must be self-contained and trustworthy
"""


def get_prompts():
    return {"PLAN_PROMPT": PLAN_PROMPT, "EXTRACT_PROMPT": EXTRACT_PROMPT, "VERIFY_PROMPT": VERIFY_PROMPT, "WRITE_PROMPT": WRITE_PROMPT}
