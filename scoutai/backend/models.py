from __future__ import annotations

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    question: str = Field(..., description="The user's research question")


class PlanSubQuestions(BaseModel):
    sub_questions: List[str] = Field(..., description="Decomposed sub-questions")
    search_queries: List[str] = Field(..., description="Search queries for each sub-question")


class PlanResponse(BaseModel):
    sub_questions: List[str]
    search_queries: List[str]


class Source(BaseModel):
    url: str = Field(..., description="Source URL")
    title: str = Field(..., description="Source title/snippet")
    snippet: str = Field(..., description="Content snippet from the source")


class ExtractRequest(BaseModel):
    sub_question: str
    source_url: str
    content: str


class ExtractBullet(BaseModel):
    text: str = Field(..., description="Bullet point fact")
    source_url: str = Field(..., description="Source URL")


class ExtractResponse(BaseModel):
    sub_question: str
    bullets: List[ExtractBullet]


class Claim(BaseModel):
    claim: str = Field(..., description="The claim statement")
    support_count: int = Field(..., ge=0, le=5, description="Number of sources supporting this claim")
    confidence: str = Field(..., description="High/Medium/Low")
    conflicts: List[str] = Field(default_factory=list, description="Conflicting claims")
    supporting_sources: List[str] = Field(default_factory=list, description="Source URLs supporting this claim")


class VerifyRequest(BaseModel):
    question: str
    claims: List[Claim]


class VerifyResponse(BaseModel):
    claims: List[Dict[str, Any]]


class WriteRequest(BaseModel):
    question: str
    executive_summary: str
    key_findings: List[str]
    citations: List[Dict[str, str]]


class WriteResponse(BaseModel):
    report: str


class PipelineStatus(BaseModel):
    step: str
    status: str  # "running", "done", "error"
    description: str
    model: str


class PipelineProgress(BaseModel):
    step: str
    step_description: str
    model: str
    done: bool = False
    error: Optional[str] = None


class NewQuestionRequest(BaseModel):
    question: str
    model: Optional[str] = None


class ReportData(BaseModel):
    executive_summary: str
    key_findings: List[str]
    confirmed: List[Dict[str, Any]]
    uncertain: List[Dict[str, Any]]
    citations: List[Dict[str, str]]
