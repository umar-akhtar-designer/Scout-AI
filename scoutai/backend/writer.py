from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

import openai

from scoutai.backend.config import NEBIUS_BASE_URL, NEBIUS_API_KEY
from scoutai.backend.prompts import WRITE_PROMPT

logger = logging.getLogger(__name__)


def _call_model(model_name: str, prompt: str) -> str:
    try:
        client = openai.OpenAI(base_url=NEBIUS_BASE_URL, api_key=NEBIUS_API_KEY, timeout=90.0, max_retries=0)
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4096,
        )
        message = completion.choices[0].message
        return (message.content or "").strip()
    except Exception as e:
        logger.warning(f"Model call failed for {model_name}: {e}")
        return ""


def _strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def _fallback_report(
    question: str,
    executive_summary: str,
    key_findings: List[str],
    citations: List[dict],
    claims: Optional[List[dict]] = None,
) -> str:
    findings = "\n".join(f"{i + 1}. {f}" for i, f in enumerate(key_findings)) or "No findings available."
    cites = "\n".join(
        f"[{c.get('ordinal', i + 1)}] URL: {c.get('url', '')}" for i, c in enumerate(citations)
    ) or "[1] URL: unavailable"
    high = [c for c in (claims or []) if c.get("confidence") == "High"]
    uncertain = [c for c in (claims or []) if c.get("confidence") in ("Medium", "Low")]
    confidence = ""
    if high:
        confidence += f"- Confirmed: {len(high)} findings are supported by multiple sources.\n"
    if uncertain:
        confidence += f"- Uncertain: {len(uncertain)} findings rely on limited evidence.\n"
    if not confidence:
        confidence = "- All findings above are drawn from the collected sources.\n"
    return (
        f"EXECUTIVE SUMMARY:\n{executive_summary}\n\n"
        f"KEY FINDINGS:\n{findings}\n\n"
        f"CONFIDENT OR UNCERTAIN INFO:\n{confidence}\n"
        f"CITATIONS:\n{cites}\n"
    )


def write_report(
    question: str,
    executive_summary: str,
    key_findings: List[str],
    claims: List[dict],
    citations: List[dict],
    model_name: Optional[str] = None,
) -> Dict[str, Any]:
    model = model_name or "nemotron-ultra"

    findings_text = "\n".join(f"- {f}" for f in key_findings) or "- No findings available."
    cites_text = "\n".join(
        f"[{c.get('ordinal', i + 1)}] URL: {c.get('url', '')}" for i, c in enumerate(citations)
    ) or "[1] URL: unavailable"
    try:
        claims_text = json.dumps(claims, indent=2, ensure_ascii=False)[:6000]
    except Exception:
        claims_text = str(claims)[:6000]

    prompt = WRITE_PROMPT
    prompt += (
        f'\n\nOriginal question: "{question}"'
        f"\n\nExecutive summary:\n{executive_summary}"
        f"\n\nKey findings:\n{findings_text}"
        f"\n\nVerified claims (JSON):\n{claims_text}"
        f"\n\nCitations (use these exact URLs and ordinals):\n{cites_text}"
        "\n\nWrite the final report now, following the required format exactly."
    )

    raw = _strip_code_fence(_call_model(model, prompt))
    if not raw:
        logger.warning("Writer model returned empty output; using fallback report")
        raw = _fallback_report(question, executive_summary, key_findings, citations, claims)

    return {"report": raw, "citations": citations, "model": model}
