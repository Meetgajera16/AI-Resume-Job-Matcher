from fastapi import APIRouter, File, Form, UploadFile

from app.api.schemas import AnalysisResponse, TextAnalysisRequest
from app.services.analysis_service import AnalysisService


router = APIRouter(prefix="/analyze")
analysis_service = AnalysisService()


@router.post("", response_model=AnalysisResponse, summary="Analyze a resume PDF against a job")
async def analyze_resume_pdf(
    resume: UploadFile = File(..., description="Text-based resume PDF"),
    job_description: str = Form(..., description="Complete job description"),
):
    return await analysis_service.analyze_pdf(resume=resume, job_description=job_description)


@router.post("/text", response_model=AnalysisResponse, summary="Analyze resume and job text")
def analyze_resume_text(payload: TextAnalysisRequest):
    return analysis_service.analyze_text(
        resume_text=payload.resume_text,
        job_description=payload.job_description,
    )
