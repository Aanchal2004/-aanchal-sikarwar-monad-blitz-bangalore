from fastapi import APIRouter

from models.schemas import AgentRunRequest, AgentRunResponse, WorkflowRequest, WorkflowResponse
from services.agent_service import run_single_agent, run_workflow

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/run", response_model=AgentRunResponse)
async def agent_run(request: AgentRunRequest) -> AgentRunResponse:
    return await run_single_agent(request.agent_type, request.input, request.context)


@router.post("/workflow", response_model=WorkflowResponse)
async def agent_workflow(request: WorkflowRequest) -> WorkflowResponse:
    return await run_workflow(request.query, request.context)
