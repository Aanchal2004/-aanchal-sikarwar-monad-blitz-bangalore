"""
Modular RAG pipeline: load → chunk → embed → retrieve → generate.

TODO: Ingest real documents from datasets/ folder during hackathon.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from config import get_settings
from models.schemas import RAGQueryResponse, RAGSource
from services.llm_provider import get_llm_provider

logger = logging.getLogger(__name__)

# In-memory store for hackathon speed (swap for Chroma in production)
_VECTOR_STORE: list[dict[str, Any]] = []


def _default_documents() -> list[dict[str, Any]]:
    return [
        {
            "content": (
                "Monad is a high-performance EVM-compatible L1 blockchain optimized "
                "for parallel execution and low latency. It supports standard Ethereum "
                "tooling including MetaMask, Foundry, and ethers.js."
            ),
            "metadata": {"source": "monad_overview", "topic": "blockchain"},
        },
        {
            "content": (
                "AI agents on Monad can hold wallets, sign transactions autonomously, "
                "and store reputation on-chain. Agent marketplaces enable discovery "
                "and payment for specialized agent services."
            ),
            "metadata": {"source": "agent_onchain", "topic": "agents"},
        },
        {
            "content": (
                "RAG (Retrieval Augmented Generation) improves LLM answers by retrieving "
                "relevant documents before generation. Typical pipeline: chunk documents, "
                "embed chunks, retrieve top-k similar chunks, pass to LLM as context."
            ),
            "metadata": {"source": "rag_basics", "topic": "rag"},
        },
    ]


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    settings = get_settings()
    size = chunk_size or settings.chunk_size
    step = size - (overlap or settings.chunk_overlap)
    chunks: list[str] = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + size])
        start += step
    return chunks or [text]


async def load_documents(path: str | Path | None = None) -> list[dict[str, Any]]:
    """Load documents from file or use defaults."""
    if path is None:
        return _default_documents()

    file_path = Path(path)
    if not file_path.exists():
        logger.warning("Document path %s not found; using defaults.", file_path)
        return _default_documents()

    text = file_path.read_text(encoding="utf-8")
    chunks = chunk_text(text)
    return [{"content": c, "metadata": {"source": str(file_path)}} for c in chunks]


async def index_documents(documents: list[dict[str, Any]] | None = None) -> int:
    """Embed and store documents in the in-memory vector store."""
    global _VECTOR_STORE
    docs = documents or await load_documents()
    provider = get_llm_provider()
    texts = [d["content"] for d in docs]
    embeddings = await provider.embed(texts)

    _VECTOR_STORE = [
        {"content": d["content"], "metadata": d.get("metadata", {}), "embedding": e}
        for d, e in zip(docs, embeddings)
    ]
    return len(_VECTOR_STORE)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


async def retrieve(question: str, top_k: int = 4) -> list[RAGSource]:
    if not _VECTOR_STORE:
        await index_documents()

    provider = get_llm_provider()
    query_embedding = (await provider.embed([question]))[0]

    scored = [
        (
            _cosine_similarity(query_embedding, item["embedding"]),
            item,
        )
        for item in _VECTOR_STORE
    ]
    scored.sort(key=lambda x: x[0], reverse=True)

    return [
        RAGSource(
            content=item["content"],
            metadata=item.get("metadata", {}),
            score=round(score, 4),
        )
        for score, item in scored[:top_k]
    ]


async def generate_answer(question: str, sources: list[RAGSource]) -> str:
    settings = get_settings()
    provider = get_llm_provider()

    context = "\n\n".join(f"[{i+1}] {s.content}" for i, s in enumerate(sources))
    messages = [
        {
            "role": "system",
            "content": (
                "Answer the question using ONLY the provided context. "
                "If unsure, say you don't know."
            ),
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}",
        },
    ]

    has_key = bool(
        settings.openai_api_key
        or settings.anthropic_api_key
        or settings.openrouter_api_key
    )
    if not has_key:
        return (
            f"[MOCK RAG] Based on {len(sources)} retrieved chunks, "
            f"here is a plausible answer to: {question}"
        )

    return await provider.chat(messages)


async def rag_query(question: str, top_k: int = 4) -> RAGQueryResponse:
    settings = get_settings()
    sources = await retrieve(question, top_k=top_k)
    answer = await generate_answer(question, sources)
    has_key = bool(
        settings.openai_api_key
        or settings.anthropic_api_key
        or settings.openrouter_api_key
    )
    return RAGQueryResponse(
        question=question,
        answer=answer,
        sources=sources,
        mock=not has_key,
    )
