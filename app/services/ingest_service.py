import os
from uuid import uuid4
from fastapi import UploadFile, HTTPException

from app.core.config import settings
from app.core.logging import setup_logger
from app.utils.file_utils import (
    ensure_directory,
    safe_filename,
    validate_pdf_bytes,
    validate_pdf_file,
)
from app.ingestion.pdf_parser import PDFParser
from app.ingestion.text_cleaner import TextCleaner
from app.ingestion.chunker import TextChunker
from app.ingestion.metadata_builder import MetadataBuilder

logger = setup_logger("ingest_service")


class IngestService:
    def __init__(self):
        self.parser = PDFParser()
        self.cleaner = TextCleaner()
        self.chunker = TextChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )

        ensure_directory(settings.raw_data_dir)
        ensure_directory(settings.processed_data_dir)
        ensure_directory(settings.chroma_persist_dir)

    async def process_pdf(self, file: UploadFile, source_type: str) -> dict:
        if source_type not in {"resume", "job_description"}:
            raise HTTPException(
                status_code=400,
                detail="source_type must be either 'resume' or 'job_description'"
            )

        validate_pdf_file(file, settings.max_file_size_mb)

        file_bytes = await file.read()
        validate_pdf_bytes(file_bytes, settings.max_file_size_mb)

        filename = safe_filename(file.filename)
        save_path = os.path.join(settings.raw_data_dir, f"{uuid4().hex}_{filename}")

        with open(save_path, "wb") as f:
            f.write(file_bytes)

        logger.info(f"Saved file to {save_path}")

        raw_text = self.parser.extract_text(save_path)
        if not raw_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the PDF."
            )

        cleaned_text = self.cleaner.clean(raw_text)
        chunks = self.chunker.split(cleaned_text)
        metadata = MetadataBuilder.build(chunks, source_type, filename)

        return {
            "status": "success",
            "source_type": source_type,
            "filename": filename,
            "extracted_characters": len(cleaned_text),
            "num_chunks": len(chunks),
            "chunks": chunks,
            "metadata": metadata
        }
