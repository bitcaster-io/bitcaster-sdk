from __future__ import annotations

import os
import re
import urllib.parse
from contextvars import ContextVar
from typing import TYPE_CHECKING, Any

import requests.exceptions
from requests import Response

from bitcaster_sdk.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    EventNotFoundError,
    ValidationError,
)

from .helpers import JsonUpdateMode
from .log import logger
from .transport import Transport

if TYPE_CHECKING:
    from bitcaster_sdk.abstract_transport import AbstractTransport

    from .types import JSON

ctx: ContextVar["Client"] = ContextVar("bitcaster_client")


class Client:
    url_regex = (
        r"(?P<schema>https?):\/\/(?P<token>.*)@"
        r"(?P<host>.*)\/api\/"
        r"o\/(?P<organization>.+)\/$"
    )
    _transport_class: type[AbstractTransport] = Transport

    def __init__(self, bae: str | None = None, debug: bool = False) -> None:
        self.options: dict[str, Any] = {}
        self.transport: AbstractTransport | None = None
        if bae is not None:
            self.bae = bae
            self.options = {"debug": debug, "shutdown_timeout": 10}
            self.parse_url(bae)
            self.transport = self._transport_class(**self.options)

    def parse_url(self, url: str) -> None:
        if not url.endswith("/"):
            url = url + "/"
        m = re.compile(self.url_regex).match(url)
        if not m:
            raise ConfigurationError(
                f"""Unable to parse url: '{url}'.
must match {self.url_regex}"""
            )
        self.options.update(m.groupdict())
        self.options["base_url"] = self.base_url

    @property
    def base_url(self) -> str:
        return "{schema}://{host}/api/o/{organization}/".format(**self.options)

    @property
    def api_url(self) -> str:
        return "{schema}://{host}/api/".format(**self.options)

    @property
    def last_called_url(self) -> str:
        return self.transport.last_url

    def assert_response(self, response: "Response") -> None:
        if response.status_code in [
            400,
        ]:
            raise ValidationError(f"Invalid request: {response.json()}")
        if response.status_code in [
            401,
        ]:
            raise AuthenticationError(f"Invalid token: {response.url}")

        if response.status_code in [
            403,
        ]:
            raise AuthorizationError(f"Insufficient grants: {response.json()}")

        if response.status_code in [404]:
            raise EventNotFoundError(f"Invalid Url: {response.url} ")

        if response.status_code not in [201, 200]:
            raise ConnectionError(response.status_code, response.url)

    def ping(self) -> dict[str, Any]:
        try:
            response = self.transport.get("/api/system/ping/")
            self.assert_response(response)
            return response.json()
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Connection Error: {self.api_url}") from e
        except Exception as e:
            logger.exception(e)
            raise

    def list_events(self, project: str, application: str) -> list[dict[str, Any]]:
        try:
            response = self.transport.get(f"p/{project}/a/{application}/e/")
            self.assert_response(response)
            return response.json()
        except Exception as e:
            logger.exception(e)
            raise e

    def list_users(self) -> list[dict[str, Any]]:
        try:
            response = self.transport.get("u/")
            self.assert_response(response)
            return response.json()
        except Exception as e:
            logger.exception(e)
            raise

    def list_distribution_lists(self, project: str) -> list[dict[str, Any]]:
        try:
            response = self.transport.get(f"p/{project}/d/")
            self.assert_response(response)
            return response.json()
        except Exception as e:
            logger.exception(e)
            raise

    def list_projects(self) -> list[dict[str, Any]]:
        try:
            response = self.transport.get("p/")
            self.assert_response(response)
            return response.json()
        except Exception as e:
            logger.exception(e)
            raise

    def list_applications(self, project: str) -> list[dict[str, Any]]:
        try:
            response = self.transport.get(f"p/{project}/a/")
            self.assert_response(response)
            return response.json()
        except Exception as e:
            logger.exception(e)
            raise

    def list_members(self, project: str, distribution_list: str) -> list[dict[str, Any]]:
        try:
            response = self.transport.get(f"p/{project}/d/{distribution_list}/m/")
            self.assert_response(response)
            return response.json()
        except Exception as e:
            logger.exception(e)
            raise

    def trigger(
        self,
        project: str,
        application: str,
        event: str,
        context: dict[str, str] | None = None,
        options: dict[str, str] | None = None,
        cid: str | None = None,
    ) -> dict[str, Any]:
        try:
            if cid:
                cid = f"?cid={cid}"
            else:
                cid = ""
            url = self.transport.get_url(f"p/{project}/a/{application}/e/{event}/trigger/{cid}")
            response = self.transport.post(url, {"context": context or {}, "options": options or {}})
            if response.status_code in [404]:
                raise EventNotFoundError(f"Event not found at {url}")
            self.assert_response(response)
            return response.json()
        except Exception as e:
            logger.exception(e)
            raise

    def add_user(self, email: str, first_name: str, last_name: str, custom: "JSON | None" = None) -> "JSON":
        try:
            response = self.transport.post(
                "u/",
                {"email": email, "first_name": first_name or "", "last_name": last_name or "", "custom_fields": custom},
            )
            self.assert_response(response)
            return response.json()
        except Exception as e:
            logger.exception(e)
            raise

    def update_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        custom_fields: "JSON | None" = None,
        mode: str = JsonUpdateMode.IGNORE,
    ) -> "JSON":
        try:
            uid = urllib.parse.quote(email)
            response = self.transport.patch(
                f"u/{uid}/",
                {
                    "first_name": first_name or "",
                    "last_name": last_name or "",
                    "custom_fields": custom_fields,
                    "_mode": mode,
                },
            )
            self.assert_response(response)
            return response.json()
        except ValidationError:
            raise
        except Exception as e:
            logger.exception(e)
            raise


ctx.set(Client(None))


def init(bae: str | None = None, **kwargs: Any) -> "Client":
    if bae is None:
        bae = os.environ.get("BITCASTER_BAE", "")
    bae = bae.strip()
    if not bae:
        raise ConfigurationError("Set BITCASTER_BAE environment variable")

    ctx.set(Client(bae, **kwargs))
    return ctx.get()
