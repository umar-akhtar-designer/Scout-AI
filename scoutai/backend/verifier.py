from __future__ import annotations

import json
import logging
from typing import Any, List

import openai
from typing_extensions import override

from scoutai.backend.config import NEBIUS_BASE_URL, NEBIUS_API_KEY, AVAILABLE_MODELS
from scoutai.backend.prompts import VERIFY_PROMPT

logger = logging.getLogger(__name__)


client = openai.OpenAI(
    base_url=NEBIUS_BASE_URL,
    api_key=NEBIUS_API_KEY,
)


def _call_model(model_name: str, prompt: str) -> str:
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return completion.choices[0].message.content or ""
    except Exception as e:
        logger.warning(f"Verify model call failed for {model_name}: {e}")
        return ""


def _parse_claims_from_verify(raw: str) -> List[dict]:
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start >= 0 and end > start:
        json_str = raw[start:end]
        try:
            parsed = json.loads(json_str)
            if isinstance(parsed.get("claims"), list):
                return parsed["claims"]
        except json.JSONDecodeError:
            pass
    return []


def verify_claims(question: str, claims_input: List[dict], model_name: str = None) -> List[dict]:
    model = model_name or AVAILABLE_MODELS.get("mid", "nemotron-super")
    
    claims_text = "\n".join([
        f"- Claim {i+1}: {c.get('claim', '')} (support: {c.get('support_count', 0)})"
        for i, c in enumerate(claims_input)
    ])
    
    prompt = VERIFY_PROMPT.replace("{question}", question)
    prompt += f'\n\nOriginal question: "{question}"\n\nClaims to verify:\n{claims_text}\n\nFor each claim, determine support count from available sources, assign confidence (High if 2+ sources, Medium if 1 source, Low if 0), and flag conflicts.'
    
    raw = _call_model(model, prompt)
    logger.info(f"Verify raw output from {model}: {raw[:100]}...")
    
    claims = _parse_claims_from_verify(raw)
    
    result = []
    for c in claims:
        result.append({
            "claim": c.get("claim", ""),
            "support_count": c.get("support_count", 0),
            "confidence": c.get("confidence", "Low"),
            "conflicts": c.get("conflicts", []),
            "supporting_sources": c.get("supporting_sources", []),
        })
    
    if not result:
        result = _heuristic_verify(claims_input)
    
    return result


def _heuristic_verify(claims_input: List[dict]) -> List[dict]:
    result = []
    for c in claims_input:
        claim = c.get("claim", "")
        support_count = c.get("support_count", 0)
        if support_count >= 2:
            confidence = "High"
        elif support_count == 1:
            confidence = "Medium"
        else:
            confidence = "Low"
        result.append({
            "claim": claim,
            "support_count": support_count,
            "confidence": confidence,
            "conflicts": [],
            "supporting_sources": [],
        })
    return result
