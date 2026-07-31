"""Bitcaster SDK async HTTP client."""

from __future__ import annotations

import urllib.parse
import warnings
from concurrent.futures import Future
from typing import TYPE_CHECKING, Any

import requests.exceptions

from bitcaster_sdk.async_transport import AsyncTransport
from bitcaster_sdk.exceptions import EventNotFoundError

from .abstract_client import AbstractClient
from .helpers import JsonUpdateMode

if TYPE_CHECKING:
    from bitcaster_sdk.abstract_transport import AbstractTransport

    from .types import JSON


class AsyncClient(AbstractClient):
    """Non-blocking Bitcaster client.

    Every API method returns a :class:`~concurrent.futures.Future` and
    executes the HTTP request on a background thread, leaving the caller
    free to do other work.

    See :class:`~bitcaster_sdk.client.Client` for constructor arguments,
    properties, and shared method documentation. Only overridden methods
    and AsyncClient-specific methods are documented below.
    """

    _transport_class: type[AbstractTransport] = AsyncTransport

    def _submit(self, fn: Any, *args: Any, **kwargs: Any) -> Future[Any]:
        if self.transport is None:
            future: Future[Any] = Future()
            future.set_exception(RuntimeError("client not initialized"))
            return future
        return self.transport.submit(fn, *args, **kwargs)

    def ping(self) -> Future[dict[str, Any]]:
        """Check connectivity with the Bitcaster server (async).

        Returns:
            A Future that resolves to a dict with server information.

        """
        url = self.transport.get_url("/api/system/ping/") if self.transport else ""

        def _call() -> dict[str, Any]:
            if self.transport is None:
                raise RuntimeError("client not initialized")
            try:
                self.transport.last_url = url
                response = self.transport.session.get(url)
                self.assert_response(response)
                return response.json()
            except requests.exceptions.ConnectionError as e:
                raise ConnectionError(f"Connection Error: {self.api_url}") from e

        return self._submit(_call)

    def list_events(self, project: str, application: str) -> Future[list[dict[str, Any]]]:
        """List events for a given project and application (async).

        Returns:
            A Future that resolves to a list of event dicts.

        """
        url = self.transport.get_url(f"p/{project}/a/{application}/e/") if self.transport else ""

        def _call() -> list[dict[str, Any]]:
            if self.transport is None:
                raise RuntimeError("client not initialized")
            self.transport.last_url = url
            response = self.transport.session.get(url)
            self.assert_response(response)
            return response.json()

        return self._submit(_call)

    def list_users(self) -> Future[list[dict[str, Any]]]:
        """List organization users (async).

        Returns:
            A Future that resolves to a list of user dicts.

        """
        url = self.transport.get_url("u/") if self.transport else ""

        def _call() -> list[dict[str, Any]]:
            if self.transport is None:
                raise RuntimeError("client not initialized")
            self.transport.last_url = url
            response = self.transport.session.get(url)
            self.assert_response(response)
            return response.json()

        return self._submit(_call)

    def list_distribution_lists(self, project: str) -> Future[list[dict[str, Any]]]:
        """List distribution lists for a project (async).

        Returns:
            A Future that resolves to a list of distribution list dicts.

        """
        url = self.transport.get_url(f"p/{project}/d/") if self.transport else ""

        def _call() -> list[dict[str, Any]]:
            if self.transport is None:
                raise RuntimeError("client not initialized")
            self.transport.last_url = url
            response = self.transport.session.get(url)
            self.assert_response(response)
            return response.json()

        return self._submit(_call)

    def list_projects(self) -> Future[list[dict[str, Any]]]:
        """List organization projects (async).

        Returns:
            A Future that resolves to a list of project dicts.

        """
        url = self.transport.get_url("p/") if self.transport else ""

        def _call() -> list[dict[str, Any]]:
            if self.transport is None:
                raise RuntimeError("client not initialized")
            self.transport.last_url = url
            response = self.transport.session.get(url)
            self.assert_response(response)
            return response.json()

        return self._submit(_call)

    def list_applications(self, project: str) -> Future[list[dict[str, Any]]]:
        """List applications for a project (async).

        Returns:
            A Future that resolves to a list of application dicts.

        """
        url = self.transport.get_url(f"p/{project}/a/") if self.transport else ""

        def _call() -> list[dict[str, Any]]:
            if self.transport is None:
                raise RuntimeError("client not initialized")
            self.transport.last_url = url
            response = self.transport.session.get(url)
            self.assert_response(response)
            return response.json()

        return self._submit(_call)

    def list_members(self, project: str, distribution_list: str) -> Future[list[dict[str, Any]]]:
        """List distribution list members (async).

        Returns:
            A Future that resolves to a list of member dicts.

        """
        url = self.transport.get_url(f"p/{project}/d/{distribution_list}/m/") if self.transport else ""

        def _call() -> list[dict[str, Any]]:
            if self.transport is None:
                raise RuntimeError("client not initialized")
            self.transport.last_url = url
            response = self.transport.session.get(url)
            self.assert_response(response)
            return response.json()

        return self._submit(_call)

    def trigger(
        self,
        project: str,
        application: str,
        event: str,
        context: dict[str, str] | None = None,
        options: dict[str, str] | None = None,
        cid: str | None = None,
    ) -> Future[dict[str, Any]]:
        """Use :meth:`set_domain` + :meth:`trigger_event` instead."""
        warnings.warn(
            "trigger() is deprecated, use trigger_event() with set_domain() instead",
            DeprecationWarning,
            stacklevel=2,
        )

        def _call() -> dict[str, Any]:
            if self.transport is None:
                raise RuntimeError("client not initialized")
            url = self.transport.get_url(
                f"p/{project}/a/{application}/e/{event}/trigger/{'?cid=' + cid if cid else ''}"
            )
            self.transport.last_url = url
            with self.transport.with_headers({"Content-Type": "application/json"}):
                response = self.transport.session.post(url, json={"context": context or {}, "options": options or {}})
            if response.status_code in [404]:
                raise EventNotFoundError(f"Event not found at {url}")
            self.assert_response(response)
            return response.json()

        return self._submit(_call)

    def add_user(self, email: str, first_name: str, last_name: str, custom: JSON | None = None) -> Future[JSON]:
        """Add a user to the current organization (async).

        Returns:
            A Future that resolves to the created user dict.

        """

        def _call() -> JSON:
            if self.transport is None:
                raise RuntimeError("client not initialized")
            url = self.transport.get_url("u/")
            self.transport.last_url = url
            with self.transport.with_headers({"Content-Type": "application/json"}):
                response = self.transport.session.post(
                    url,
                    json={
                        "email": email,
                        "first_name": first_name or "",
                        "last_name": last_name or "",
                        "custom_fields": custom,
                    },
                )
            self.assert_response(response)
            return response.json()

        return self._submit(_call)

    def unregister_user(self, project: str, application: str, username: str) -> Future[JSON]:
        """Remove a user from all distribution lists pinned to an application (async).

        Returns:
            A Future that resolves to a dict with the number of removed
            memberships, e.g. ``{"deleted": 3}``.

        """
        uid = urllib.parse.quote(username)

        def _call() -> JSON:
            if self.transport is None:
                raise RuntimeError("client not initialized")
            url = self.transport.get_url(f"p/{project}/a/{application}/unregister/{uid}/")
            self.transport.last_url = url
            with self.transport.with_headers({"Content-Type": "application/json"}):
                response = self.transport.session.post(url, json={})
            self.assert_response(response)
            return response.json()

        return self._submit(_call)

    def update_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        custom_fields: JSON | None = None,
        mode: str = JsonUpdateMode.IGNORE,
    ) -> Future[JSON]:
        """Update an existing user (async).

        Returns:
            A Future that resolves to the updated user dict.

        """
        uid = urllib.parse.quote(email)

        def _call() -> JSON:
            if self.transport is None:
                raise RuntimeError("client not initialized")
            url = self.transport.get_url(f"u/{uid}/")
            self.transport.last_url = url
            with self.transport.with_headers({"Content-Type": "application/json"}):
                response = self.transport.session.patch(
                    url,
                    json={
                        "first_name": first_name or "",
                        "last_name": last_name or "",
                        "custom_fields": custom_fields,
                        "_mode": mode,
                    },
                )
            self.assert_response(response)
            return response.json()

        return self._submit(_call)

    def flush(self, timeout: float | None = None) -> bool:
        """Wait for all queued requests to complete.

        Args:
            timeout: Maximum seconds to wait. Falls back to
                ``shutdown_timeout`` (default 10).

        Returns:
            ``True`` if all requests completed, ``False`` on timeout.

        """
        if self.transport is None:
            return True
        if timeout is None:
            timeout = self.options.get("shutdown_timeout", 10)
        return self.transport.flush(timeout)

    def close(self, timeout: float | None = None) -> None:
        """Flush pending work and shut down the background worker.

        The client is unusable after calling this method.

        Args:
            timeout: Maximum seconds to wait for pending requests.

        """
        if self.transport is None:
            return
        self.flush(timeout)
        self.transport.kill()
        self.transport = None

    def __enter__(self) -> AsyncClient:
        """Enter the runtime context."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit the runtime context and shut down the background worker."""
        self.close()
