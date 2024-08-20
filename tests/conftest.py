import os
from typing import Tuple

import pytest
import responses
from responses import RequestsMock

from bitcaster_sdk.client import Client


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
    os.environ["BITCASTER_BAE"] = "http://key-11@app.bitcaster.io/api/o/os4d/"
    # os.environ["BITCASTER_BAE"] = "http://key-11@app.bitcaster.io/api/o/os4d/p/bitcaster/a/bitcaster"
    # os.environ["BITCASTER_BAE"] = "http://796863862936@localhost:8000/api/o/unicef/p/hope/a/core"


@pytest.fixture(scope="function")
def bae():
    return os.environ["BITCASTER_BAE"]


@pytest.fixture(scope="function")
def client(bae: str) -> Client:
    from bitcaster_sdk import init

    return init(bae)


@pytest.fixture(scope="function")
def client_setup(client):
    # yield MagicMock(), client
    with responses.RequestsMock() as rsps:
        yield rsps, client


@pytest.fixture(scope="function")
def response_ping(client_setup: Tuple[RequestsMock, Client]):
    responses, client = client_setup
    responses.add(responses.GET, f"{client.api_url}system/ping/", json={"token": "Key1", "slug": "core"})
    yield


@pytest.fixture(scope="function")
def response_trigger(client_setup: Tuple[RequestsMock, Client]):
    responses, client = client_setup
    url = f"{client.base_url}p/bitcaster/a/bitcaster/e/a1/trigger/"
    responses.add(responses.POST, url, json={"occurrence": 15}, status=201)
    yield url


@pytest.fixture(scope="function")
def response_events(client_setup: Tuple[RequestsMock, Client]):
    responses, client = client_setup
    url = f"{client.base_url}p/bitcaster/a/bitcaster/e/"
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
    yield url


@pytest.fixture(scope="function")
def response_lists(client_setup: Tuple[RequestsMock, Client]):
    responses, client = client_setup
    url = f"{client.base_url}p/bitcaster/d/"
    responses.add(
        responses.GET,
        url,
        json=[{"name": "Dis1", "id": 2, "members": "http://localhost:8000/api/o/local/p/project1/d/2/m/"}],
    )
    yield url


@pytest.fixture(scope="function")
def response_members(client_setup: Tuple[RequestsMock, Client]):
    responses, client = client_setup
    url = f"{client.base_url}p/bitcaster/d/1/m/"
    responses.add(
        responses.GET,
        url,
        json=[
            {
                "id": 1,
                "address": "user1@example.com",
                "user": "user1@example.com",
                "channel": "BitcasterLog",
                "active": True,
            }
        ],
    )
    yield url


@pytest.fixture(scope="function")
def response_users(client_setup: Tuple[RequestsMock, Client]):
    responses, client = client_setup
    url = f"{client.base_url}u/"
    responses.add(
        responses.GET,
        url,
        json=[
            {
                "id": 1,
                "email": "user1@example.com",
                "username": "user1@example.com",
                "locked": False,
                "version": 1723969808195040,
                "last_updated": "2024-08-18T08:45:54.879847Z",
                "first_name": "",
                "last_name": "",
                "is_active": True,
                "custom_fields": {},
            },
            {
                "id": 2,
                "email": "user2@example.com",
                "username": "user2@example.com",
                "locked": True,
                "version": 1723969808195040,
                "last_updated": "2024-08-18T08:45:54.879847Z",
                "first_name": "",
                "last_name": "",
                "is_active": True,
                "custom_fields": {},
            },
            {
                "id": 3,
                "email": "user3@example.com",
                "username": "user3@example.com",
                "locked": False,
                "version": 1723969808195040,
                "last_updated": "2024-08-18T08:45:54.879847Z",
                "first_name": "",
                "last_name": "",
                "is_active": False,
                "custom_fields": {},
            },
        ],
    )
    yield url
