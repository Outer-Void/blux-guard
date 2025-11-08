"""Policy enforcement decorators that wrap legacy BLUX modules."""

from __future__ import annotations

import asyncio
import functools
from typing import Any, Awaitable, Callable, TypeVar

from . import telemetry

F = TypeVar("F", bound=Callable[..., Awaitable[Any]])


def enforce(channel: str) -> Callable[[F], F]:
    """Decorator that records telemetry before and after coroutine execution."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            telemetry.record_event(
                f"policy.{channel}",
                actor="policy",
                payload={"phase": "before"},
            )
            result = await func(*args, **kwargs)
            telemetry.record_event(
                f"policy.{channel}",
                actor="policy",
                payload={"phase": "after"},
            )
            return result

        return wrapper  # type: ignore[return-value]

    return decorator


@enforce("shell.exec")
async def run_command(command: str) -> int:
    from . import sandbox

    return await sandbox.run_command(command)
