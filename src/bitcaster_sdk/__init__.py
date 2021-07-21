import os

from . import client
from .api import trigger
from .logging import logger

__all__ = ('trigger', 'logger')


def init(*args, **kwargs):
    bae = os.environ.get('BITCASTER_AEP')
    client.client = client.Client(bae, *args, **kwargs)
    return client.client
