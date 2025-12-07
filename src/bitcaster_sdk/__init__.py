from typing import Any

from bitcaster_sdk import client

from .client import init

__all__ = ["init", "trigger", "ping", "list_events"]


def trigger(event: str, context: dict[str, str] | None = None, options: dict[str, str] | None = None):
    return client.ctx.get().trigger(event, context, options)


def ping() -> dict[str, Any]:
    return client.ctx.get().ping()


def list_events() -> dict[str, Any]:
    return client.ctx.get().list_events()
