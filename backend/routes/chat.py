from fastapi import APIRouter

from models.schemas import ChatRequest, ChatResponse
from services.agent_service import chat

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def post_chat(request: ChatRequest) -> ChatResponse:
    from config import get_settings

    settings = get_settings()
    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    reply, is_mock = await chat(messages, agent_id=request.agent_id)

    return ChatResponse(
        reply=reply,
        agent_id=request.agent_id,
        provider=settings.llm_provider,
        model=settings.llm_model,
        mock=is_mock,
    )
