"""Pydantic request/response schemas."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    provider: str
    model: str
    version: str = "0.1.0"


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"] = "user"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    agent_id: str | None = None
    stream: bool = False


class ChatResponse(BaseModel):
    reply: str
    agent_id: str | None = None
    provider: str
    model: str
    mock: bool = False


class AgentRunRequest(BaseModel):
    agent_type: str = Field(..., description="planner|researcher|executor|critic|wallet|memory")
    input: str
    context: dict[str, Any] = Field(default_factory=dict)


class AgentRunResponse(BaseModel):
    agent_type: str
    output: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    mock: bool = False


class WorkflowRequest(BaseModel):
    query: str
    context: dict[str, Any] = Field(default_factory=dict)


class WorkflowStep(BaseModel):
    agent: str
    output: str
    duration_ms: int = 0


class WorkflowResponse(BaseModel):
    query: str
    steps: list[WorkflowStep]
    final_output: str
    mock: bool = False


class RAGQueryRequest(BaseModel):
    question: str
    top_k: int = 4
    collection: str = "default"


class RAGSource(BaseModel):
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    score: float = 0.0


class RAGQueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[RAGSource] = Field(default_factory=list)
    mock: bool = False
