#  :copyright: Copyright (c) 2018-2020. OS4D Ltd - All Rights Reserved
#  :license: Commercial
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Written by Stefano Apostolico <s.apostolico@gmail.com>, October 2020
import json
import os
from time import sleep
from urllib.parse import urlparse

import pytest
import responses
from bitcaster_sdk.client import Client
from requests.exceptions import ConnectionError

#
# @pytest.fixture()
# def client():
#     aep = os.environ.get('BITCASTER_AEP',
#                          "http://key-xxxxxxxx@localhost:8000/api/o/bitcaster/a/38/"
#                          )
#     return Client(bae=aep, debug=True)
#
#
def test_post(client_setup):
    responses, client = client_setup
    responses.add(responses.POST,
                         'http://localhost:8000/api/o/bitcaster/a/38/s/26/trigger/',
                         json={"message": "Event triggered",
                               "stream": "bitcaster_upgraded", "development": False, "id": 71,
                               "timestamp": "2020-10-19T17:13:09.268698Z"},
                         status=201)

    res = client.send(stream=26, context={})
    assert res.status_code == 201


def test_no_answer(client_setup):
    responses, client = client_setup
    client.transport.conn = urlparse('http://sss')
    with pytest.raises(ConnectionError):
        client.send(stream=26, context={})


def test_queue(client_setup):
    responses, client = client_setup
    def request_callback(request):
        client.terminate()
        return (201, {}, json.dumps({"message": "Event triggered",
                                     "stream": "bitcaster_upgraded", "development": False, "id": 71,
                                     "timestamp": "2020-10-19T17:13:09.268698Z"}))

    responses.add_callback(
        responses.POST, 'http://localhost:8000/api/o/bitcaster/a/38/s/26/trigger/',
        callback=request_callback,
        content_type='application/json',
    )
    client.queue(stream=26, context={'a': 1})
    client.queue(stream=26, context={'a': 2})
    while not client.empty():
        sleep(1)
