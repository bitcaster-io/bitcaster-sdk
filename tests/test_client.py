import json
from time import sleep
from urllib.parse import urlparse

import pytest
import requests


def test_trigger(client_setup, base_url):
    responses, client = client_setup
    responses.add(
        responses.POST,
        f"{base_url}/e/pippo/trigger/",
        json={
            "message": "Event triggered",
            "stream": "bitcaster_upgraded",
            "development": False,
            "id": 71,
            "timestamp": "2020-10-19T17:13:09.268698Z",
        },
        status=201,
    )

    res = client.trigger("pippo", context={})
    assert res["message"] == "Event triggered"


def test_trigger(client_setup, base_url):
    responses, client = client_setup
    responses.add(
        responses.POST,
        f"{base_url}/e/pippo/trigger/",
        json={
            "message": "Event triggered",
            "stream": "bitcaster_upgraded",
            "development": False,
            "id": 71,
            "timestamp": "2020-10-19T17:13:09.268698Z",
        },
        status=201,
    )

    res = client.trigger("pippo", context={})
    assert res["message"] == "Event triggered"


def test_no_answer(client):
    client.transport.conn = urlparse("http://sss")
    with pytest.raises(requests.ConnectionError):
        client.send("pippo", context={})


#
# def test_queue(client_setup, base_url):
#     responses, client = client_setup
#     def request_callback(request):
#         client.terminate()
#         return (201, {}, json.dumps({"message": "Event triggered",
#                                      "stream": "bitcaster_upgraded", "development": False, "id": 71,
#                                      "timestamp": "2020-10-19T17:13:09.268698Z"}))
#
#     responses.add_callback(
#         responses.POST, f'{base_url}e/pippo/queue/',
#         callback=request_callback,
#         content_type='application/json',
#     )
#     client.queue("pippo", context={'a': 1})
#     client.queue("pippo", context={'a': 2})
#     while not client.empty():
#         sleep(1)
