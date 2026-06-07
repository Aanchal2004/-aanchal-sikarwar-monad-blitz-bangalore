"""Backend API smoke tests."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app import app


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_chat(client):
    r = await client.post("/chat", json={"messages": [{"role": "user", "content": "hi"}]})
    assert r.status_code == 200
    assert "reply" in r.json()


@pytest.mark.asyncio
async def test_agent_run(client):
    r = await client.post("/agent/run", json={"agent_type": "planner", "input": "test goal"})
    assert r.status_code == 200
    assert r.json()["agent_type"] == "planner"


@pytest.mark.asyncio
async def test_workflow(client):
    r = await client.post("/agent/workflow", json={"query": "build a demo"})
    assert r.status_code == 200
    data = r.json()
    assert "steps" in data
    assert "final_output" in data


@pytest.mark.asyncio
async def test_rag_query(client):
    r = await client.post("/rag/query", json={"question": "What is Monad?"})
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data
    assert "sources" in data
