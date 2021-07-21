

def test_api(client_setup):
    responses, __ = client_setup
    responses.add(responses.POST, 'http://localhost:8000/api/o/bitcaster/a/38/s/26/trigger/',
                         json={"message": "Event triggered",
                               "stream": "bitcaster_upgraded", "development": False, "id": 71,
                               "timestamp": "2020-10-19T17:13:09.268698Z"},
                         status=201)

    import bitcaster_sdk

    bitcaster_sdk.init()
    from bitcaster_sdk import trigger
    trigger(26, {})
