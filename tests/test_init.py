import os

import bitcaster_sdk


def test_init():
    bitcaster_sdk.init("")


def test_init2():
    bitcaster_sdk.init(os.environ["BITCASTER_BAE"])
