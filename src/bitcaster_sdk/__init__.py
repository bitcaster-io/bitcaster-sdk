"""Bitcaster SDK - Module-level convenience API."""

from __future__ import annotations

import warnings
from typing import Any

from bitcaster_sdk import client

from .client import init
from .version import __version__

__all__ = [
    "init",
    "set_domain",
    "trigger",
    "trigger_event",
    "ping",
    "list_events",
    "list_users",
    "list_distribution_lists",
    "unregister_user",
    "VERSION",
]

VERSION = __version__


def trigger(
    project: str,
    application: str,
    event: str,
    context: dict[str, str] | None = None,
    options: dict[str, str] | None = None,
) -> dict[str, Any]:
    warnings.warn(
        "bitcaster_sdk.trigger() is deprecated, use set_domain() + trigger_event() instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return client.ctx.get().trigger(project, application, event, context, options)


def set_domain(project: str, application: str) -> None:
    client.ctx.get().set_domain(project, application)


def trigger_event(
    event: str,
    context: dict[str, str] | None = None,
    options: dict[str, str] | None = None,
) -> dict[str, Any]:
    return client.ctx.get().trigger_event(event, context, options)


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


def list_projects() -> list[dict[str, Any]]:
    return client.ctx.get().list_projects()


def list_applications(project: str) -> list[dict[str, Any]]:
    return client.ctx.get().list_applications(project)


def unregister_user(project: str, username: str, application: str | None = None) -> dict[str, Any]:
    return client.ctx.get().unregister_user(project, username, application)
