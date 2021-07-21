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


def test_api(mocked_responses):
    mocked_responses.add(responses.POST, 'http://localhost:8000/api/o/bitcaster/a/38/s/26/trigger/',
                  json={"message": "Event triggered",
                        "stream": "bitcaster_upgraded", "development": False, "id": 71,
                        "timestamp": "2020-10-19T17:13:09.268698Z"},
                  status=201)

    import bitcaster_sdk

    bitcaster_sdk.init()
    from bitcaster_sdk import trigger
    trigger(26, {})
