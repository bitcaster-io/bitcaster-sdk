"""Bitcaster SDK - RabbitMQ publishing client.

Publishes events to a RabbitMQ queue in a format compatible with the
Bitcaster ``AgentAMQP`` monitor agent
(``bitcaster.agents.amqp``): a JSON message where the event slug is
stored under ``event_field`` (default ``"event"``) and the event context
under ``"data"``.
"""

from __future__ import annotations

import json
import warnings
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Iterator

from bitcaster_sdk.exceptions import ConfigurationError

from .abstract_client import AbstractClient
from .log import logger

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection

__all__ = ["RabbitClient"]


class RabbitClient(AbstractClient):
    """Publish events to a RabbitMQ queue for consumption by Bitcaster AgentAMQP.

    The client connects to RabbitMQ (an ``amqp://`` URL in the style of
    ``amqp://<user>:<password>@<host>:<port>/<virtual_host>``), declares a
    durable queue (bound to an exchange when configured) and publishes each
    event as a JSON message: ``{<event_field>: <event>, "data": <context>}``.

    The Bitcaster AMQP agent resolves the event against the application of
    its monitor, so messages carry no project/application information; use
    :meth:`~bitcaster_sdk.abstract_client.AbstractClient.set_domain` to bind
    this client to the application owning the events.

    Requires the ``pika`` package (install ``bitcaster-sdk[amqp]``).
    """

    def __init__(
        self,
        url: str,
        queue: str = "bitcaster",
        exchange: str = "",
        routing_key: str = "",
        event_field: str = "event",
        project: str | None = None,
        application: str | None = None,
        debug: bool = False,
    ) -> None:
        """Initialize the RabbitMQ client.

        Args:
            url: AMQP connection URL (``amqp://user:password@host:port/virtual_host``).
            queue: Name of the queue to publish to.
            exchange: Optional exchange to bind the queue to.
            routing_key: Routing key used when binding the queue.
            event_field: JSON field name that holds the event slug
                (must match the agent's ``event_field`` config).
            project: Default project slug for :meth:`trigger_event`.
            application: Default application slug for :meth:`trigger_event`.
            debug: Enable debug logging.

        """
        super().__init__(project=project, application=application, debug=debug)
        pika = self._pika()
        self.connection_params = pika.URLParameters(url)
        self.queue = queue
        self.exchange = exchange or ""
        self.routing_key = routing_key or ""
        self.event_field = event_field or "event"
        self.options["url"] = url

    @staticmethod
    def _pika() -> Any:
        try:
            import pika  # noqa: PLC0415
        except ImportError as e:
            raise ConfigurationError(
                "The pika package is required for RabbitClient. Install it with: pip install 'bitcaster-sdk[amqp]'"
            ) from e
        return pika

    @contextmanager
    def _connection(self) -> Iterator["BlockingConnection"]:
        pika = self._pika()
        connection: "BlockingConnection" = pika.BlockingConnection(self.connection_params)
        try:
            yield connection
        finally:
            connection.close()

    @contextmanager
    def _channel(self) -> Iterator["BlockingChannel"]:
        with self._connection() as connection:
            channel: "BlockingChannel" = connection.channel()
            yield channel

    def _ensure_queue(self, channel: "BlockingChannel") -> None:
        channel.queue_declare(queue=self.queue, durable=True)
        if self.exchange:
            channel.queue_bind(queue=self.queue, exchange=self.exchange, routing_key=self.routing_key)

    @property
    def last_called_url(self) -> str:
        """The AMQP URL the client publishes to."""
        return str(self.connection_params)

    def ping(self) -> dict[str, Any]:
        """Check connectivity with the RabbitMQ server.

        Returns:
            A dict identifying the server and the configured queue.

        """
        with self._connection() as connection:
            return {
                "connected": True,
                "host": connection.params.host,
                "port": connection.params.port,
                "virtual_host": connection.params.virtual_host,
                "queue": self.queue,
                "exchange": self.exchange,
            }

    def trigger(
        self,
        project: str,
        application: str,
        event: str,
        context: dict[str, str] | None = None,
        options: dict[str, str] | None = None,
        cid: str | None = None,
    ) -> dict[str, Any]:
        """Publish an event to the RabbitMQ queue.

        Use :meth:`set_domain` + :meth:`trigger_event` instead.

        Args:
            project: Project slug (informational, not part of the message).
            application: Application slug (informational, not part of the message).
            event: Event slug.
            context: Key/value pairs to include as event context.
            options: Key/value pairs for additional event options (not
                supported by the AMQP agent, ignored).
            cid: Optional correlation ID (not supported by the AMQP agent, ignored).

        Returns:
            A dict describing the published message.

        """
        warnings.warn(
            "trigger() is deprecated, use trigger_event() with set_domain() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        del options, cid
        body = json.dumps({self.event_field: event, "data": context or {}})
        logger.debug("Publishing event '%s' to queue '%s'", event, self.queue)
        try:
            with self._channel() as channel:
                self._ensure_queue(channel)
                channel.basic_publish(
                    exchange=self.exchange,
                    routing_key=self.queue,
                    body=body,
                    properties=self._pika().BasicProperties(delivery_mode=2),
                )
        except Exception as e:
            logger.exception("Failed to publish event '%s'", event)
            raise ConnectionError(f"Failed to publish event to RabbitMQ: {e}") from e
        return {"published": True, "event": event, "queue": self.queue, "exchange": self.exchange}

    # ---- HTTP-only API, not available for a queue publisher ---------------

    def list_events(self, project: str, application: str) -> Any:
        raise NotImplementedError("RabbitClient only publishes events; use the HTTP Client to list events")

    def list_users(self) -> Any:
        raise NotImplementedError("RabbitClient only publishes events; use the HTTP Client to list users")

    def list_distribution_lists(self, project: str) -> Any:
        raise NotImplementedError("RabbitClient only publishes events; use the HTTP Client to list distribution lists")

    def list_projects(self) -> Any:
        raise NotImplementedError("RabbitClient only publishes events; use the HTTP Client to list projects")

    def list_applications(self, project: str) -> Any:
        raise NotImplementedError("RabbitClient only publishes events; use the HTTP Client to list applications")

    def list_members(self, project: str, distribution_list: str) -> Any:
        raise NotImplementedError("RabbitClient only publishes events; use the HTTP Client to list members")

    def add_user(self, email: str, first_name: str, last_name: str, custom: Any = None) -> Any:
        raise NotImplementedError("RabbitClient only publishes events; use the HTTP Client to add users")

    def update_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        custom_fields: Any = None,
        mode: str = "ignore",
    ) -> Any:
        raise NotImplementedError("RabbitClient only publishes events; use the HTTP Client to update users")

    def register_user(
        self,
        project: str,
        application: str,
        username: str,
        first_name: str = "",
        last_name: str = "",
        email: str = "",
        custom_fields: Any = None,
        active: bool = True,
        addresses: Any = None,
        distribution_list: str | None = None,
    ) -> Any:
        raise NotImplementedError("RabbitClient only publishes events; use the HTTP Client to register users")

    def unregister_user(self, project: str, application: str, username: str) -> Any:
        raise NotImplementedError("RabbitClient only publishes events; use the HTTP Client to unregister users")
