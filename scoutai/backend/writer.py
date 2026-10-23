from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

import openai

from scoutai.backend.config import NEBIUS_BASE_URL, NEBIUS_API_KEY
from scoutai.backend.prompts import WRITE_PROMPT

logger = logging.getLogger(__name__)


def _call_model(model_name: str, prompt: str, disable_thinking: bool = False) -> str:
    try:
        client = openai.OpenAI(base_url=NEBIUS_BASE_URL, api_key=NEBIUS_API_KEY, timeout=90.0, max_retries=0)
        kwargs = {}
        if disable_thinking:
            kwargs["extra_body"] = {"chat_template_kwargs": {"enable_thinking": False}}
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4096,
            **kwargs,
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


def _clean_report(text: str) -> str:
    text = re.sub(r"(?m)^(\s*(?:[-*]\s*|\d+\.\s*)?)Note:\s*", r"\1", text)
    text = re.sub(r"(?m)^(\s*(?:[-*]\s*|\d+\.\s*)?)Claim\s+\d+:\s*", r"\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _fallback_report(
    question: str,
    executive_summary: str,
    key_findings: List[str],
    citations: List[dict],
) -> str:
    findings = "\n".join(f"{i + 1}. {f}" for i, f in enumerate(key_findings)) or "No findings available."
    cites = "\n".join(
        f"[{c.get('ordinal', i + 1)}] URL: {c.get('url', '')}" for i, c in enumerate(citations)
    ) or "[1] URL: unavailable"
    return (
        f"EXECUTIVE SUMMARY:\n{executive_summary}\n\n"
        f"KEY FINDINGS:\n{findings}\n\n"
        "CONFIDENT OR UNCERTAIN INFO:\n"
        "- Confirmed: Findings above are drawn from the collected sources.\n\n"
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
        logger.warning("Writer returned empty content; retrying without extended thinking")
        raw = _strip_code_fence(_call_model(model, prompt, disable_thinking=True))
    if not raw:
        logger.warning("Writer model returned empty output; using fallback report")
        raw = _fallback_report(question, executive_summary, key_findings, citations)
    else:
        raw = _clean_report(raw)
        if "CITATIONS:" not in raw:
            raw = raw.rstrip() + "\n\nCITATIONS:\n" + cites_text

    return {"report": raw, "citations": citations, "model": model}
