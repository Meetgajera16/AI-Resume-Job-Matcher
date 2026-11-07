from fastapi import UploadFile
from app.services.ingest_service import IngestService
from app.embeddings.indexer import DocumentIndexer


class IndexService:
    def __init__(self):
        self.ingest_service = IngestService()
        self.indexer = DocumentIndexer()

    async def process_and_index(self, file: UploadFile, source_type: str) -> dict:
        ingestion_result = await self.ingest_service.process_pdf(file, source_type)

        collection_name = self._get_collection_name(source_type)

        indexed_count = self.indexer.index_documents(
            collection_name=collection_name,
            chunks=ingestion_result["chunks"],
            metadata=ingestion_result["metadata"]
        )

        return {
            "status": "success",
            "source_type": source_type,
            "filename": ingestion_result["filename"],
            "collection_name": collection_name,
            "indexed_chunks": indexed_count
        }

    @staticmethod
    def _get_collection_name(source_type: str) -> str:
        if source_type == "resume":
            return "resume_chunks"
        elif source_type == "job_description":
            return "job_chunks"
        else:
            raise ValueError("source_type must be 'resume' or 'job_description'")