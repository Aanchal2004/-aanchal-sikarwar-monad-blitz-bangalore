"""Tiny in-process event bus + WebSocket fan-out, keyed by run_id.
Keeps an event history per run so REST/late subscribers can replay.
"""
from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class EventBus:
    def __init__(self) -> None:
        self._subs: dict[int, set[WebSocket]] = defaultdict(set)
        self._history: dict[int, list[dict]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def subscribe(self, run_id: int, ws: WebSocket) -> None:
        async with self._lock:
            self._subs[run_id].add(ws)
        for ev in list(self._history.get(run_id, [])):
            await ws.send_json(ev)

    async def unsubscribe(self, run_id: int, ws: WebSocket) -> None:
        async with self._lock:
            self._subs[run_id].discard(ws)

    def history(self, run_id: int) -> list[dict]:
        return list(self._history.get(run_id, []))

    async def emit(self, run_id: int, event_type: str, payload: dict[str, Any]) -> None:
        ev = {"run_id": run_id, "type": event_type, **payload}
        self._history[run_id].append(ev)
        dead = []
        for ws in list(self._subs.get(run_id, set())):
            try:
                await ws.send_json(ev)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.unsubscribe(run_id, ws)


bus = EventBus()
