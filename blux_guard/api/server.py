"""FastAPI server exposing guard status."""

from __future__ import annotations

from fastapi import FastAPI, WebSocket
from fastapi.responses import PlainTextResponse

from ..core import telemetry
from . import stream

app = FastAPI(title="BLUX Guard API")


@app.get("/status")
async def status() -> dict:
    return await telemetry.collect_status()


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics() -> PlainTextResponse:
    chunks = []

    async for chunk in telemetry.iter_prometheus_metrics():
        chunks.append(chunk)
    return PlainTextResponse("\n".join(chunks))


@app.websocket("/stream")
async def websocket_endpoint(socket: WebSocket) -> None:
    await stream.register(socket)


@app.on_event("startup")
async def startup() -> None:
    stream.start()


@app.on_event("shutdown")
async def shutdown() -> None:
    await stream.stop()
