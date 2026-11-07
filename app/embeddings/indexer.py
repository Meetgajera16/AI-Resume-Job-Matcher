from typing import List, Dict
from langchain_core.documents import Document
from app.embeddings.vector_store import VectorStoreManager


class DocumentIndexer:
    def __init__(self):
        self.vector_store_manager = VectorStoreManager()

    def index_documents(
        self,
        collection_name: str,
        chunks: List[str],
        metadata: List[Dict]
    ) -> int:
        if len(chunks) != len(metadata):
            raise ValueError("Chunks and metadata must have the same length.")

        documents = [
            Document(page_content=chunk, metadata=meta)
            for chunk, meta in zip(chunks, metadata)
        ]

        store = self.vector_store_manager.get_store(collection_name)
        store.add_documents(documents)

        return len(documents)