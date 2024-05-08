import os
import re
from contextvars import ContextVar
from typing import Any, Optional

import requests.exceptions
from requests import Response

from bitcaster_sdk.exceptions import (
    AuthenticationError,
    ConfigurationError,
    EventNotFound,
    ValidationError,
)

from .logging import logger
from .transport import Transport

ctx: ContextVar["Client"] = ContextVar("bitcaster_client")


class Client:
    url_regex = (
        r"(?P<schema>https?):\/\/(?P<token>.*)@"
        r"(?P<host>.*)\/api\/"
        r"o\/(?P<organization>.+)\/"
        r"p\/(?P<project>.+)\/"
        r"a\/(?P<application>.+)"
    )

    def __init__(self, bae: Optional[str] = None, debug: Optional[bool] = False) -> None:
        self.options: dict[str, Any] = {}
        self.transport: Optional[Transport] = None
        if bae is not None:
            self.bae = bae
            self.options = {"debug": debug, "shutdown_timeout": 10}
            self.parse_url(bae)
            self.transport = Transport(**self.options)

    def parse_url(self, url: str) -> None:
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
        return "{schema}://{host}/api/o/{organization}/p/{project}/a/{application}/".format(**self.options)

    @property
    def api_url(self) -> str:
        return "{schema}://{host}/api/".format(**self.options)

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
            raise AuthenticationError(f"Insufficient grants: {response.url}")

        if response.status_code in [404]:
            raise EventNotFound(f"Invalid Stream: {response.url} ")

        if response.status_code not in [201, 200]:
            raise ConnectionError(response.status_code, response.url)

    def ping(self) -> dict[str, Any]:
        try:
            response = self.transport.get("/api/system/ping/")
            self.assert_response(response)
            ret = response.json()
            return ret
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Connection Error: {self.api_url}") from e
        except Exception as e:
            logger.exception(e)
            raise

    def list_events(self) -> dict[str, Any]:
        try:
            response = self.transport.get("e/")
            self.assert_response(response)
            ret = response.json()
            return ret
        except Exception as e:
            logger.exception(e)
            raise

    def trigger(
        self, event: str, context: Optional[dict[str, str]] = None, options: Optional[dict[str, str]] = None
    ) -> dict[str, Any]:
        try:
            response = self.transport.post(f"e/{event}/trigger/", {"context": context or {}, "options": options or {}})
            if response.status_code in [404]:
                raise EventNotFound(response.json())
            self.assert_response(response)
            ret = response.json()
            return ret
        except Exception as e:
            logger.exception(e)
            raise


ctx.set(Client(None))


def init(bae: Optional[str] = None, **kwargs: Any) -> "Client":

    if bae is None:
        bae = os.environ.get("BITCASTER_BAE", "")
    bae = bae.strip()
    if not bae:
        raise ConfigurationError("Set BITCASTER_BAE environment variable")

    ctx.set(Client(bae, **kwargs))
    return ctx.get()
