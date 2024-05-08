import os

import pytest
from click.testing import CliRunner
from bitcaster_sdk.__main__ import cli


def test_ping(client_setup, response_ping):
    runner = CliRunner()
    result = runner.invoke(cli, "ping")
    assert result.exit_code == 0
    assert result.output == "{'token': 'Key1', 'slug': 'core'}\n"


@pytest.mark.parametrize("token", [os.environ["BITCASTER_BAE"], None], ids=["token", "no-token"])
@pytest.mark.parametrize("debug", ["-d", None], ids=["debug", "no-debug"])
def test_trigger(client_setup, response_trigger, debug, token):
    runner = CliRunner()
    args = []
    if token:
        args.extend(["--bae", token])
    args.append("trigger")
    if debug:
        args.append(debug)
    args.extend(["a1", "-c", "integer", 1, "-c", "string", "abc"])
    result = runner.invoke(cli, args)
    print(result.output)
    assert result.exit_code == 0


def test_list(client_setup, response_list):
    runner = CliRunner()
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
