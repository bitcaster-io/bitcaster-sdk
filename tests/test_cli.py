from __future__ import annotations

import json
import os
import sys
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, List, Tuple
from urllib.parse import urlparse

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


class FakeParameters:
    def __init__(self, url: str) -> None:
        p = urlparse(url)
        self.host = p.hostname or "localhost"
        self.port = p.port or 5672
        self.virtual_host = p.path.strip("/") or "/"
        self.username = p.username or ""
        self.password = p.password or ""
        self.original = url

    def __str__(self) -> str:
        return self.original


class FakeChannel:
    def __init__(self) -> None:
        self.published: list[tuple[str, str, str, Any]] = []

    def queue_declare(self, queue: str, durable: bool = False, **kwargs: object) -> object:
        return SimpleNamespace()

    def queue_bind(self, queue: str, exchange: str, routing_key: str) -> None:
        pass

    def basic_publish(self, exchange: str, routing_key: str, body: str, properties: object | None = None) -> None:
        self.published.append((exchange, routing_key, body, properties))


class FakeConnection:
    def __init__(self, pika: "FakePika", params: FakeParameters) -> None:
        self.pika = pika
        self.params = params
        self.closed = False

    def channel(self) -> FakeChannel:
        channel = FakeChannel()
        self.pika.channels.append(channel)
        return channel

    def close(self) -> None:
        self.closed = True


class FakePika:
    def __init__(self) -> None:
        self.channels: list[FakeChannel] = []

    def URLParameters(self, url: str) -> FakeParameters:  # noqa: N802
        return FakeParameters(url)

    def BlockingConnection(self, params: FakeParameters) -> FakeConnection:  # noqa: N802
        return FakeConnection(self, params)

    def BasicProperties(self, delivery_mode: int = 1) -> SimpleNamespace:  # noqa: N802
        return SimpleNamespace(delivery_mode=delivery_mode)


@pytest.fixture
def fake_pika(monkeypatch: pytest.MonkeyPatch) -> FakePika:
    fake = FakePika()
    monkeypatch.setitem(sys.modules, "pika", fake)
    return fake


def test_amqp_trigger(fake_pika: FakePika, monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI trigger with an amqp:// BAE uses RabbitClient."""
    monkeypatch.setenv("BITCASTER_BAE", "amqp://user:pass@localhost:5672/")
    monkeypatch.setenv("BITCASTER_PROJECT", "bitcaster")
    monkeypatch.setenv("BITCASTER_APPLICATION", "bitcaster")
    runner = CliRunner()
    result = runner.invoke(cli, ["trigger", "a1", "-c", "foo", "bar"])
    assert result.exit_code == 0

    channel = fake_pika.channels[-1]
    _exchange, _routing_key, body, _properties = channel.published[-1]
    assert json.loads(body) == {"event": "a1", "data": {"foo": "bar"}}


def test_amqp_ping(fake_pika: FakePika, monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI ping with amqp:// BAE uses RabbitClient."""
    monkeypatch.setenv("BITCASTER_BAE", "amqp://user:pass@localhost:5672/")
    runner = CliRunner()
    result = runner.invoke(cli, ["ping"])
    assert result.exit_code == 0
    assert "connected" in result.output


def test_amqp_list_events_errors(fake_pika: FakePika, monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI list commands with amqp:// BAE raise NotImplementedError."""
    monkeypatch.setenv("BITCASTER_BAE", "amqp://user:pass@localhost:5672/")
    runner = CliRunner()
    result = runner.invoke(cli, ["events", "-p", "x", "-a", "y"])
    assert result.exit_code != 0
    assert "only publishes events" in result.output


def test_cli_requires_bae(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BITCASTER_BAE", raising=False)
    runner = CliRunner()
    result = runner.invoke(cli, ["ping"])
    assert result.exit_code != 0
    assert "Failed to initialize" in result.output


@pytest.mark.parametrize("status", [401, 404, 500])
@pytest.mark.parametrize(
    ("args", "path"),
    [
        (["projects"], "p/"),
        (["lists", "-p", "bitcaster"], "p/bitcaster/d/"),
        (["applications", "-p", "bitcaster"], "p/bitcaster/a/"),
        (["members", "-p", "bitcaster", "-d", "1"], "p/bitcaster/d/1/m/"),
        (["events", "-p", "bitcaster", "-a", "bitcaster"], "p/bitcaster/a/bitcaster/e/"),
    ],
)
def test_list_commands_error_handling(
    client_setup: Tuple[RequestsMock, Client], args: List[str], path: str, status: int
) -> None:
    responses, client = client_setup
    responses.add(responses.GET, f"{client.base_url}{path}", json={"detail": "err"}, status=status)
    runner = CliRunner()
    result = runner.invoke(cli, args)
    assert result.exit_code != 0


def test_ping_error_handling(client_setup: Tuple[RequestsMock, Client]) -> None:
    responses, client = client_setup
    responses.add(responses.GET, f"{client.api_url}system/ping/", json={}, status=500)
    runner = CliRunner()
    result = runner.invoke(cli, ["ping"])
    assert result.exit_code != 0


def test_trigger_error_handling(client_setup: Tuple[RequestsMock, Client]) -> None:
    responses, client = client_setup
    url = f"{client.base_url}p/bitcaster/a/bitcaster/e/a1/trigger/"
    responses.add(responses.POST, url, json={}, status=500)
    runner = CliRunner()
    result = runner.invoke(cli, ["trigger", "a1", "-p", "bitcaster", "-a", "bitcaster"])
    assert result.exit_code != 0


def test_users_list_error_handling(client_setup: Tuple[RequestsMock, Client]) -> None:
    responses, client = client_setup
    responses.add(responses.GET, f"{client.base_url}u/", json={}, status=500)
    runner = CliRunner()
    result = runner.invoke(cli, ["users", "list"])
    assert result.exit_code != 0


def test_users_add_invalid_custom_fields(client_setup: Tuple[RequestsMock, Client]) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["users", "add", "new@b.com", "--custom", "not-json"])
    assert result.exit_code != 0
    assert "valid json" in result.output


def test_users_update_invalid_custom_fields(client_setup: Tuple[RequestsMock, Client]) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["users", "update", "new@b.com", "--custom", "not-json"])
    assert result.exit_code != 0
    assert "valid json" in result.output


def test_users_update_validation_error(client_setup: Tuple[RequestsMock, Client]) -> None:
    responses, client = client_setup
    url = f"{client.base_url}u/new%40b.com/"
    responses.add(responses.PATCH, url, json={"email": ["invalid"]}, status=400)
    runner = CliRunner()
    result = runner.invoke(cli, ["users", "update", "new@b.com", "-f", "First"])
    assert result.exit_code == 1
    assert "Invalid request" in result.output


@pytest.mark.parametrize(
    ("args", "path"),
    [
        (["projects"], "p/"),
        (["applications", "-p", "bitcaster"], "p/bitcaster/a/"),
    ],
)
def test_list_commands_debug_output(client_setup: Tuple[RequestsMock, Client], args: List[str], path: str) -> None:
    responses, client = client_setup
    url = f"{client.base_url}{path}"
    responses.add(responses.GET, url, json=[{"slug": "s1", "name": "N1"}])
    runner = CliRunner()
    result = runner.invoke(cli, ["--debug", *args])
    assert result.exit_code == 0
    assert url in result.output