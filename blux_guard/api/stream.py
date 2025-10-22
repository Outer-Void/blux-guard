"""Simple broadcast stream for cockpit events."""

from __future__ import annotations

import asyncio
from typing import Set

from fastapi import WebSocket

from ..core import telemetry

_clients: Set[WebSocket] = set()
_loop: asyncio.AbstractEventLoop | None = None


def start() -> None:
    global _loop
    if _loop is None:
        _loop = asyncio.get_event_loop()


async def stop() -> None:
    while _clients:
        socket = _clients.pop()
        await socket.close()


async def register(socket: WebSocket) -> None:
    await socket.accept()
    _clients.add(socket)
    try:
        while True:
            data = await socket.receive_text()
            telemetry.record_event("api.stream", {"message": data})
            for client in list(_clients):
                if client is not socket:
                    await client.send_text(data)
    except Exception:
        pass
    finally:
        _clients.discard(socket)
        await socket.close()
