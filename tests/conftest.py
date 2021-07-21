import os

import pytest
import responses

from bitcaster_sdk.client import Client
from bitcaster_sdk.sdk import Bitcaster


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


@pytest.fixture(scope='function')
def rsps_sdk():
    # yield FakeRequestsMock()
    with responses.RequestsMock() as rsps:
        payload = [{
            "name": "core",
            "id": 38,
            "slug": "core",
            "timezone": "UTC",
            "links": {
                "streams": "http://localhost:8000/api/o/bitcaster/a/38/s/",
                "home": "http://localhost:8000/o/bitcaster/a/core/"
            }
        }]
        rsps.add(rsps.GET, 'http://localhost:8000/api/system/ping/',
                 json=payload,
                 status=200)
        yield rsps


@pytest.fixture(scope='function')
def rsps_client():
    # yield FakeRequestsMock()
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture(scope='function')
def sdk_setup():
    # yield FakeRequestsMock()
    sdt = os.environ.get('BITCASTER_SDT',
                         "http://sdk-xxxxxxxxx@localhost:8000/api/o/bitcaster/a/38/"
                         )
    sdk = Bitcaster(sdt)

    with responses.RequestsMock() as rsps:
        payload = {
            "base_api": "http://localhost:8000/api/",
            "slug": "bitcaster",
            "org": "Bitcaster",

            }
        rsps.add(rsps.GET, 'http://localhost:8000/api/system/ping/',
                 json=payload,
                 status=200)
        yield rsps, sdk


@pytest.fixture(scope='function')
def client_setup():
    # yield FakeRequestsMock()
    aep = os.environ.get('BITCASTER_AEP',
                         "http://sdk-xxxxxxxxx@localhost:8000/api/o/bitcaster/a/38/"
                         )
    client = Client(aep)

    with responses.RequestsMock() as rsps:
        yield rsps, client
