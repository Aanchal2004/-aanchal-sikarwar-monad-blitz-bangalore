from fastapi import APIRouter

from config import get_settings
from models.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        provider=settings.llm_provider,
        model=settings.llm_model,
    )
