"""Bitcaster SDK sync HTTP client."""

from __future__ import annotations

import os
import urllib.parse
import warnings
from contextvars import ContextVar
from typing import TYPE_CHECKING, Any

import requests.exceptions

from bitcaster_sdk.exceptions import (
    ConfigurationError,
    EventNotFoundError,
    ValidationError,
)

from .abstract_client import AbstractClient
from .helpers import JsonUpdateMode
from .log import logger
from .transport import Transport

if TYPE_CHECKING:
    from bitcaster_sdk.abstract_transport import AbstractTransport

    from .types import JSON

ctx: ContextVar["Client"] = ContextVar("bitcaster_client")


class Client(AbstractClient):
    """Sync HTTP client for the Bitcaster REST API.

    Every method blocks on the HTTP request and returns the parsed response
    directly.
    """

    _transport_class: type[AbstractTransport] = Transport

    def ping(self) -> dict[str, Any]:
        """Check connectivity with the Bitcaster server.

        Returns:
            A dict with server identifying information (e.g. ``token``, ``slug``).

        """
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
        """List events for a given project and application.

        Args:
            project: Project slug.
            application: Application slug.

        Returns:
            A list of event dicts, each containing ``name``, ``slug``,
            ``active``, ``locked``, ``description``.

        """
        try:
            response = self.transport.get(f"p/{project}/a/{application}/e/")
            self.assert_response(response)
            return response.json()
        except Exception as e:
            logger.exception(e)
            raise e

    def list_users(self) -> list[dict[str, Any]]:
        """List users in the current organization.

        Returns:
            A list of user dicts, each containing ``email``, ``username``,
            ``is_active``, ``locked``, etc.

        """
        try:
            response = self.transport.get("u/")
            self.assert_response(response)
            return response.json()
        except Exception as e:
            logger.exception(e)
            raise

    def list_distribution_lists(self, project: str) -> list[dict[str, Any]]:
        """List distribution lists for a project.

        Args:
            project: Project slug.

        Returns:
            A list of distribution list dicts.

        """
        try:
            response = self.transport.get(f"p/{project}/d/")
            self.assert_response(response)
            return response.json()
        except Exception as e:
            logger.exception(e)
            raise

    def list_projects(self) -> list[dict[str, Any]]:
        """List projects in the current organization.

        Returns:
            A list of project dicts, each containing ``slug``, ``name``,
            ``applications``, ``lists``, ``channels``.

        """
        try:
            response = self.transport.get("p/")
            self.assert_response(response)
            return response.json()
        except Exception as e:
            logger.exception(e)
            raise

    def list_applications(self, project: str) -> list[dict[str, Any]]:
        """List applications for a project.

        Args:
            project: Project slug.

        Returns:
            A list of application dicts, each containing ``slug``, ``name``.

        """
        try:
            response = self.transport.get(f"p/{project}/a/")
            self.assert_response(response)
            return response.json()
        except Exception as e:
            logger.exception(e)
            raise

    def list_members(self, project: str, distribution_list: str) -> list[dict[str, Any]]:
        """List members of a distribution list.

        Args:
            project: Project slug.
            distribution_list: Distribution list ID.

        Returns:
            A list of member dicts, each containing ``id``, ``address``,
            ``user``, ``channel``.

        """
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
        """Use :meth:`set_domain` + :meth:`trigger_event` instead."""
        warnings.warn(
            "trigger() is deprecated, use trigger_event() with set_domain() instead",
            DeprecationWarning,
            stacklevel=2,
        )
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
        """Add a new user to the current organization.

        Args:
            email: User email address.
            first_name: User first name.
            last_name: User last name.
            custom: Optional dict of custom fields.

        Returns:
            The API response dict for the created user.

        """
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

    def unregister_user(self, project: str, username: str, application: str | None = None) -> "JSON":
        """Remove a user from a project's or application's distribution lists.

        With ``application``, removes the user from all distribution lists
        pinned to that application; requires the ``MANAGE_APPLICATION_USERS``
        grant. Without it, removes the user from *every* distribution list in
        the project (pinned or not); requires the ``MANAGE_PROJECT_USERS``
        grant and an API key scoped at project level or above.

        Args:
            project: Project slug.
            username: Username (or email) of the user to unregister.
            application: Optional application slug to restrict the removal to.

        Returns:
            A dict with the number of removed memberships, e.g. ``{"deleted": 3}``.

        """
        try:
            uid = urllib.parse.quote(username)
            if application:
                path = f"p/{project}/a/{application}/unregister/{uid}/"
            else:
                path = f"p/{project}/unregister/{uid}/"
            response = self.transport.post(path, {})
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
        """Update an existing user in the current organization.

        Args:
            email: User email address (used as the lookup key).
            first_name: New first name.
            last_name: New last name.
            custom_fields: Optional dict of custom fields to update.
            mode: Merge mode for custom fields
                (see :class:`~bitcaster_sdk.helpers.JsonUpdateMode`).

        Returns:
            The API response dict for the updated user.

        """
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
    """Initialize the module-level client from a BAE or environment variable."""
    if bae is None:
        bae = os.environ.get("BITCASTER_BAE", "")
    bae = bae.strip()
    if not bae:
        raise ConfigurationError("Set BITCASTER_BAE environment variable")

    ctx.set(Client(bae, **kwargs))
    return ctx.get()
