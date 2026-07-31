from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, List, Tuple

import pytest
from click.testing import CliRunner

from bitcaster_sdk.__cli__ import cli

if TYPE_CHECKING:
    from responses import RequestsMock

    from bitcaster_sdk.client import Client


def test_ping(client_setup: Tuple[RequestsMock, Client], response_ping: str) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, "ping")
    assert result.exit_code == 0
    assert result.output == "{'token': 'Key1', 'slug': 'core'}\n"


# @pytest.mark.parametrize("token", [os.environ["BITCASTER_BAE"], None], ids=["token", "no-token"])
@pytest.mark.parametrize("args", [["--bae", "xx", "ping"]])
def test_error_handling(args: List[str]) -> None:
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


def test_users_list(client_setup: Tuple[RequestsMock, Client], response_users: str) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["users", "list"])
    assert result.exit_code == 0


def test_users_add(client_setup: Tuple[RequestsMock, Client]) -> None:
    responses, client = client_setup
    url = f"{client.base_url}u/"
    responses.add(responses.POST, url, json={"email": "new@b.com"}, status=201)
    runner = CliRunner()
    result = runner.invoke(cli, ["users", "add", "new@b.com", "-f", "First", "-l", "Last"])
    assert result.exit_code == 0


def test_users_add_json(client_setup: Tuple[RequestsMock, Client]) -> None:
    responses, client = client_setup
    url = f"{client.base_url}u/"
    responses.add(responses.POST, url, json={"email": "new@b.com"}, status=201)
    runner = CliRunner()
    result = runner.invoke(cli, ["--json", "users", "add", "new@b.com", "-f", "First", "-l", "Last"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == {"email": "new@b.com"}


def test_users_update_json(client_setup: Tuple[RequestsMock, Client]) -> None:
    responses, client = client_setup
    url = f"{client.base_url}u/new%40b.com/"
    responses.add(responses.PATCH, url, json={"email": "new@b.com", "first_name": "Updated"})
    runner = CliRunner()
    result = runner.invoke(cli, ["--json", "users", "update", "new@b.com", "-f", "Updated"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == {"email": "new@b.com", "first_name": "Updated"}


def test_users_update(client_setup: Tuple[RequestsMock, Client]):
    responses, client = client_setup
    email = "user%40example.com"
    url = f"{client.base_url}u/{email}/"
    responses.add(responses.PATCH, url, json={})

    runner = CliRunner()
    result = runner.invoke(cli, ["users", "update", r"user@example.com"])
    assert result.exit_code == 0


def test_unregister(client_setup: Tuple[RequestsMock, Client]) -> None:
    responses, client = client_setup
    url = f"{client.base_url}p/bitcaster/a/bitcaster/unregister/user%40example.com/"
    responses.add(responses.POST, url, json={"deleted": 2})
    runner = CliRunner()
    result = runner.invoke(cli, ["unregister", "user@example.com", "-p", "bitcaster", "-a", "bitcaster"])
    assert result.exit_code == 0
    assert "Removed 2 membership(s)" in result.output


def test_unregister_json(client_setup: Tuple[RequestsMock, Client]) -> None:
    responses, client = client_setup
    url = f"{client.base_url}p/bitcaster/a/bitcaster/unregister/user%40example.com/"
    responses.add(responses.POST, url, json={"deleted": 2})
    runner = CliRunner()
    result = runner.invoke(cli, ["--json", "unregister", "user@example.com", "-p", "bitcaster", "-a", "bitcaster"])
    assert result.exit_code == 0
    assert json.loads(result.output) == {"deleted": 2}


class TestJsonOutput:
    def test_ping_json(self, client_setup: Tuple[RequestsMock, Client], response_ping: str) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "ping"])
        assert result.exit_code == 0
        assert json.loads(result.output) == {"token": "Key1", "slug": "core"}

    def test_events_json(self, client_setup: Tuple[RequestsMock, Client], response_events: str) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "events", "-p", "bitcaster", "-a", "bitcaster"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert data[0]["slug"] == "test-event-1"

    def test_projects_json(self, client_setup: Tuple[RequestsMock, Client]) -> None:
        responses, client = client_setup
        url = f"{client.base_url}p/"
        responses.add(responses.GET, url, json=[{"slug": "proj1", "name": "Project 1"}])
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "projects"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == [{"slug": "proj1", "name": "Project 1"}]

    def test_projects_json_full(self, client_setup: Tuple[RequestsMock, Client]) -> None:
        responses, client = client_setup
        url = f"{client.base_url}p/"
        payload = [
            {
                "name": "Project",
                "slug": "project",
                "applications": "http://localhost:8000/api/o/organization/p/project/a/",
                "lists": "http://localhost:8000/api/o/organization/p/project/d/",
                "channels": "http://localhost:8000/api/o/organization/p/project/c/",
            }
        ]
        responses.add(responses.GET, url, json=payload)
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "projects"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == payload

    def test_lists_json(self, client_setup: Tuple[RequestsMock, Client], response_lists: str) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "lists", "-p", "bitcaster"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)

    def test_members_json(self, client_setup: Tuple[RequestsMock, Client], response_members: str) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "members", "-p", "bitcaster", "-d", "1"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)

    def test_applications_json(self, client_setup: Tuple[RequestsMock, Client]) -> None:
        responses, client = client_setup
        url = f"{client.base_url}p/myapp/a/"
        responses.add(responses.GET, url, json=[{"slug": "app1", "name": "App 1"}])
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "applications", "-p", "myapp"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == [{"slug": "app1", "name": "App 1"}]

    def test_trigger_json(self, client_setup: Tuple[RequestsMock, Client], response_trigger: str) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "trigger", "a1", "-p", "bitcaster", "-a", "bitcaster"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == {"occurrence": 15}

    def test_users_list_json(self, client_setup: Tuple[RequestsMock, Client], response_users: str) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "users", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 3

    def test_projects_json_after_subcommand(self, client_setup: Tuple[RequestsMock, Client]) -> None:
        responses, client = client_setup
        url = f"{client.base_url}p/"
        responses.add(responses.GET, url, json=[{"slug": "proj1", "name": "Project 1"}])
        runner = CliRunner()
        result = runner.invoke(cli, ["projects", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == [{"slug": "proj1", "name": "Project 1"}]

    def test_ping_json_after_subcommand(self, client_setup: Tuple[RequestsMock, Client], response_ping: str) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["ping", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output) == {"token": "Key1", "slug": "core"}

    def test_events_json_after_subcommand(
        self, client_setup: Tuple[RequestsMock, Client], response_events: str
    ) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["events", "-p", "bitcaster", "-a", "bitcaster", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert data[0]["slug"] == "test-event-1"


class TestFormattedOutput:
    def test_projects_formatted(self, client_setup: Tuple[RequestsMock, Client]) -> None:
        responses, client = client_setup
        url = f"{client.base_url}p/"
        responses.add(responses.GET, url, json=[{"slug": "proj1", "name": "Project 1"}])
        runner = CliRunner()
        result = runner.invoke(cli, ["projects"])
        assert result.exit_code == 0
        assert "proj1" in result.output

    def test_applications_formatted(self, client_setup: Tuple[RequestsMock, Client]) -> None:
        responses, client = client_setup
        url = f"{client.base_url}p/myapp/a/"
        responses.add(responses.GET, url, json=[{"slug": "app1", "name": "App 1"}])
        runner = CliRunner()
        result = runner.invoke(cli, ["applications", "-p", "myapp"])
        assert result.exit_code == 0
        assert "app1" in result.output
