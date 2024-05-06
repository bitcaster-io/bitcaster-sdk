import os
from typing import Optional

from .client import client
# from .logging import logger
#
# __all__ = ('trigger', 'logger')
#
#
# def init(bae: Optional[str] = None, *args, **kwargs):
#     if not bae:
#         bae = os.environ.get('BITCASTER_BAE', "")
#     bae = bae.strip()
#     if not bae:
#         raise RuntimeError('Set BITCASTER_AEP environment variable')
#
#     client.client = client.Client(bae, *args, **kwargs)
#     return client.client
