from __future__ import annotations

import json
import asyncio
import logging
from typing import Any, List

import openai
from typing_extensions import override

from scoutai.backend.config import NEBIUS_BASE_URL, NEBIUS_API_KEY
from scoutai.backend.prompts import EXTRACT_PROMPT

# Set openai API key and base URL at module level
openai.api_key = NEBIUS_API_KEY
openai.base_url = NEBIUS_BASE_URL

logger = logging.getLogger(__name__)


async def extract_from_source(
    sub_question: str,
    source_url: str,
    content: str,
    model_name: str = None,
) -> dict:
    model = model_name or "nemotron-nano"
    prompt = EXTRACT_PROMPT.replace("{sub_question}", sub_question).replace(
        "{source_url}", source_url
    )
    prompt += f'\n\nSub-question: "{sub_question}"\nSource URL: {source_url}\nSource content (truncated if long):\n{content[:3000]}'

    loop = asyncio.get_event_loop()
    raw = await loop.run_in_executor(None, _call_model, model, prompt)
    logger.info(f"Extract raw output from {model}: {raw[:100]}...")

    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start >= 0 and end > start:
        json_str = raw[start:end]
        try:
            parsed = json.loads(json_str)
            if (
                isinstance(parsed.get("bullets"), list)
                and isinstance(parsed.get("sub_question"), str)
                and isinstance(parsed.get("source_url"), str)
            ):
                return parsed
        except json.JSONDecodeError:
            pass

    logger.error(f"Failed to parse extract JSON from model {model}. Raw: {raw}")
    return {"sub_question": sub_question, "bullets": [], "source_url": source_url}


async def extract_parallel(
    items: List[dict],
    model_name: str = None,
) -> List[dict]:
    model = model_name or "nemotron-nano"
    sem = asyncio.Semaphore(6)

    async def _limited(item):
        async with sem:
            return await extract_from_source(
                item["sub_question"], item["source_url"], item["content"], model
            )

    tasks = [_limited(item) for item in items]
    return await asyncio.gather(*tasks)


def _call_model(model_name: str, prompt: str) -> str:
    try:
        client = openai.OpenAI(base_url=NEBIUS_BASE_URL, api_key=NEBIUS_API_KEY, timeout=45.0, max_retries=0)
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=700,
        )
        message = completion.choices[0].message
        return (message.content or getattr(message, "reasoning", "") or "")
    except Exception as e:
        logger.warning(f"Model call failed for {model_name}: {e}")
        return ""
