from __future__ import annotations

import asyncio
import io
import logging
import re
from typing import Any, List

import requests
from bs4 import BeautifulSoup
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
            response = await asyncio.to_thread(
                client.search,
                query=query,
                search_depth="basic",
                include_answer=False,
                include_raw_content=False,
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


URL_RE = re.compile(r"https?://[^\s<>\"'\])}]+", re.IGNORECASE)


def extract_urls(text: str, limit: int = 2) -> List[str]:
    """Return unique http(s) URLs found in a message, capped at `limit`."""
    seen = []
    for match in URL_RE.findall(text or ""):
        url = match.rstrip(".,;:!?")
        if url not in seen:
            seen.append(url)
        if len(seen) >= limit:
            break
    return seen


def fetch_url_text(url: str, max_chars: int = 6000, timeout: int = 20) -> dict:
    """Fetch a URL and return {url, title, snippet} with readable text."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    content_type = (response.headers.get("content-type") or "").lower()

    if "application/pdf" in content_type:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(response.content))
        text = "\n".join((page.extract_text() or "") for page in reader.pages[:30])
        title = url
    elif "html" in content_type or not content_type:
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()
        title = (soup.title.get_text(strip=True) if soup.title else "") or url
        text = " ".join(soup.get_text(" ").split())
    else:
        title = url
        text = response.text

    text = " ".join(text.split())
    if not text:
        raise ValueError("No readable text found at this URL")
    return {"url": url, "title": title[:200], "snippet": text[:max_chars]}
