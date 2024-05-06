import os
from typing import Optional

from .logging import logger


def init(bae: Optional[str] = None, *args, **kwargs):
    from . import client

    if not bae:
        bae = os.environ.get("BITCASTER_BAE", "")
    bae = bae.strip()
    if not bae:
        raise RuntimeError("Set BITCASTER_AEP environment variable")

    client.client = client.Client(bae, debug=True, *args, **kwargs)
    return client.client
