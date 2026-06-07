from fastapi import APIRouter

from models.schemas import RAGQueryRequest, RAGQueryResponse
from services.rag_service import rag_query

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/query", response_model=RAGQueryResponse)
async def rag_query_endpoint(request: RAGQueryRequest) -> RAGQueryResponse:
    return await rag_query(request.question, top_k=request.top_k)
