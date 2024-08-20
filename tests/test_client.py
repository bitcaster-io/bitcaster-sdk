from typing import TYPE_CHECKING, Tuple

import pytest
from responses import RequestsMock

from bitcaster_sdk.client import Client
from bitcaster_sdk.exceptions import ConfigurationError

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


def test_trigger(client_setup: Tuple[RequestsMock, Client], response_trigger: str) -> None:
    responses, client = client_setup
    url = response_trigger
    res = client.trigger("bitcaster", "bitcaster", "a1", context={})
    assert res == {"occurrence": 15}

    responses.add(responses.POST, url, body=Exception(""))
    with pytest.raises(Exception):
        client.trigger("bitcaster", "bitcaster", "a1", context={})


def test_ping(client_setup: Tuple[RequestsMock, Client], monkeypatch: "MonkeyPatch", response_ping: str) -> None:
    responses, client = client_setup

    res = client.ping()
    assert res == {"token": "Key1", "slug": "core"}

    responses.add(responses.GET, f"{client.api_url}system/ping/", body=Exception(""))
    with pytest.raises(Exception):
        client.ping()


def test_list_events(client_setup: Tuple[RequestsMock, Client], response_events: str) -> None:
    responses, client = client_setup
    url = response_events
    res = client.list_events("bitcaster", "bitcaster")
    assert res[0]["active"]

    responses.add(responses.GET, url, body=Exception(""))
    with pytest.raises(Exception):
        client.list_events("bitcaster", "bitcaster")


def test_client_parse_url(client: "Client") -> None:
    with pytest.raises(ConfigurationError):
        client.parse_url("")
