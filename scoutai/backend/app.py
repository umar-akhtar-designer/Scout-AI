from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional, Callable

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from scoutai.backend.config import validate_config, list_models, NEBIUS_API_KEY, NEBIUS_BASE_URL, TAVILY_API_KEY
from scoutai.backend.pipeline import PipelineRun, PipelineProgress
from scoutai.backend.models import PlanRequest, NewQuestionRequest, PipelineStatus, ReportData

logger = logging.getLogger(__name__)

app = FastAPI(title="ScoutAI", description="Multi-model deep research agent", version="0.1.0")

# --- Static / Templates ---
PROJECT_DIR = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_DIR / "scoutai" / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"
TEMPLATE_DIR = FRONTEND_DIR / "templates"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATE_DIR) if TEMPLATE_DIR.exists() else str(PROJECT_DIR / "templates"))

# --- Global state ---
active_runs: Dict[str, PipelineRun] = {}


@app.on_event("startup")
async def startup_check():
    logger.info("ScoutAI startup check")
    if validate_config():
        models = list_models()
        logger.info(f"Configured models: {models}")
        try:
            from scoutai.backend.planner import plan_question
            result = plan_question("What is AI?", model_name=models.get("fast", "nemotron-nano"))
            logger.info(f"Plan test result: {result}")
        except Exception as e:
            logger.warning(f"Model test call failed: {e}")
    else:
        logger.warning("Startup config validation failed")


@app.get("/health", response_model=Dict[str, str])
async def health():
    return {"status": "ok", "message": "ScoutAI is running"}


@app.get("/api/contract")
async def api_contract():
    return {
        "events": [
            {"name": "plan_start", "description": "Planning step started", "fields": ["step", "model"]},
            {"name": "plan_done", "description": "Planning step completed", "fields": ["step", "model", "sub_questions_count"]},
            {"name": "plan_error", "description": "Planning step failed", "fields": ["step", "model", "error"]},
            {"name": "search_start", "description": "Search step started", "fields": ["step", "model", "query_count"]},
            {"name": "search_done", "description": "Search step completed", "fields": ["step", "model", "sources_count"]},
            {"name": "search_error", "description": "Search step failed", "fields": ["step", "model", "error"]},
            {"name": "extract_start", "description": "Extraction step started", "fields": ["step", "model", "item_count"]},
            {"name": "extract_done", "description": "Extraction step completed", "fields": ["step", "model", "bullets_count"]},
            {"name": "extract_error", "description": "Extraction step failed", "fields": ["step", "model", "error"]},
            {"name": "verify_start", "description": "Verification step started", "fields": ["step", "model", "claim_count"]},
            {"name": "verify_done", "description": "Verification step completed", "fields": ["step", "model", "claims_verified"]},
            {"name": "verify_error", "description": "Verification step failed", "fields": ["step", "model", "error"]},
            {"name": "write_start", "description": "Report writing step started", "fields": ["step", "model"]},
            {"name": "write_done", "description": "Report writing step completed", "fields": ["step", "model", "report_id"]},
            {"name": "write_error", "description": "Writing step failed", "fields": ["step", "model", "error"]},
            {"name": "complete", "description": "Pipeline complete with final report", "fields": ["report", "citations", "total_time"]},
        ]
    }


@app.get("/sse/{run_id}")
async def sse_stream(run_id: str):
    run = active_runs.get(run_id)
    if not run:
        return JSONResponse({"type": "error", "data": {"message": "Run not found"}}, status_code=404)
    
    async def event_stream():
        await asyncio.sleep(0.1)
        if run.write_result:
            report = run.write_result.get("report", "")
            citations = run.write_result.get("citations", [])
            total_time = round(time.time() - run.start_time, 2)
            yield f"data: {json.dumps({'type': 'complete', 'data': {'report': report, 'citations': citations, 'total_time': total_time}})}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'progress', 'data': {'step': 'plan', 'status': 'running', 'model': run.model_fast, 'step_description': 'Planning research questions...'}})}\n\n"
            for _ in range(60):
                await asyncio.sleep(0.1)
                if run.write_result:
                    report = run.write_result.get("report", "")
                    citations = run.write_result.get("citations", [])
                    total_time = round(time.time() - run.start_time, 2)
                    yield f"data: {json.dumps({'type': 'complete', 'data': {'report': report, 'citations': citations, 'total_time': total_time}})}\n\n"
                    break
            if not run.write_result:
                yield f"data: {json.dumps({'type': 'error', 'data': {'message': 'Pipeline timeout'}})}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/api/run")
async def api_run(request: NewQuestionRequest, background_tasks: Any = None):
    run_id = f"run_{int(time.time() * 1000)}"
    if run_id in active_runs:
        del active_runs[run_id]
    run = PipelineRun(question=request.question, on_progress=lambda prog: None, on_complete=lambda r: None, on_error=lambda err: logger.error(f"Pipeline error: {err}"))
    active_runs[run_id] = run
    import asyncio
    async def _run_and_store():
        try:
            result = await run.run()
            active_runs[run_id].write_result = result
        except Exception as e:
            logger.exception("Background pipeline error")
            active_runs[run_id].write_result = {"error": str(e)}
    asyncio.create_task(_run_and_store())
    return {"run_id": run_id, "status": "started"}


@app.get("/api/run/{run_id}")
async def api_run_status(run_id: str):
    run = active_runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    total_time = round(time.time() - run.start_time, 2) if hasattr(run, 'start_time') else 0
    return {"run_id": run_id, "status": "completed" if run.write_result else "running", "total_time": total_time, "has_report": run.write_result is not None}


@app.post("/api/demo")
async def api_demo():
    return {"report": "EXECUTIVE SUMMARY: This is a demo report generated with cached data. When real APIs are available, this will be replaced with a full multi-model research report.\n\nKEY FINDINGS: \n1. The research question has been addressed with collected evidence from multiple sources.\n2. Key findings are summarized with confidence ratings and citations.\n\nCONFIDENT OR UNCERTAIN INFO:\n- Confirmed: Demo mode is active, providing UI functionality during API downtime.\n- Uncertain/Conflicting: Some claims may need verification with live API access.\n\nCITATIONS:\n[1] URL: https://example.com\n"}


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "ScoutAI"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
