from fastapi import APIRouter, UploadFile, File, Form
from app.services.index_service import IndexService
from app.api.schemas import IndexResponse

router = APIRouter()
index_service = IndexService()


@router.post("/index", response_model=IndexResponse)
async def index_pdf(
    file: UploadFile = File(...),
    source_type: str = Form(...)
):
    return await index_service.process_and_index(file=file, source_type=source_type)