from typing import TYPE_CHECKING, Any

import pytest

from bitcaster_sdk.exceptions import ConfigurationError

if TYPE_CHECKING:
    from bitcaster_sdk.client import Client


def test_trigger(client_setup, response_trigger):
    responses, client = client_setup
    url = response_trigger
    res = client.trigger("a1", context={})
    assert res == {"occurrence": 15}

    responses.add(responses.POST, url, body=ConnectionError(""))
    with pytest.raises(ConnectionError, match=""):
        client.trigger("a1", context={})


def test_ping(client_setup: tuple[Any, "Client"], monkeypatch, response_ping):
    responses, client = client_setup

    res = client.ping()
    assert res == {"token": "Key1", "slug": "core"}

    responses.add(responses.GET, f"{client.api_url}system/ping/", body=ConnectionError(""))
    with pytest.raises(ConnectionError, match=""):
        client.ping()


def test_list_events(client_setup: tuple[Any, "Client"], response_list):
    responses, client = client_setup
    url = response_list
    res = client.list_events()
    assert res[0]["active"]

    responses.add(responses.GET, url, body=ConnectionError(""))
    with pytest.raises(ConnectionError, match=""):
        client.list_events()


def test_client_parse_url(client: "Client"):
    with pytest.raises(ConfigurationError):
        assert client.parse_url("")
