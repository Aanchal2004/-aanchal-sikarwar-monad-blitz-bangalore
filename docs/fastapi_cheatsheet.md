# FastAPI Cheat Sheet

## Run Server

```bash
cd backend
uvicorn app:app --reload --port 8000
```

## Route Pattern

```python
from fastapi import APIRouter
router = APIRouter(prefix="/items", tags=["items"])

@router.get("/")
async def list_items():
    return {"items": []}

@router.post("/")
async def create_item(data: ItemCreate):
    return data
```

## Pydantic Models

```python
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    agent_id: str | None = None
```

## Include Router in app.py

```python
from routes.chat import router as chat_router
app.include_router(chat_router)
```

## CORS

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], ...)
```

## Lifespan (startup/shutdown)

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await index_documents()  # startup
    yield
    # shutdown cleanup
```

## Test with httpx

```python
from httpx import AsyncClient, ASGITransport
transport = ASGITransport(app=app)
async with AsyncClient(transport=transport, base_url="http://test") as client:
    r = await client.get("/health")
```

## Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## This Kit's Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | /health | Health check |
| POST | /chat | Chat with LLM |
| POST | /agent/run | Run single agent |
| POST | /agent/workflow | Multi-agent pipeline |
| POST | /rag/query | RAG question answering |
