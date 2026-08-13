from __future__ import annotations

import json
import sys
from types import SimpleNamespace
from urllib.parse import urlparse

import pytest

from bitcaster_sdk.exceptions import ConfigurationError
from bitcaster_sdk.rabbit_client import RabbitClient

AMQP_URL = "amqp://bitcaster:secret@localhost:5672/vhost"


class FakeParameters:
    def __init__(self, url: str) -> None:
        p = urlparse(url)
        self.host = p.hostname or "localhost"
        self.port = p.port or 5672
        self.virtual_host = p.path.strip("/") or "/"
        self.username = p.username or ""
        self.password = p.password or ""
        self.original = url

    def __str__(self) -> str:
        return self.original


class FakeChannel:
    def __init__(self) -> None:
        self.declared: list[tuple[str, bool]] = []
        self.bound: list[tuple[str, str, str]] = []
        self.published: list[tuple[str, str, str, object]] = []
        self.fail_publish = False

    def queue_declare(self, queue: str, durable: bool = False, **kwargs: object) -> object:
        self.declared.append((queue, durable))
        return SimpleNamespace()

    def queue_bind(self, queue: str, exchange: str, routing_key: str) -> None:
        self.bound.append((queue, exchange, routing_key))

    def basic_publish(self, exchange: str, routing_key: str, body: str, properties: object | None = None) -> None:
        if self.fail_publish:
            raise RuntimeError("connection lost")
        self.published.append((exchange, routing_key, body, properties))


class FakeConnection:
    def __init__(self, pika: FakePika, params: FakeParameters) -> None:
        self.pika = pika
        self.params = params
        self.closed = False

    def channel(self) -> FakeChannel:
        channel = FakeChannel()
        self.pika.channels.append(channel)
        return channel

    def close(self) -> None:
        self.closed = True


class FakePika:
    def __init__(self) -> None:
        self.parameters: list[FakeParameters] = []
        self.channels: list[FakeChannel] = []
        self.connections: list[FakeConnection] = []

    def URLParameters(self, url: str) -> FakeParameters:  # noqa: N802
        params = FakeParameters(url)
        self.parameters.append(params)
        return params

    def BlockingConnection(self, params: FakeParameters) -> FakeConnection:  # noqa: N802
        connection = FakeConnection(self, params)
        self.connections.append(connection)
        return connection

    def BasicProperties(self, delivery_mode: int = 1) -> SimpleNamespace:  # noqa: N802
        return SimpleNamespace(delivery_mode=delivery_mode)


@pytest.fixture
def fake_pika(monkeypatch: pytest.MonkeyPatch) -> FakePika:
    fake = FakePika()
    monkeypatch.setitem(sys.modules, "pika", fake)
    return fake


def test_constructor_parses_amqp_url(fake_pika: FakePika) -> None:
    client = RabbitClient(AMQP_URL, queue="bitcaster-events")

    params = fake_pika.parameters[-1]
    assert params.host == "localhost"
    assert params.port == 5672
    assert params.virtual_host == "vhost"
    assert params.username == "bitcaster"
    assert params.password == "secret"
    assert client.queue == "bitcaster-events"
    assert client.event_field == "event"
    assert client.last_called_url == AMQP_URL


def test_trigger_event_publishes_agent_compatible_message(fake_pika: FakePika) -> None:
    client = RabbitClient(AMQP_URL, queue="bitcaster-events")
    client.set_domain("bitcaster", "bitcaster")

    result = client.trigger_event("a1", context={"foo": "bar"})

    channel = fake_pika.channels[-1]
    assert channel.declared == [("bitcaster-events", True)]
    assert channel.bound == []
    exchange, routing_key, body, properties = channel.published[-1]
    assert exchange == ""
    assert routing_key == "bitcaster-events"
    assert json.loads(body) == {"event": "a1", "data": {"foo": "bar"}}
    assert properties.delivery_mode == 2
    assert result == {"published": True, "event": "a1", "queue": "bitcaster-events", "exchange": ""}


def test_queue_bind_when_exchange_configured(fake_pika: FakePika) -> None:
    client = RabbitClient(AMQP_URL, queue="q", exchange="events_exchange", routing_key="rk")
    client.set_domain("bitcaster", "bitcaster")

    client.trigger_event("a1", context={})

    channel = fake_pika.channels[-1]
    assert channel.bound == [("q", "events_exchange", "rk")]
    exchange, _routing_key, _body, _properties = channel.published[-1]
    assert exchange == "events_exchange"


def test_custom_event_field(fake_pika: FakePika) -> None:
    client = RabbitClient(AMQP_URL, queue="q", event_field="slug")
    client.set_domain("bitcaster", "bitcaster")

    client.trigger_event("a1", context={"foo": "bar"})

    channel = fake_pika.channels[-1]
    _exchange, _routing_key, body, _properties = channel.published[-1]
    assert json.loads(body) == {"slug": "a1", "data": {"foo": "bar"}}


def test_trigger_event_requires_domain(fake_pika: FakePika) -> None:
    client = RabbitClient(AMQP_URL, queue="q")

    with pytest.raises(ConfigurationError, match="set_domain"):
        client.trigger_event("a1", context={})


def test_trigger_publishes_with_explicit_domain(fake_pika: FakePika) -> None:
    client = RabbitClient(AMQP_URL, queue="q")

    with pytest.warns(DeprecationWarning, match="deprecated"):
        client.trigger("bitcaster", "bitcaster", "a1", context={"foo": "bar"})

    channel = fake_pika.channels[-1]
    _exchange, _routing_key, body, _properties = channel.published[-1]
    assert json.loads(body) == {"event": "a1", "data": {"foo": "bar"}}


def test_ping_reports_connection_info(fake_pika: FakePika) -> None:
    client = RabbitClient(AMQP_URL, queue="q")

    result = client.ping()

    assert result["connected"] is True
    assert result["host"] == "localhost"
    assert result["port"] == 5672
    assert result["virtual_host"] == "vhost"
    assert result["queue"] == "q"
    assert fake_pika.connections[-1].closed is True


def test_http_only_methods_not_supported(fake_pika: FakePika) -> None:
    client = RabbitClient(AMQP_URL, queue="q")

    with pytest.raises(NotImplementedError):
        client.list_events("bitcaster", "bitcaster")
    with pytest.raises(NotImplementedError):
        client.list_users()
    with pytest.raises(NotImplementedError):
        client.list_distribution_lists("bitcaster")
    with pytest.raises(NotImplementedError):
        client.list_projects()
    with pytest.raises(NotImplementedError):
        client.list_applications("bitcaster")
    with pytest.raises(NotImplementedError):
        client.list_members("bitcaster", "dl1")
    with pytest.raises(NotImplementedError):
        client.add_user("user@example.com", "First", "Last")
    with pytest.raises(NotImplementedError):
        client.update_user("user@example.com", "First", "Last")
    with pytest.raises(NotImplementedError):
        client.register_user("bitcaster", "bitcaster", "user1")
    with pytest.raises(NotImplementedError):
        client.unregister_user("bitcaster", "bitcaster", "user1")


def test_trigger_raises_connection_error_on_publish_failure(fake_pika: FakePika) -> None:
    client = RabbitClient(AMQP_URL, queue="q")
    client.set_domain("bitcaster", "bitcaster")
    fake_pika.channels.append(FakeChannel())

    def failing_channel(*_args: object, **kwargs: object) -> FakeChannel:
        channel = FakeChannel()
        channel.fail_publish = True
        return channel

    client._channel = failing_channel  # type: ignore[method-assign]

    with pytest.raises(ConnectionError, match="Failed to publish"):
        client.trigger_event("a1", context={"foo": "bar"})


def test_missing_pika_raises_configuration_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "pika", None)

    with pytest.raises(ConfigurationError, match="bitcaster-sdk\\[amqp\\]"):
        RabbitClient(AMQP_URL, queue="q")
