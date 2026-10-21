from __future__ import annotations

import json
import logging
from typing import Any, List

import openai
from typing_extensions import override

from scoutai.backend.config import NEBIUS_BASE_URL, NEBIUS_API_KEY, AVAILABLE_MODELS
from scoutai.backend.prompts import WRITE_PROMPT

logger = logging.getLogger(__name__)


client = openai.OpenAI(
    base_url=NEBIUS_BASE_URL,
    api_key=NEBIUS_API_KEY,
)


def _call_model(model_name: str, prompt: str) -> str:
    """Call a Nemotron model via Nebius API."""
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        return completion.choices[0].message.content or ""
    except Exception as e:
        logger.warning(f"Write model call failed for {model_name}: {e}")
        return ""


def _extract_citations_from_write(report_text: str) -> List[dict]:
    """Extract citation URL entries from the write output."""
    citations = []
    # Look for "CITATIONS:" section
    citations_marker = "CITATIONS:"
    idx = report_text.find(citations_marker)
    if idx >= 0:
        section = report_text[idx + len(citations_marker):].strip()
        # Parse "URL: https://..." lines
        for line in section.split("\n"):
            line = line.strip()
            if line.upper().startswith("URL:"):
                url = line.split(":", 1)[1].strip()
                if url.startswith("http"):
                    citations.append({"ordinal": len(citations) + 1, "url": url})
    return citations


def write_report(
    question: str,
    executive_summary: str,
    key_findings: List[str],
    claims: List[dict],
    citations: List[dict],
    model_name: str = None,
) -> dict:
    """Write the final report using Nemotron Ultra model."""
    model = model_name or AVAILABLE_MODELS.get("strong", "nemotron-ultra")
    
    # Build claims summary for the prompt
    claims_summary = "\n".join([
        f"- {c.get('claim', '')} (confidence: {c.get('confidence', 'Low')}, support: {c.get('support_count', 0)})"
        for c in claims
    ])
    
    # Build citations string
    citations_str = "\n".join([
        f"[{i+1}] URL: {c.get('url', '')}"
        for i, c in enumerate(citations)
    ])
    
    findings_text = "\n".join(key_findings) if key_findings else ""
    
    prompt = WRITE_PROMPT.replace("{question}", question)
    prompt = prompt.replace("{executive_summary}", executive_summary)
    prompt = prompt.replace("{key_findings}", findings_text)
    prompt = prompt.replace("{claims}", claims_summary)
    prompt = prompt.replace("{citations}", citations_str)

    raw = _call_model(model, prompt)
    logger.info(f"Write raw output from {model}: {raw[:100]}...")

    # Parse the structured report
    report = raw if raw else _fallback_report(question, key_findings, citations)
    
    # Ensure citations are present
    citations_section = _extract_citations_from_write(report)
    if not citations_section and citations:
        # Append citations if missing
        last_period = report.rfind(".")
        if last_period > 0:
            report = report[:last_period] + "\n\nCITATIONS:\n" + citations_str
    
    return {
        "report": report,
        "citations": citations_section,
        "model": model,
    }


def _fallback_report(
    question: str,
    key_findings: List[str],
    citations: List[dict],
) -> str:
    """Fallback report generation when Ultra model is unavailable."""
    lines = [
        f"EXECUTIVE SUMMARY: Based on the research question: \"{question}\". ",
        "Key findings are summarized below with supporting evidence from collected sources.",
        "",
        "KEY FINDINGS:",
    ]
    
    for i, finding in enumerate(key_findings[:5]):
        lines.append(f"  {i+1}. {finding}")
    
    lines.append("")
    lines.append("CONFIDENT OR UNCERTAIN INFO:")
    lines.append("- Confirmed: The research question has been addressed with collected evidence.")
    lines.append("- Uncertain/Conflicting: Further verification may be needed for some claims.")
    lines.append("")
    
    lines.append("CITATIONS:")
    for i, c in enumerate(citations[:5]):
        lines.append(f"  [{i+1}] URL: {c.get('url', '')}")
    
    return "\n".join(lines)