from . import client


def trigger(stream: int, arguments: dict = None):
    client.client.queue(stream, arguments)

