#  :copyright: Copyright (c) 2018-2020. OS4D Ltd - All Rights Reserved
#  :license: Commercial
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Written by Stefano Apostolico <s.apostolico@gmail.com>, October 2020
import json
import os

from requests.exceptions import ConnectionError
import pytest
import responses

from bitcaster_sdk.client import Client
from bitcaster_sdk.sdk import Bitcaster


@pytest.fixture()
def client():
    sdt = os.environ.get('BITCASTER_SDT',
                         "http://sdk-xxxxxxxxx@localhost:8000/api/o/bitcaster/a/38/"
                         )
    return Bitcaster(sdt)


def test_init(mocked_responses, client: Bitcaster):
    mocked_responses.add(responses.GET, 'http://localhost:8000/api/system/ping/',
                         json={'base_api': 'http://localhost:8000/api/o/bitcaster/',
                               'org': 'bitcaster',
                               'slug': 'bitcaster',
                               },
                         status=200)
    client.init()
    assert client.base_url == 'http://localhost:8000/api/o/bitcaster/'


def test_list_applications(mocked_responses, client: Bitcaster):
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
    mocked_responses.add(responses.GET, 'http://localhost:8000/api/system/ping/',
                         json=payload,
                         status=200)
    res = client.filter_applications()
    assert res.status_code == 200
    assert res.json() == payload


def test_add_application(mocked_responses, client: Bitcaster):
    payload = {'id': 252,
               'links': {'home': 'http://localhost:8000/o/bitcaster/a/test_app/',
                         'streams': 'http://localhost:8000/api/o/bitcaster/a/252/s/'},
               'name': 'test_app',
               'slug': 'test_app'}
    mocked_responses.add(responses.POST, 'http://localhost:8000/o/bitcaster/a/',
                         json=payload,
                         status=201)
    res = client.create_application(admins=[1], name='test_app')
    assert res.status_code == 201, res.json()
    assert res.json() == payload


def test_remove_application(mocked_responses, client: Bitcaster):
    mocked_responses.add(responses.DELETE, 'http://localhost:8000/o/bitcaster/a/111/',
                         json={},
                         status=204)
    res = client.delete_application(111)
    assert res.status_code == 204


def test_add_member(mocked_responses, client: Bitcaster):
    payload = {
        "id": 1,
        "user": {
            "id": 1,
            "title": None,
            "name": "user1",
            "email": "a@example.com"
        },
        "role": "1",
        "links": {
            "detail": "http://localhost:8000/api/o/bitcaster/m/1/",
            "organization": "http://localhost:8000/api/o/bitcaster/",
            "addresses": "http://localhost:8000/api/o/bitcaster/m/1/a/",
            "subscriptions": "http://localhost:8000/api/o/bitcaster/m/1/s/",
            "assignment": "http://localhost:8000/api/o/bitcaster/m/1/aa/"
        },
        "extras": {}
    }
    mocked_responses.add(responses.POST, 'http://localhost:8000/o/bitcaster/a/111/',
                         json=payload,
                         status=201)
    res = client.add_member(email='a@example.com',
                            role="security",
                            name='user1')
    assert res.status_code == 201, res.json()


def test_delete_member(mocked_responses, client: Bitcaster):
    mocked_responses.add(responses.DELETE, 'http://localhost:8000/o/bitcaster/m/162/',
                         json={},
                         status=204)
    res = client.delete_member(162)
    assert res.status_code == 204


def test_add_address(mocked_responses, client: Bitcaster):
    mocked_responses.add(responses.POST, 'http://localhost:8000/o/bitcaster/m/1/a/',
                         json={},
                         status=201)
    res = client.add_address(1, label='label1', address='test1@example.com')
    assert res.status_code == 201, res.json()
    assert res.json() == {}


def test_delete_address(mocked_responses, client: Bitcaster):
    mocked_responses.add(responses.DELETE, 'http://localhost:8000/o/bitcaster/m/1/a/242/',
                         json={},
                         status=201)
    res = client.delete_address(1, 242)
    assert res.status_code == 204, res.json()


def test_create_assignment(mocked_responses, client: Bitcaster):
    mocked_responses.add(responses.POST, 'http://localhost:8000/o/bitcaster/m/1/aa/',
                         json={'id': 251,
                               'label': 'aaa',
                               'value': 'me@gexample.com',
                               'assigned_to': 'SystemEmail',
                               'user': 1,
                               'address': 11, 'channel': 'SystemEmail', 'locked': False, 'verified': False},
                         status=201)
    res = client.create_assignment(1, address=11, channel='systememail')
    assert res.status_code == 201, res.json()
