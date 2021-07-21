import os

import pytest
import responses
from bitcaster_sdk.sdk import Bitcaster

#
# @pytest.fixture()
# def client():
#     sdt = os.environ.get('BITCASTER_SDT',
#                          "http://sdk-xxxxxxxxx@localhost:8000/api/o/bitcaster/a/38/"
#                          )
#     return Bitcaster(sdt)


def test_init(sdk_setup):
    responses, client= sdk_setup
    client.init()
    assert client.base_url == 'http://localhost:8000/api/o/bitcaster/'


def test_list_applications(sdk_setup):
    responses, client = sdk_setup
    responses.add(responses.GET, 'http://localhost:8000/api/o/bitcaster/a/',
                         json=[],
                         status=200)

    res = client.filter_applications()
    assert res.status_code == 200


def test_add_application(sdk_setup):
    responses, client = sdk_setup

    payload = {'id': 252,
               'links': {'home': 'http://localhost:8000/o/bitcaster/a/test_app/',
                         'streams': 'http://localhost:8000/api/o/bitcaster/a/252/s/'},
               'name': 'test_app',
               'slug': 'test_app'}
    responses.add(responses.POST, 'http://localhost:8000/api/o/bitcaster/a/',
                         json=payload,
                         status=201)
    res = client.create_application(admins=[1], name='test_app')
    assert res.status_code == 201, res.json()
    assert res.json() == payload


def test_remove_application(sdk_setup):
    responses, client = sdk_setup

    responses.add(responses.DELETE, 'http://localhost:8000/api/o/bitcaster/a/111/',
                         json={},
                         status=204)
    res = client.delete_application(111)
    assert res.status_code == 204


def test_add_member(sdk_setup):
    responses, client = sdk_setup
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
    responses.add(responses.POST, 'http://localhost:8000/api/o/bitcaster/m/',
                         json=payload,
                         status=201)
    res = client.add_member(email='a@example.com',
                            role="security",
                            name='user1')
    assert res.status_code == 201, res.json()


def test_delete_member(sdk_setup):
    responses, client = sdk_setup
    responses.add(responses.DELETE, 'http://localhost:8000/api/o/bitcaster/m/162/',
                         json={},
                         status=204)
    res = client.delete_member(162)
    assert res.status_code == 204


def test_add_address(sdk_setup):
    responses, client = sdk_setup
    responses.add(responses.POST, 'http://localhost:8000/api/o/bitcaster/m/1/a/',
                         json={},
                         status=201)
    res = client.add_address(1, label='label1', address='test1@example.com')
    assert res.status_code == 201, res.json()
    assert res.json() == {}


def test_delete_address(sdk_setup):
    responses, client = sdk_setup
    responses.add(responses.DELETE, 'http://localhost:8000/api/o/bitcaster/m/1/a/242/',
                         json={},
                         status=204)
    res = client.delete_address(1, 242)
    assert res.status_code == 204, res.json()


def test_create_assignment(sdk_setup):
    responses, client = sdk_setup
    responses.add(responses.POST, 'http://localhost:8000/api/o/bitcaster/m/1/aa/',
                         json={'id': 251,
                               'label': 'aaa',
                               'value': 'me@gexample.com',
                               'assigned_to': 'SystemEmail',
                               'user': 1,
                               'address': 11, 'channel': 'SystemEmail', 'locked': False, 'verified': False},
                         status=201)
    res = client.create_assignment(1, address=11, channel='systememail')
    assert res.status_code == 201, res.json()
