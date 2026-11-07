from langchain_chroma import Chroma
from app.embeddings.embedding_provider import EmbeddingProvider
from app.core.config import settings


class VectorStoreManager:
    def __init__(self):
        self.persist_directory = settings.chroma_persist_dir

    def get_store(self, collection_name: str) -> Chroma:
        # Keep OpenAI configuration lazy so the local /analyze endpoints work
        # without an API key. RAG indexing/retrieval still uses the configured
        # embedding provider when those endpoints are called.
        embedding_function = EmbeddingProvider().get_embeddings()
        return Chroma(
            collection_name=collection_name,
            embedding_function=embedding_function,
            persist_directory=self.persist_directory
        )
