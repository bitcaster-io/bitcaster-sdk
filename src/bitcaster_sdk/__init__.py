from typing import Any, Optional

from bitcaster_sdk import client

from .client import init

__all__ = ["init", "trigger", "ping", "list_events", "list_users", "list_distribution_lists"]


def trigger(
    project: str,
    application: str,
    event: str,
    context: Optional[dict[str, str]] = None,
    options: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    return client.ctx.get().trigger(project, application, event, context, options)


def ping() -> dict[str, Any]:
    return client.ctx.get().ping()


def list_events(project: str, application: str) -> list[dict[str, Any]]:
    return client.ctx.get().list_events(project, application)


def list_distribution_lists(project: str) -> list[dict[str, Any]]:
    return client.ctx.get().list_distribution_lists(project)


def list_members(project: str, distribution_list: str) -> list[dict[str, Any]]:
    return client.ctx.get().list_members(project, distribution_list)


def list_users() -> list[dict[str, Any]]:
    return client.ctx.get().list_users()
