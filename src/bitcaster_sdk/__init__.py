from typing import Any, Optional

from bitcaster_sdk import client

from .client import init

__all__ = ["init", "trigger", "ping", "list_events"]


def trigger(event: str, context: Optional[dict[str, str]] = None, options: Optional[dict[str, str]] = None):
    return client.ctx.get().trigger(event, context, options)


def ping() -> dict[str, Any]:
    return client.ctx.get().ping()


def list_events() -> dict[str, Any]:
    return client.ctx.get().list_events()
