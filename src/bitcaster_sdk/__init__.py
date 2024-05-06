import os
from typing import Optional

from .api import trigger, list_events
from .logging import logger

__all__ = ('trigger', 'list_events')


def init(bae: Optional[str] = None, *args, **kwargs):
    from . import client
    if not bae:
        bae = os.environ.get('BITCASTER_BAE', "")
    bae = bae.strip()
    if not bae:
        raise RuntimeError('Set BITCASTER_AEP environment variable')

    client.client = client.Client(bae, *args, **kwargs)
    return client.client
