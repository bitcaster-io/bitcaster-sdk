import os
from typing import Tuple

import pytest
from click.testing import CliRunner
from responses import RequestsMock

from bitcaster_sdk.__main__ import cli
from bitcaster_sdk.client import Client


def test_ping(client_setup: Tuple[RequestsMock, Client], response_ping: str) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, "ping")
    assert result.exit_code == 0
    assert result.output == "{'token': 'Key1', 'slug': 'core'}\n"


# @pytest.mark.parametrize("token", [os.environ["BITCASTER_BAE"], None], ids=["token", "no-token"])
@pytest.mark.parametrize("args", (["--bae", "xx", "ping"],))
def test_error_handling(args: list[str]) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, args)
    assert result.exit_code > 0


@pytest.mark.parametrize("verbosity", [1, 2], ids=["v1", "v2"])
@pytest.mark.parametrize("token", [os.environ["BITCASTER_BAE"], None], ids=["token", "no-token"])
@pytest.mark.parametrize("debug", ["-d", None], ids=["debug", "no-debug"])
def test_trigger(
    client_setup: Tuple[RequestsMock, Client], response_trigger: str, debug: str, token: str, verbosity: int
) -> None:
    runner = CliRunner()
    args: list[str] = []
    if token:
        args.extend(["--bae", token])
    if debug:
        args.extend(["--debug"])
    verb = ["-v"] * verbosity
    args.append("trigger")
    args.extend(["a1", "-p", "bitcaster", "-a", "bitcaster", "-c", "integer", "1", "-c", "string", "abc"])
    args.extend(verb)
    result = runner.invoke(cli, args)
    assert result.exit_code == 0


def test_events(client_setup: Tuple[RequestsMock, Client], response_events: str) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["events", "-p", "bitcaster", "-a", "bitcaster"])
    assert result.exit_code == 0


@pytest.mark.parametrize("debug", ["-d", None], ids=["debug", "no-debug"])
def test_lists(client_setup: Tuple[RequestsMock, Client], response_lists: str, debug: str) -> None:
    runner = CliRunner()
    args: list[str] = []
    if debug:
        args.extend(["--debug"])
    args.extend(["lists", "-p", "bitcaster"])
    result = runner.invoke(cli, args)
    assert result.exit_code == 0


@pytest.mark.parametrize("debug", ["-d", None], ids=["debug", "no-debug"])
def test_members(client_setup: Tuple[RequestsMock, Client], response_members: str, debug: str) -> None:
    runner = CliRunner()
    args: list[str] = []
    if debug:
        args.extend(["--debug"])
    args.extend(["members", "-p", "bitcaster", "-d", "1"])
    result = runner.invoke(cli, args)
    assert result.exit_code == 0


def test_users(client_setup: Tuple[RequestsMock, Client], response_users: str) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["users"])
    assert result.exit_code == 0
