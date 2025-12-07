import os

import pytest
import responses


class FakeRequestsMock:
    fake = True

    def add_callback(self, *args, **kwargs):
        pass

    def add(self, *args, **kwargs):
        pass


class BitcasterRequestsMock:
    fake = True

    def add_callback(self, *args, **kwargs):
        pass

    def add(self, *args, **kwargs):
        pass


def pytest_configure(config):
    os.environ["BITCASTER_BAE"] = "http://key-11@app.bitcaster.io/api/o/os4d/p/bitcaster/a/bitcaster"


@pytest.fixture
def bae():
    return os.environ["BITCASTER_BAE"]


@pytest.fixture
def client(bae):
    from bitcaster_sdk import init

    return init(bae)


@pytest.fixture
def client_setup(client):
    with responses.RequestsMock() as rsps:
        yield rsps, client


@pytest.fixture
def response_ping(client_setup):
    responses, client = client_setup
    responses.add(responses.GET, f"{client.api_url}system/ping/", json={"token": "Key1", "slug": "core"})


@pytest.fixture
def response_trigger(client_setup):
    responses, client = client_setup
    url = f"{client.base_url}e/a1/trigger/"
    responses.add(responses.POST, url, json={"occurrence": 15}, status=201)
    return url


@pytest.fixture
def response_list(client_setup):
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
                "id": 1,
                "locked": False,
                "name": "Test Event #1",
                "newsletter": False,
                "slug": "test-event-1",
            },
            {
                "active": False,
                "application": 2,
                "channels": [10],
                "description": None,
                "id": 2,
                "locked": False,
                "name": "Test Event #2",
                "newsletter": False,
                "slug": "test-event-2",
            },
            {
                "active": False,
                "application": 2,
                "channels": [10],
                "description": None,
                "id": 3,
                "locked": True,
                "name": "Test Event #3",
                "newsletter": False,
                "slug": "test-event-3",
            },
        ],
    )
    return url
