import pytest
from typing import TYPE_CHECKING

from bitcaster_sdk.exceptions import ConfigurationError

if TYPE_CHECKING:
    from bitcaster_sdk.client import Client


def test_trigger(client_setup):
    responses, client = client_setup
    url = f"{client.base_url}e/a1/trigger/"
    responses.add(
        responses.POST,
        url,
        json={"occurrence": 15},
        status=201,
    )
    res = client.trigger("a1", context={})
    assert res == {"occurrence": 15}

    responses.add(responses.POST, url, body=Exception(""))
    with pytest.raises(Exception):
        client.trigger("a1", context={})


def test_ping(client_setup: "[Any, Client]", monkeypatch):
    responses, client = client_setup
    responses.add(responses.GET, f"{client.api_url}system/ping/", json={"token": "Key1", "slug": "core"})

    res = client.ping()
    assert res == {"token": "Key1", "slug": "core"}

    responses.add(responses.GET, f"{client.api_url}system/ping/", body=Exception(""))
    with pytest.raises(Exception):
        client.ping()


def test_list_events(client_setup: "[Any, Client]"):
    responses, client = client_setup
    url = f"{client.base_url}e/"
    responses.add(
        responses.GET,
        url,
        json=[
            {
                "active": True,
                "application": 2,
                "channels": [10],
                "description": None,
                "id": 9,
                "locked": False,
                "name": "Test Event",
                "newsletter": False,
                "slug": "test-event",
            }
        ],
    )

    res = client.list_events()
    assert res[0]["active"]

    responses.add(responses.GET, url, body=Exception(""))
    with pytest.raises(Exception):
        client.list_events()


def test_client_parse_url(client: "Client"):
    with pytest.raises(ConfigurationError):
        assert client.parse_url("")
