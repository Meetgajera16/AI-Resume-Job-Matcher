from fastapi import APIRouter, UploadFile, File, Form
from app.services.ingest_service import IngestService
from app.api.schemas import IngestResponse

router = APIRouter()
ingest_service = IngestService()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(
    file: UploadFile = File(...),
    source_type: str = Form(...)
):
    return await ingest_service.process_pdf(file=file, source_type=source_type)