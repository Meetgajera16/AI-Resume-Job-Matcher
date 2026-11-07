from langchain_openai import OpenAIEmbeddings
from app.core.config import settings


class EmbeddingProvider:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key
        )

    def get_embeddings(self):
        return self.embeddings