import os
from typing import Tuple

import pytest
from responses import RequestsMock

from bitcaster_sdk.client import Client
from bitcaster_sdk.exceptions import ConfigurationError


def test_trigger(client_setup: Tuple[RequestsMock, Client], response_trigger: str) -> None:
    import bitcaster_sdk

    bitcaster_sdk.trigger("bitcaster", "bitcaster", "a1")


#
@pytest.mark.parametrize("bae", ["", "aa", "ftp://example.com", "https://example.com"])
def test_init_error(bae: str) -> None:
    import bitcaster_sdk

    with pytest.raises(ConfigurationError):
        bitcaster_sdk.init(bae)


@pytest.mark.parametrize(
    "bae",
    [
        None,
        "https://token@example.com/api/o/ORG/",
        "https://token@example.com/api/o/ORG",
        "https://token@example.com/api/o/ORG///",
        os.environ["BITCASTER_BAE"],
    ],
)
def test_init_success(bae: str) -> None:
    import bitcaster_sdk

    bitcaster_sdk.init(bae)
