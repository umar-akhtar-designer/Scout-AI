from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Callable

from scoutai.backend.config import validate_config, list_models
from scoutai.backend.planner import plan_question
from scoutai.backend.extractor import extract_parallel
from scoutai.backend.verifier import verify_claims
from scoutai.backend.writer import write_report
from scoutai.backend.models import (
    PipelineStatus,
    PipelineProgress,
    PlanRequest,
    NewQuestionRequest,
    ReportData,
    Source,
)

logger = logging.getLogger(__name__)


class PipelineRun:
    """Orchestrates the full Plan -> Search -> Extract -> Verify -> Write pipeline with SSE progress."""
    
    def __init__(
        self,
        question: str,
        on_progress: Callable[[PipelineProgress], None] = lambda _p: None,
        on_complete: Callable[[Dict], None] = lambda _r: None,
        on_error: Callable[[str], None] = lambda _e: None,
        seed_urls: Optional[List[str]] = None,
    ):
        self.question = question
        self.seed_urls = seed_urls or []
        self.on_progress = on_progress
        self.on_complete = on_complete
        self.on_error = on_error
        
        self.plan_result: Optional[dict] = None
        self.extract_results: Optional[List[dict]] = None
        self.verify_results: Optional[List[dict]] = None
        self.write_result: Optional[dict] = None
        self.progress: Optional[PipelineProgress] = None
        
        self.start_time = time.time()
        self.sources: List[Source] = []
        
        self.model_fast = "nemotron-nano"
        self.model_mid = "nemotron-super"
        self.model_strong = "nemotron-ultra"
        
        if validate_config():
            cfg = list_models()
            self.model_fast = cfg.get("fast", self.model_fast)
            self.model_mid = cfg.get("mid", self.model_mid)
            self.model_strong = cfg.get("strong", self.model_strong)
    
    async def run(self) -> Dict[str, Any]:
        try:
            await self._run_plan()
            if self._check_error("plan"):
                return {"error": "Plan step failed"}
            
            await self._run_search()
            if self._check_error("search"):
                return {"error": "Search step failed"}
            
            await self._run_extract()
            if self._check_error("extract"):
                return {"error": "Extract step failed"}
            
            await self._run_verify()
            if self._check_error("verify"):
                return {"error": "Verify step failed"}
            
            await self._run_write()
            if self._check_error("write"):
                return {"error": "Write step failed"}
            
            return self._build_final_report()
        except Exception as e:
            logger.exception("Unexpected pipeline error")
            self.on_error(str(e))
            return {"error": str(e)}
    
    def _check_error(self, step: str) -> bool:
        return False
    
    async def _run_plan(self):
        self._progress(step="plan", status="running", description="Planning research questions...", model=self.model_fast)
        try:
            self.plan_result = await asyncio.wait_for(
                asyncio.to_thread(plan_question, self.question, model_name=self.model_fast),
                timeout=75,
            )
        except asyncio.TimeoutError:
            logger.warning("Plan step timed out; using fallback plan")
            self.plan_result = {"sub_questions": [self.question], "search_queries": [self.question]}
        self._progress(step="plan", status="done", description=f"Generated {len(self.plan_result.get('sub_questions', []))} sub-questions", model=self.model_fast)
    
    async def _run_search(self):
        from scoutai.backend.searcher import fetch_url_text, search_tavily_queries

        queries = self.plan_result.get("search_queries", [])
        seed_sources: List[Source] = []

        if self.seed_urls:
            self._progress(step="search", status="running", description="Reading linked pages...", model="Tavily")
            for url in self.seed_urls:
                try:
                    data = await asyncio.wait_for(
                        asyncio.to_thread(fetch_url_text, url), timeout=25
                    )
                    if data and data.get("snippet"):
                        seed_sources.append(Source(**data))
                except Exception as e:
                    logger.warning(f"Could not read {url}: {e}")

        if not queries and not seed_sources:
            self._progress(step="search", status="done", description="No search queries generated", model="Tavily")
            self.sources = []
            return

        self._progress(step="search", status="running", description=f"Searching web for {len(queries)} queries...", model="Tavily")

        raw_sources = []
        if queries:
            try:
                raw_sources = await asyncio.wait_for(search_tavily_queries(queries), timeout=60)
            except asyncio.TimeoutError:
                logger.warning("Search step timed out; continuing without web results")
                raw_sources = []

        normalized = []
        for item in raw_sources:
            if isinstance(item, Source):
                normalized.append(item)
                continue
            try:
                normalized.append(Source(
                    url=item.get("url", ""),
                    title=item.get("title", "") or item.get("url", ""),
                    snippet=item.get("snippet", "") or "",
                ))
            except Exception:
                continue

        combined = seed_sources + [s for s in normalized if s.url]
        seen = set()
        deduped = []
        for source in combined:
            if source.url and source.url not in seen:
                seen.add(source.url)
                deduped.append(source)
        self.sources = deduped
        self._progress(
            step="search",
            status="done",
            description=f"Found {len(self.sources)} sources" + (" (linked page included)" if seed_sources else ""),
            model="Tavily",
        )
    
    async def _run_extract(self):
        if not self.sources:
            self._progress(step="extract", status="done", description="No sources to extract from", model=self.model_fast)
            self.extract_results = []
            return
        extract_items = []
        max_items = 9
        sub_questions = self.plan_result.get("sub_questions", [])
        for source in self.sources:
            for sq in sub_questions:
                if len(extract_items) >= max_items:
                    break
                extract_items.append({"sub_question": sq, "source_url": source.url, "content": source.snippet or ""})
            if len(extract_items) >= max_items:
                break
        self._progress(step="extract", status="running", description=f"Extracting facts from {len(extract_items)} source-sub pairs...", model=self.model_fast)
        try:
            self.extract_results = await asyncio.wait_for(
                extract_parallel(extract_items, model_name=self.model_fast), timeout=120
            )
        except asyncio.TimeoutError:
            logger.warning("Extract step timed out; continuing with partial results")
            self.extract_results = []
        self._progress(step="extract", status="done", description=f"Extracted {len([b for r in self.extract_results for b in r.get('bullets', [])])} bullet facts", model=self.model_fast)
    
    async def _run_verify(self):
        if not self.extract_results:
            self._progress(step="verify", status="done", description="No extracted claims to verify", model=self.model_mid)
            self.verify_results = []
            return
        claims_input = []
        claim_sources = {}
        claim_order = []
        for er in self.extract_results:
            source_url = er.get("source_url", "")
            for bullet in er.get("bullets", []):
                text = bullet.get("text", "") if isinstance(bullet, dict) else str(bullet)
                text = (text or "").strip()
                if not text:
                    continue
                key = " ".join(text.lower().split())
                if key not in claim_sources:
                    claim_sources[key] = {"claim": text, "sources": set()}
                    claim_order.append(key)
                if source_url:
                    claim_sources[key]["sources"].add(source_url)
        for key in claim_order:
            entry = claim_sources[key]
            claims_input.append({
                "claim": entry["claim"],
                "support_count": len(entry["sources"]),
                "supporting_sources": sorted(entry["sources"]),
            })
        self._progress(step="verify", status="running", description="Verifying claims against sources...", model=self.model_mid)
        try:
            self.verify_results = await asyncio.wait_for(
                asyncio.to_thread(verify_claims, self.question, claims_input, model_name=self.model_mid),
                timeout=100,
            )
        except asyncio.TimeoutError:
            logger.warning("Verify step timed out; continuing with unverified claims")
            self.verify_results = claims_input
        self._progress(step="verify", status="done", description=f"Verified {len(self.verify_results)} claims", model=self.model_mid)
    
    async def _run_write(self):
        if not self.verify_results:
            self._progress(step="write", status="done", description="No verified claims to write", model=self.model_strong)
            return
        high_claims = [c for c in self.verify_results if c.get("confidence") == "High"]
        uncertain_claims = [c for c in self.verify_results if c.get("confidence") in ("Medium", "Low")]
        exec_summary = ""
        if high_claims:
            exec_summary = f"Research on '{self.question}' found {len(high_claims)} high-confidence claims supported by multiple sources."
        if uncertain_claims:
            if exec_summary:
                exec_summary += " "
            exec_summary += f"{len(uncertain_claims)} claims have medium or low confidence."
        if not exec_summary:
            exec_summary = f"Research on '{self.question}' is in progress."
        key_findings = []
        for i, c in enumerate(self.verify_results[:5]):
            prefix = "Confirmed" if c.get("confidence") == "High" else "Note"
            key_findings.append(f"{prefix}: {c.get('claim', '')[:100]}")
        citations = []
        for i, source in enumerate(self.sources[:5]):
            citations.append({"ordinal": i + 1, "url": source.url})
        self._progress(step="write", status="running", description="Writing final report...", model=self.model_strong)
        try:
            self.write_result = await asyncio.wait_for(
                asyncio.to_thread(
                    write_report, question=self.question, executive_summary=exec_summary,
                    key_findings=key_findings, claims=self.verify_results, citations=citations,
                    model_name=self.model_strong,
                ),
                timeout=120,
            )
        except asyncio.TimeoutError:
            logger.warning("Writer timed out; using fallback report")
            findings = "\n".join(f"{i + 1}. {f}" for i, f in enumerate(key_findings)) or "No findings available."
            cites = "\n".join(f"[{c.get('ordinal', i + 1)}] URL: {c.get('url', '')}" for i, c in enumerate(citations)) or "[1] URL: unavailable"
            self.write_result = {
                "report": f"EXECUTIVE SUMMARY:\n{exec_summary}\n\nKEY FINDINGS:\n{findings}\n\nCITATIONS:\n{cites}\n",
                "citations": citations,
            }
        self._progress(step="write", status="done", description="Report generated", model=self.model_strong)
    
    def _build_final_report(self) -> Dict[str, Any]:
        if self.write_result and self.write_result.get("report"):
            return {"report": self.write_result["report"], "citations": self.write_result.get("citations", []),
                    "model_fast": self.model_fast, "model_mid": self.model_mid, "model_strong": self.model_strong,
                    "total_time": round(time.time() - self.start_time, 2), "sources_count": len(self.sources)}
        return {"report": f"EXECUTIVE SUMMARY: Research on '{self.question}'. Pipeline completed with available data.\n\nKEY FINDINGS: No full report available.\n\nCITATIONS:", "citations": [],
                "model_fast": self.model_fast, "model_mid": self.model_mid, "model_strong": self.model_strong,
                "total_time": round(time.time() - self.start_time, 2), "sources_count": len(self.sources), "fallback": True}
    
    def _progress(self, step: str, status: str, description: str, model: str):
        prog = PipelineProgress(step=step, step_description=description, model=model, done=(status == "done"))
        self.progress = prog
        self.on_progress(prog)
