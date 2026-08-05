from __future__ import annotations

import sys
from types import SimpleNamespace
from typing import TYPE_CHECKING, Tuple
from urllib.parse import urlparse

import pytest
import responses as responses_lib
from requests.exceptions import ReadTimeout

from bitcaster_sdk.client import Client
from bitcaster_sdk.exceptions import ConfigurationError
from bitcaster_sdk.transport import Transport

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch
    from responses import RequestsMock


def test_trigger(client_setup: Tuple[RequestsMock, Client], response_trigger: str) -> None:
    responses, client = client_setup
    url = response_trigger
    res = client.trigger("bitcaster", "bitcaster", "a1", context={})
    assert res == {"occurrence": 15}

    responses.add(responses.POST, url, body=Exception(""))
    with pytest.raises(Exception, match=".*"):
        client.trigger("bitcaster", "bitcaster", "a1", context={})


def test_cid_trigger(client_setup, response_cid_trigger):
    responses, client = client_setup
    res = client.trigger("bitcaster", "bitcaster", "a1", context={}, cid="b73c34d3-bb28-4389-86f3-aaabc7606474")
    assert res == {"occurrence": 15}


def test_ping(client_setup: Tuple[RequestsMock, Client], monkeypatch: "MonkeyPatch", response_ping: str) -> None:
    responses, client = client_setup

    res = client.ping()
    assert res == {"token": "Key1", "slug": "core"}

    responses.add(responses.GET, f"{client.api_url}system/ping/", body=Exception(""))
    with pytest.raises(Exception, match=".*"):
        client.ping()


def test_list_events(client_setup: Tuple[RequestsMock, Client], response_events: str) -> None:
    responses, client = client_setup
    url = response_events
    res = client.list_events("bitcaster", "bitcaster")
    assert res[0]["active"]

    responses.add(responses.GET, url, body=Exception(""))
    with pytest.raises(Exception, match=".*"):
        client.list_events("bitcaster", "bitcaster")


def test_client_parse_url(client: "Client") -> None:
    with pytest.raises(ConfigurationError):
        client.parse_url("")


def test_client_configures_transport_timeout(bae: str) -> None:
    client = Client(bae, timeout=7)

    assert client.transport is not None
    assert client.transport.timeout == 7


def test_trigger_passes_timeout_to_request(bae: str) -> None:
    client = Client(bae, timeout=7)
    url = f"{client.base_url}p/bitcaster/a/bitcaster/e/a1/trigger/"
    client.set_domain("bitcaster", "bitcaster")

    with responses_lib.RequestsMock() as rsps:
        rsps.add(responses_lib.POST, url, json={"occurrence": 15}, status=201)
        result = client.trigger_event("a1", context={})

        assert result == {"occurrence": 15}
        assert rsps.calls[0].request.req_kwargs["timeout"] == 7


def test_ping_passes_timeout_to_request(bae: str) -> None:
    client = Client(bae, timeout=7)

    with responses_lib.RequestsMock() as rsps:
        rsps.add(responses_lib.GET, f"{client.api_url}system/ping/", json={"token": "Key1", "slug": "core"})

        assert client.ping() == {"token": "Key1", "slug": "core"}
        assert rsps.calls[0].request.req_kwargs["timeout"] == 7


def test_default_timeout_preserves_requests_behavior(bae: str) -> None:
    client = Client(bae)

    with responses_lib.RequestsMock() as rsps:
        rsps.add(responses_lib.GET, f"{client.api_url}system/ping/", json={"token": "Key1", "slug": "core"})

        assert client.ping() == {"token": "Key1", "slug": "core"}
        assert rsps.calls[0].request.req_kwargs["timeout"] is None


def test_ping_maps_request_timeout_to_connection_error(bae: str) -> None:
    client = Client(bae, timeout=7)

    with responses_lib.RequestsMock() as rsps:
        rsps.add(responses_lib.GET, f"{client.api_url}system/ping/", body=ReadTimeout("timed out"))

        with pytest.raises(ConnectionError, match="Connection Error"):
            client.ping()


def test_list_users(client_setup: Tuple[RequestsMock, Client], response_users: str) -> None:
    responses, client = client_setup
    res = client.list_users()
    assert len(res) == 3

    responses.add(responses.GET, f"{client.base_url}u/", body=Exception(""))
    with pytest.raises(Exception, match=".*"):
        client.list_users()


def test_list_projects(client_setup: Tuple[RequestsMock, Client]) -> None:
    responses, client = client_setup
    url = f"{client.base_url}p/"
    responses.add(responses.GET, url, json=[{"slug": "proj1"}])
    res = client.list_projects()
    assert res == [{"slug": "proj1"}]

    responses.add(responses.GET, url, body=Exception(""))
    with pytest.raises(Exception, match=".*"):
        client.list_projects()


def test_list_applications(client_setup: Tuple[RequestsMock, Client]) -> None:
    responses, client = client_setup
    url = f"{client.base_url}p/myapp/a/"
    responses.add(responses.GET, url, json=[{"slug": "app1"}])
    res = client.list_applications("myapp")
    assert res == [{"slug": "app1"}]

    responses.add(responses.GET, url, body=Exception(""))
    with pytest.raises(Exception, match=".*"):
        client.list_applications("myapp")


def test_list_distribution_lists(client_setup: Tuple[RequestsMock, Client]) -> None:
    responses, client = client_setup
    url = f"{client.base_url}p/myproject/d/"
    responses.add(responses.GET, url, json=[{"name": "Dis1"}])
    res = client.list_distribution_lists("myproject")
    assert res == [{"name": "Dis1"}]

    responses.add(responses.GET, url, body=Exception(""))
    with pytest.raises(Exception, match=".*"):
        client.list_distribution_lists("myproject")


def test_list_members(client_setup: Tuple[RequestsMock, Client]) -> None:
    responses, client = client_setup
    url = f"{client.base_url}p/myproject/d/1/m/"
    responses.add(responses.GET, url, json=[{"id": 1}])
    res = client.list_members("myproject", "1")
    assert res == [{"id": 1}]

    responses.add(responses.GET, url, body=Exception(""))
    with pytest.raises(Exception, match=".*"):
        client.list_members("myproject", "1")


def test_add_user(client_setup: Tuple[RequestsMock, Client]) -> None:
    responses, client = client_setup
    url = f"{client.base_url}u/"
    responses.add(responses.POST, url, json={"email": "new@b.com"}, status=201)
    res = client.add_user("new@b.com", "First", "Last")
    assert res == {"email": "new@b.com"}

    responses.add(responses.POST, url, body=Exception(""))
    with pytest.raises(Exception, match=".*"):
        client.add_user("new@b.com", "First", "Last")


def test_update_user(client_setup: Tuple[RequestsMock, Client]) -> None:
    responses, client = client_setup
    url = f"{client.base_url}u/new%40b.com/"
    responses.add(responses.PATCH, url, json={"email": "new@b.com", "first_name": "Updated"})
    res = client.update_user("new@b.com", "Updated", "")
    assert res["first_name"] == "Updated"

    responses.add(responses.PATCH, url, body=Exception(""))
    with pytest.raises(Exception, match=".*"):
        client.update_user("new@b.com", "Updated", "")


def test_transport_put() -> None:
    transport = Transport("http://app.bitcaster.io/api/o/os4d/", "key-11", timeout=7)
    with responses_lib.RequestsMock() as rsps:
        rsps.add(responses_lib.PUT, "http://app.bitcaster.io/api/o/os4d/u/", json={"ok": True})
        resp = transport.put("u/", {"email": "a@b.com"})
        assert resp.json() == {"ok": True}
        assert rsps.calls[0].request.req_kwargs["timeout"] == 7


class TestDomain:
    def test_set_domain(self, client: Client) -> None:
        client.set_domain("my-project", "my-app")
        assert client.project == "my-project"
        assert client.application == "my-app"

    def test_trigger_event(self, client_setup: Tuple[RequestsMock, Client], response_trigger: str) -> None:
        responses, client = client_setup
        client.set_domain("bitcaster", "bitcaster")
        res = client.trigger_event("a1", context={})
        assert res == {"occurrence": 15}

    def test_trigger_event_no_domain(self, client: Client) -> None:
        with pytest.raises(ConfigurationError, match="set_domain"):
            client.trigger_event("a1")

    def test_trigger_event_uses_latest_domain(self, client_setup: Tuple[RequestsMock, Client]) -> None:
        responses, client = client_setup
        url = f"{client.base_url}p/other-project/a/other-app/e/ev/trigger/"
        responses.add(responses_lib.POST, url, json={"occurrence": 7}, status=201)
        client.set_domain("other-project", "other-app")
        res = client.trigger_event("ev", context={})
        assert res == {"occurrence": 7}

    def test_trigger_deprecated(self, client_setup: Tuple[RequestsMock, Client], response_trigger: str) -> None:
        responses, client = client_setup
        with pytest.warns(DeprecationWarning):
            res = client.trigger("bitcaster", "bitcaster", "a1", context={})
            assert res == {"occurrence": 15}


class _FakeParams:
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


class _FakeChan:
    published: list[tuple[str, str, str, object]] = []

    def queue_declare(self, queue: str, durable: bool = False, **kwargs: object) -> object:
        return SimpleNamespace()

    def queue_bind(self, queue: str, exchange: str, routing_key: str) -> None:
        pass

    def basic_publish(self, exchange: str, routing_key: str, body: str, properties: object | None = None) -> None:
        self.published.append((exchange, routing_key, body, properties))


class _FakeConn:
    def __init__(self, pika: object, params: _FakeParams) -> None:
        self.params = params
        self.closed = False

    def channel(self) -> _FakeChan:
        return _FakeChan()

    def close(self) -> None:
        self.closed = True


class _FakePika:
    def URLParameters(self, url: str) -> _FakeParams:  # noqa: N802
        return _FakeParams(url)

    def BlockingConnection(self, params: _FakeParams) -> _FakeConn:  # noqa: N802
        return _FakeConn(self, params)

    def BasicProperties(self, delivery_mode: int = 1) -> SimpleNamespace:  # noqa: N802
        return SimpleNamespace(delivery_mode=delivery_mode)


def test_init_with_amqp_bae(monkeypatch: pytest.MonkeyPatch) -> None:
    """init() creates RabbitClient when BAE starts with amqp://."""
    monkeypatch.setitem(sys.modules, "pika", _FakePika())
    from bitcaster_sdk import init

    client = init("amqp://user:pass@localhost:5672/", project="p1", application="a1")
    assert client.__class__.__name__ == "RabbitClient"
    assert client.project == "p1"
    assert client.application == "a1"
    assert client.queue == "bitcaster"

    # verify module-level convenience functions work
    from bitcaster_sdk import trigger_event, set_domain

    set_domain("p1", "a1")
    trigger_event("ev", context={"k": "v"})
