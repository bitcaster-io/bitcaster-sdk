import os
from unittest.mock import MagicMock
from urllib.parse import urlparse, urlsplit

import pytest
import responses

import bitcaster_sdk


# from bitcaster_sdk.client import Client
# from bitcaster_sdk.sdk import Bitcaster


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
    # os.environ["BITCASTER_BAE"] = "http://key-1@app.bitcaster.io/api/o/os4d/p/bitcaster/a/bitcaster"
    os.environ["BITCASTER_BAE"] = "http://796863862936@localhost:8000/api/o/unicef/p/hope/a/core"


@pytest.fixture(scope="function")
def bae():
    return os.environ["BITCASTER_BAE"]


@pytest.fixture(scope="function")
def client(bae):
    from bitcaster_sdk.client import Client

    return Client(bae)


@pytest.fixture(scope="function")
def client_setup(client):
    # yield MagicMock(), client
    with responses.RequestsMock() as rsps:
        yield rsps, client
