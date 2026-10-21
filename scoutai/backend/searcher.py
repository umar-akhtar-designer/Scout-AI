from __future__ import annotations

import asyncio
import logging
from typing import Any, List

from tavily import TavilyClient

from scoutai.backend.config import TAVILY_API_KEY

logger = logging.getLogger(__name__)


_tavily_client: Any = None


def _get_tavily_client() -> TavilyClient:
    global _tavily_client
    if _tavily_client is None:
        _tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    return _tavily_client


async def search_tavily_queries(queries: List[str]) -> List[dict]:
    if not queries:
        return []
    client = _get_tavily_client()
    
    async def _single_search(query: str) -> List[dict]:
        try:
            response = client.search(
                query=query,
                search_depth="advanced",
                include_answer=False,
                include_raw_content=True,
                max_results=5,
            )
            results = response.get("results", [])
            sources = []
            for r in results:
                url = r.get("url", "")
                title = r.get("title", "")
                snippet = r.get("content", "")
                if url:
                    sources.append({"url": url, "title": title, "snippet": snippet})
            return sources
        except Exception as e:
            logger.error(f"Tavily search failed for '{query}': {e}")
            return []
    
    tasks = [_single_search(q) for q in queries]
    all_sources = await asyncio.gather(*tasks)
    result = []
    for sources in all_sources:
        result.extend(sources)
    seen = set()
    deduped = []
    for s in result:
        if s["url"] not in seen:
            seen.add(s["url"])
            deduped.append(s)
    logger.info(f"Tavily search returned {len(deduped)} unique sources for {len(queries)} queries")
    return deduped
