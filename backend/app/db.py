"""SQLite mirror (via SQLModel). Chain is the source of truth; this is the fast
local read model that drives hiring decisions (avoids Monad's ~1.2s read lag).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel, create_engine, Session

from . import config

engine = create_engine(f"sqlite:///{config.DB_PATH}", connect_args={"check_same_thread": False})


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Agent(SQLModel, table=True):
    agent_id: int = Field(primary_key=True)
    name: str
    skill: str
    wallet: str
    price_mon: float
    persona: str = ""
    operator: str = ""  # who owns/operates this agent (signals Agent != Manager)
    rep_sum: int = 0
    rep_jobs: int = 0

    @property
    def reputation(self) -> float:
        return (self.rep_sum / self.rep_jobs) if self.rep_jobs else 0.0


class Run(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    prompt: str
    budget_mon: float = 0.0  # workforce budget the human allocated for this run
    status: str = "running"  # running | completed | failed
    final_result: str = ""
    created_at: str = Field(default_factory=_now)


class Subtask(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(index=True)
    idx: int
    description: str
    skill: str
    status: str = "pending"  # pending | hiring | paid | working | rated | done | skipped


class Decision(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subtask_id: int = Field(index=True)
    candidates_json: str  # snapshot list of {agent_id,name,price,reputation,utility}
    selected_agent_id: int
    utility: float
    reasoning: str = ""


class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subtask_id: int = Field(index=True)
    agent_id: int
    amount_mon: float
    tx_hash: str = ""
    block: int = 0
    status: str = "sent"  # sent | confirmed | failed
    latency_ms: int = 0  # wall-clock to on-chain confirmation


class Rating(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subtask_id: int = Field(index=True)
    agent_id: int
    score: int
    tx_hash: str = ""


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
