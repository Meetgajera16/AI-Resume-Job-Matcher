from typing import List
from app.embeddings.vector_store import VectorStoreManager
from app.core.config import settings


class RetrievalService:
    def __init__(self):
        self.vector_store_manager = VectorStoreManager()

    def retrieve(self, collection_name: str, query: str, k: int = None) -> List:
        top_k = k or settings.top_k_results
        store = self.vector_store_manager.get_store(collection_name)
        return store.similarity_search(query, k=top_k)