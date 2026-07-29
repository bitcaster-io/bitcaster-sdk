from __future__ import annotations

import urllib.parse
from concurrent.futures import Future
from typing import TYPE_CHECKING, Any

import requests.exceptions

from bitcaster_sdk.async_transport import AsyncTransport
from bitcaster_sdk.exceptions import EventNotFoundError

from .client import Client
from .helpers import JsonUpdateMode

if TYPE_CHECKING:
    from bitcaster_sdk.abstract_transport import AbstractTransport

    from .types import JSON


class AsyncClient(Client):
    _transport_class: type[AbstractTransport] = AsyncTransport

    def _submit(self, fn: Any, *args: Any, **kwargs: Any) -> Future[Any]:
        if self.transport is None:
            future: Future[Any] = Future()
            future.set_exception(RuntimeError("client not initialized"))
            return future
        return self.transport.submit(fn, *args, **kwargs)

    def ping(self) -> Future[dict[str, Any]]:
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

    def update_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        custom_fields: JSON | None = None,
        mode: str = JsonUpdateMode.IGNORE,
    ) -> Future[JSON]:
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
        if self.transport is None:
            return True
        if timeout is None:
            timeout = self.options.get("shutdown_timeout", 10)
        return self.transport.flush(timeout)

    def close(self, timeout: float | None = None) -> None:
        if self.transport is None:
            return
        self.flush(timeout)
        self.transport.kill()
        self.transport = None

    def __enter__(self) -> AsyncClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
