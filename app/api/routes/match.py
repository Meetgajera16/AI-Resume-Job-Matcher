from fastapi import APIRouter, Query
from app.services.match_service import MatchService
from app.api.schemas import MatchResponse

router = APIRouter()
match_service = MatchService()


@router.post("/match", response_model=MatchResponse)
def match_documents(
    query: str = Query(..., description="Semantic query for resume-job comparison")
):
    return match_service.run_match(query=query)