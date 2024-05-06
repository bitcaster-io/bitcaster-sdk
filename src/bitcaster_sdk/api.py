from typing import Optional

from . import client


def trigger(event: str, context: Optional[dict[str, str]] = None, ):
    return client.client.trigger(event, context)


def list_events():
    return client.client.list_events()


def ping():
    return client.client.ping()


del client