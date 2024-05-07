from click.testing import CliRunner
from bitcaster_sdk.__main__ import cli, ping


def test_ping(client_setup, response_ping):
    runner = CliRunner()
    result = runner.invoke(cli, "ping")
    assert result.exit_code == 0
    assert result.output == "{'token': 'Key1', 'slug': 'core'}\n"


def test_trigger(client_setup, response_trigger):
    runner = CliRunner()
    result = runner.invoke(cli, ["trigger", "a1", "-c", "integer", 1, "-c", "string", "abc"])
    assert result.exit_code == 0
    assert result.output == "{'occurrence': 15}\n"


def test_list(client_setup, response_list):
    runner = CliRunner()
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
