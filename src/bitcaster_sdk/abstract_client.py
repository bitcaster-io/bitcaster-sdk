"""Bitcaster SDK - Abstract base client."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any


from bitcaster_sdk.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    EventNotFoundError,
    ValidationError,
)


if TYPE_CHECKING:
    from requests import Response
    from bitcaster_sdk.abstract_transport import AbstractTransport

    from .types import JSON


class AbstractClient(ABC):
    """Abstract base for Bitcaster HTTP clients.

    Provides shared constructor, URL parsing, response validation, and
    the :meth:`set_domain` / :meth:`trigger_event` workflow. Subclasses
    implement the actual HTTP methods (sync or async).
    """

    url_regex = (
        r"(?P<schema>https?):\/\/(?P<token>.*)@"
        r"(?P<host>.*)\/api\/"
        r"o\/(?P<organization>.+)\/$"
    )
    _transport_class: type[AbstractTransport]

    def __init__(
        self,
        bae: str | None = None,
        debug: bool = False,
        project: str | None = None,
        application: str | None = None,
    ) -> None:
        """Initialize the client.

        Args:
            bae: Bitcaster endpoint URL (format: ``https://<API_KEY>@<HOST>/api/o/<ORG>/``).
                Falls back to the ``BITCASTER_BAE`` environment variable via
                :func:`bitcaster_sdk.client.init`.
            debug: Enable debug logging.
            project: Default project slug for :meth:`trigger_event`.
            application: Default application slug for :meth:`trigger_event`.

        """
        self.options: dict[str, Any] = {}
        self.transport: AbstractTransport | None = None
        self.project: str | None = project
        self.application: str | None = application
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
        """Organization-scoped API base URL."""
        return "{schema}://{host}/api/o/{organization}/".format(**self.options)

    @property
    def api_url(self) -> str:
        """The server-level API base URL (``https://<HOST>/api/``)."""
        return "{schema}://{host}/api/".format(**self.options)

    @property
    def last_called_url(self) -> str:
        """The last URL that was requested by the transport."""
        return self.transport.last_url

    @staticmethod
    def assert_response(response: Response) -> None:
        """Check an HTTP response and raise a typed exception on failure.

        Raises:
            ValidationError: HTTP 400
            AuthenticationError: HTTP 401
            AuthorizationError: HTTP 403
            EventNotFoundError: HTTP 404
            ConnectionError: Other non-2xx status

        """
        if response.status_code == 400:
            raise ValidationError(f"Invalid request: {response.json()}")
        if response.status_code == 401:
            raise AuthenticationError(f"Invalid token: {response.url}")
        if response.status_code == 403:
            raise AuthorizationError(f"Insufficient grants: {response.json()}")
        if response.status_code == 404:
            raise EventNotFoundError(f"Invalid Url: {response.url}")
        if response.status_code not in {200, 201}:
            raise ConnectionError(response.status_code, response.url)

    def set_domain(self, project: str, application: str) -> None:
        """Set the default project and application for subsequent calls.

        After calling this, :meth:`trigger_event` can be called without
        repeating the project/application arguments.

        Args:
            project: Project slug.
            application: Application slug.

        """
        self.project = project
        self.application = application

    def trigger_event(
        self,
        event: str,
        context: dict[str, str] | None = None,
        options: dict[str, str] | None = None,
        cid: str | None = None,
    ) -> Any:
        """Trigger an event using the pre-configured project/application domain.

        Requires :meth:`set_domain` (or passing ``project``/``application``
        to the constructor) to have been called first.

        Args:
            event: Event slug.
            context: Key/value pairs to include as event context.
            options: Key/value pairs for additional event options.
            cid: Optional correlation ID.

        Returns:
            The API response (a dict for sync, a Future for async).

        """
        if self.project is None or self.application is None:
            raise ConfigurationError("Call client.set_domain(project, app) before client.trigger_event()")
        return self.trigger(self.project, self.application, event, context, options, cid)

    # ---- abstract methods ------------------------------------------------

    @abstractmethod
    def ping(self) -> Any: ...

    @abstractmethod
    def list_events(self, project: str, application: str) -> Any: ...

    @abstractmethod
    def list_users(self) -> Any: ...

    @abstractmethod
    def list_distribution_lists(self, project: str) -> Any: ...

    @abstractmethod
    def list_projects(self) -> Any: ...

    @abstractmethod
    def list_applications(self, project: str) -> Any: ...

    @abstractmethod
    def list_members(self, project: str, distribution_list: str) -> Any: ...

    @abstractmethod
    def trigger(
        self,
        project: str,
        application: str,
        event: str,
        context: dict[str, str] | None = None,
        options: dict[str, str] | None = None,
        cid: str | None = None,
    ) -> Any: ...

    @abstractmethod
    def add_user(self, email: str, first_name: str, last_name: str, custom: JSON | None = None) -> Any: ...

    @abstractmethod
    def unregister_user(self, project: str, username: str, application: str | None = None) -> Any: ...

    @abstractmethod
    def update_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        custom_fields: JSON | None = None,
        mode: str = "ignore",
    ) -> Any: ...
