from __future__ import annotations

import json
import asyncio
import logging
from typing import Any, List

import openai
from typing_extensions import override

from scoutai.backend.config import NEBIUS_BASE_URL, NEBIUS_API_KEY, AVAILABLE_MODELS
from scoutai.backend.prompts import PLAN_PROMPT

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
            temperature=0.3,
        )
        return completion.choices[0].message.content or ""
    except Exception as e:
        logger.warning(f"Model call failed for {model_name}: {e}")
        return ""


def plan_question(question: str, model_name: str = None) -> dict:
    """Decompose a user question into sub-questions and search queries using Nemotron Nano."""
    model = model_name or AVAILABLE_MODELS.get("fast", "nemotron-nano")
    prompt = PLAN_PROMPT + "\n\nQuestion: " + question

    raw = _call_model(model, prompt)
    logger.info(f"Plan raw output from {model}: {raw[:100]}...")

    # Try to parse strict JSON from the model output
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start >= 0 and end > start:
        json_str = raw[start:end]
        try:
            parsed = json.loads(json_str)
            # Validate we have sub_questions and search_queries of same length
            if (
                isinstance(parsed.get("sub_questions"), list)
                and isinstance(parsed.get("search_queries"), list)
                and len(parsed["sub_questions"]) == len(parsed["search_queries"])
                and 3 <= len(parsed["sub_questions"]) <= 5
            ):
                return parsed
        except json.JSONDecodeError:
            pass

    # Fallback: return a minimal plan
    logger.error(f"Failed to parse plan JSON from model {model}. Raw: {raw}")
    return {"sub_questions": [question], "search_queries": [question]}


# Backward-compatible export for any imports expecting the old name
plan_question_decompose = plan_question
