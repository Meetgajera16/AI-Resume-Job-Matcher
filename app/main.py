from fastapi import FastAPI
from app.core.config import settings
from app.api.routes.health import router as health_router
from app.api.routes.ingest import router as ingest_router
from app.api.routes.index import router as index_router
from app.api.routes.match import router as match_router
from app.api.routes.analyze import router as analyze_router
from app.api.routes.explain import router as explain_router

app = FastAPI(
    title=settings.app_name,
    description="Explainable resume-to-job matching with optional RAG retrieval.",
    version="0.3.0",
)

app.include_router(health_router, tags=["Health"])
app.include_router(ingest_router, tags=["Ingestion"])
app.include_router(index_router, tags=["Indexing"])
app.include_router(match_router, tags=["Matching"])
app.include_router(analyze_router, tags=["Advanced Analysis"])
app.include_router(explain_router, tags=["Advanced Analysis"])
