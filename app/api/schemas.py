from pydantic import BaseModel
from typing import Any, Dict, List, Literal


class IngestResponse(BaseModel):
    status: str
    source_type: str
    filename: str
    extracted_characters: int
    num_chunks: int
    chunks: List[str]
    metadata: List[Dict[str, Any]]


class IndexResponse(BaseModel):
    status: str
    source_type: str
    filename: str
    collection_name: str
    indexed_chunks: int


class RetrievedChunk(BaseModel):
    content: str
    metadata: Dict[str, Any]


class MatchResponse(BaseModel):
    status: str
    query: str
    resume_results: List[RetrievedChunk]
    job_results: List[RetrievedChunk]


class TextAnalysisRequest(BaseModel):
    resume_text: str
    job_description: str


class Confidence(BaseModel):
    score: float
    label: Literal["low", "medium", "high"]


class SkillEvidence(BaseModel):
    skill: str
    category: str
    importance: Literal["required", "preferred"]
    matched: bool
    job_evidence: str
    resume_evidence: str | None = None


class SkillAnalysis(BaseModel):
    required: List[SkillEvidence]
    preferred: List[SkillEvidence]
    required_coverage: float
    preferred_coverage: float
    matched_skills: List[str]
    missing_required_skills: List[str]
    missing_preferred_skills: List[str]
    additional_resume_skills: List[str]


class ExperienceAssessment(BaseModel):
    required_years: float | None
    candidate_years: float | None
    matched: bool | None
    score: float
    estimation_method: str | None
    job_evidence: str | None
    resume_evidence: str | None


class EducationAssessment(BaseModel):
    required_level: str | None
    preferred_level: str | None
    candidate_level: str | None
    matched: bool | None
    score: float
    job_evidence: str | None
    resume_evidence: str | None


class Recommendation(BaseModel):
    priority: int
    type: str
    title: str
    action: str


class AnalysisResponse(BaseModel):
    status: str
    analysis_id: str
    algorithm_version: str
    resume_filename: str | None
    overall_score: float
    verdict: str
    verdict_label: str
    confidence: Confidence
    subscores: Dict[str, float]
    weights_used: Dict[str, float]
    skills: SkillAnalysis
    experience: ExperienceAssessment
    education: EducationAssessment
    must_have_gaps: List[str]
    recommendations: List[Recommendation]
    disclaimer: str
