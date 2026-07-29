from __future__ import annotations

import os
from typing import TYPE_CHECKING, Tuple

import pytest

from bitcaster_sdk.exceptions import ConfigurationError

if TYPE_CHECKING:
    from responses import RequestsMock

    from bitcaster_sdk.client import Client


def test_trigger(client_setup: Tuple[RequestsMock, Client], response_trigger: str) -> None:
    import bitcaster_sdk

    bitcaster_sdk.trigger("bitcaster", "bitcaster", "a1")


def test_list_projects(client_setup: Tuple[RequestsMock, Client]) -> None:
    import bitcaster_sdk

    responses, client = client_setup
    url = f"{client.base_url}p/"
    responses.add(responses.GET, url, json=[{"slug": "proj1"}])
    res = bitcaster_sdk.list_projects()
    assert res == [{"slug": "proj1"}]


def test_list_applications(client_setup: Tuple[RequestsMock, Client]) -> None:
    import bitcaster_sdk

    responses, client = client_setup
    url = f"{client.base_url}p/myapp/a/"
    responses.add(responses.GET, url, json=[{"slug": "app1"}])
    res = bitcaster_sdk.list_applications("myapp")
    assert res == [{"slug": "app1"}]


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
