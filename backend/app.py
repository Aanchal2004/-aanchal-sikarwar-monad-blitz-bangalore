"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from routes.agent import router as agent_router
from routes.chat import router as chat_router
from routes.health import router as health_router
from routes.rag import router as rag_router
from services.rag_service import index_documents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Starting backend | provider=%s model=%s", settings.llm_provider, settings.llm_model)
    count = await index_documents()
    logger.info("Indexed %d RAG documents", count)
    yield
    logger.info("Shutting down backend")


app = FastAPI(
    title="Monad Agent Hackathon Kit",
    description="FastAPI backend for AI agents, RAG, and Monad integration",
    version="0.1.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(agent_router)
app.include_router(rag_router)


@app.get("/")
async def root():
    return {
        "name": "Monad Agent Hackathon Kit API",
        "docs": "/docs",
        "endpoints": ["/health", "/chat", "/agent/run", "/agent/workflow", "/rag/query"],
    }
