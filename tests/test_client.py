from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

import pytest
import responses as responses_lib

from bitcaster_sdk.exceptions import ConfigurationError
from bitcaster_sdk.transport import Transport

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch
    from responses import RequestsMock

    from bitcaster_sdk.client import Client


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


def test_unregister_user(client_setup: Tuple[RequestsMock, Client]) -> None:
    responses, client = client_setup
    url = f"{client.base_url}p/myproject/a/myapp/unregister/user%40b.com/"
    responses.add(responses.POST, url, json={"deleted": 3})
    res = client.unregister_user("myproject", "myapp", "user@b.com")
    assert res == {"deleted": 3}

    responses.add(responses.POST, url, body=Exception(""))
    with pytest.raises(Exception, match=".*"):
        client.unregister_user("myproject", "myapp", "user@b.com")


def test_transport_put() -> None:
    transport = Transport("http://app.bitcaster.io/api/o/os4d/", "key-11")
    with responses_lib.RequestsMock() as rsps:
        rsps.add(responses_lib.PUT, "http://app.bitcaster.io/api/o/os4d/u/", json={"ok": True})
        resp = transport.put("u/", {"email": "a@b.com"})
        assert resp.json() == {"ok": True}


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
