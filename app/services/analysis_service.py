"""Application service for the advanced explainable matcher."""

from __future__ import annotations

import hashlib

from fastapi import HTTPException, UploadFile
from pypdf.errors import PdfReadError

from app.core.config import settings
from app.ingestion.pdf_parser import PDFParser
from app.ingestion.text_cleaner import TextCleaner
from app.scoring.match_score import calculate_match
from app.scoring.suggestions import build_recommendations
from app.utils.file_utils import safe_filename, validate_pdf_bytes, validate_pdf_file


class AnalysisService:
    def __init__(self) -> None:
        self.parser = PDFParser()
        self.cleaner = TextCleaner()

    def analyze_text(self, resume_text: str, job_description: str, resume_filename: str | None = None) -> dict:
        resume_text = self.cleaner.clean(resume_text)
        job_description = self.cleaner.clean(job_description)
        self._validate_text(resume_text, job_description)

        analysis = calculate_match(resume_text, job_description)
        recommendations = build_recommendations(analysis)
        identifier = hashlib.sha256(
            f"{resume_text}\0{job_description}".encode("utf-8", errors="ignore")
        ).hexdigest()[:16]

        return {
            "status": "success",
            "analysis_id": identifier,
            "algorithm_version": "hybrid-explainable-v1",
            "resume_filename": resume_filename,
            **analysis,
            "recommendations": recommendations,
            "disclaimer": (
                "This result is decision support, not a hiring decision. It uses job-related text only, "
                "does not assess protected characteristics, and may miss equivalent or implied experience."
            ),
        }

    async def analyze_pdf(self, resume: UploadFile, job_description: str) -> dict:
        validate_pdf_file(resume, settings.max_file_size_mb)
        file_bytes = await resume.read()
        validate_pdf_bytes(file_bytes, settings.max_file_size_mb)
        try:
            resume_text = self.parser.extract_text_from_bytes(file_bytes)
        except (PdfReadError, ValueError, OSError) as exc:
            raise HTTPException(status_code=400, detail="The PDF could not be read.") from exc
        if not resume_text.strip():
            raise HTTPException(
                status_code=422,
                detail="No selectable text was found. Upload a text-based PDF; scanned PDFs need OCR first.",
            )
        return self.analyze_text(
            resume_text=resume_text,
            job_description=job_description,
            resume_filename=safe_filename(resume.filename or "resume.pdf"),
        )

    @staticmethod
    def _validate_text(resume_text: str, job_description: str) -> None:
        if len(resume_text) < settings.min_resume_text_chars:
            raise HTTPException(
                status_code=422,
                detail=f"Resume text must contain at least {settings.min_resume_text_chars} characters.",
            )
        if len(job_description) < settings.min_job_description_chars:
            raise HTTPException(
                status_code=422,
                detail=f"Job description must contain at least {settings.min_job_description_chars} characters.",
            )
        if len(job_description) > settings.max_job_description_chars:
            raise HTTPException(
                status_code=413,
                detail=f"Job description exceeds {settings.max_job_description_chars:,} characters.",
            )
