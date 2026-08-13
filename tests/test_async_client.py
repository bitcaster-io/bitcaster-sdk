from __future__ import annotations

from concurrent.futures import Future
from typing import Any, Callable

import pytest
import responses as responses_lib
from requests.exceptions import ReadTimeout
from responses import RequestsMock

from bitcaster_sdk.async_client import AsyncClient
from bitcaster_sdk.exceptions import ConfigurationError, EventNotFoundError, ValidationError


@pytest.fixture
def bae() -> str:
    return "http://key-11@app.bitcaster.io/api/o/os4d/"


@pytest.fixture
def client(bae: str) -> AsyncClient:
    return AsyncClient(bae)


@pytest.fixture
def client_setup(client: AsyncClient):
    with RequestsMock() as rsps:
        yield rsps, client


@pytest.fixture
def response_trigger(client_setup):
    rsps, client = client_setup
    url = f"{client.base_url}p/bitcaster/a/bitcaster/e/a1/trigger/"
    rsps.add(responses_lib.POST, url, json={"occurrence": 15}, status=201)
    return url


@pytest.fixture
def response_ping(client_setup):
    rsps, client = client_setup
    rsps.add(responses_lib.GET, f"{client.api_url}system/ping/", json={"token": "Key1", "slug": "core"})


@pytest.fixture
def response_events(client_setup):
    rsps, client = client_setup
    url = f"{client.base_url}p/bitcaster/a/bitcaster/e/"
    rsps.add(responses_lib.GET, url, json=[{"active": True, "slug": "e1"}, {"active": False, "slug": "e2"}])
    return url


@pytest.fixture
def response_users(client_setup):
    rsps, client = client_setup
    url = f"{client.base_url}u/"
    rsps.add(responses_lib.GET, url, json=[{"email": "u1@b.com"}, {"email": "u2@b.com"}])
    return url


@pytest.fixture
def response_projects(client_setup):
    rsps, client = client_setup
    url = f"{client.base_url}p/"
    rsps.add(responses_lib.GET, url, json=[{"slug": "proj1"}, {"slug": "proj2"}])
    return url


@pytest.fixture
def response_applications(client_setup):
    rsps, client = client_setup
    url = f"{client.base_url}p/myapp/a/"
    rsps.add(responses_lib.GET, url, json=[{"slug": "app1"}])
    return url


@pytest.fixture
def response_lists(client_setup):
    rsps, client = client_setup
    url = f"{client.base_url}p/myproject/d/"
    rsps.add(responses_lib.GET, url, json=[{"name": "Dis1", "id": 2}])
    return url


@pytest.fixture
def response_members(client_setup):
    rsps, client = client_setup
    url = f"{client.base_url}p/myproject/d/1/m/"
    rsps.add(responses_lib.GET, url, json=[{"id": 1, "address": "m1@b.com"}])
    return url


class TestTrigger:
    def test_success(self, client_setup, response_trigger) -> None:
        rsps, client = client_setup
        future = client.trigger("bitcaster", "bitcaster", "a1", context={})
        assert future.result(timeout=5) == {"occurrence": 15}

    def test_with_cid(self, client_setup) -> None:
        rsps, client = client_setup
        url = f"{client.base_url}p/bitcaster/a/bitcaster/e/a1/trigger/?cid=abc-123"
        rsps.add(responses_lib.POST, url, json={"occurrence": 42}, status=201)
        future = client.trigger("bitcaster", "bitcaster", "a1", context={}, cid="abc-123")
        assert future.result(timeout=5) == {"occurrence": 42}

    def test_404_raises(self, client_setup) -> None:
        rsps, client = client_setup
        url = f"{client.base_url}p/bitcaster/a/bitcaster/e/unknown/trigger/"
        rsps.add(responses_lib.POST, url, status=404)
        future = client.trigger("bitcaster", "bitcaster", "unknown")
        with pytest.raises(EventNotFoundError):
            future.result(timeout=5)

    def test_400_raises(self, client_setup) -> None:
        rsps, client = client_setup
        url = f"{client.base_url}p/bitcaster/a/bitcaster/e/bad/trigger/"
        rsps.add(responses_lib.POST, url, json={"detail": "bad request"}, status=400)
        future = client.trigger("bitcaster", "bitcaster", "bad")
        with pytest.raises(ValidationError):
            future.result(timeout=5)

    def test_network_error(self, client_setup) -> None:
        rsps, client = client_setup
        url = f"{client.base_url}p/bitcaster/a/bitcaster/e/fail/trigger/"
        rsps.add(responses_lib.POST, url, body=ConnectionError("connection refused"))
        future = client.trigger("bitcaster", "bitcaster", "fail")
        with pytest.raises(ConnectionError):
            future.result(timeout=5)


class TestPing:
    def test_success(self, client_setup, response_ping) -> None:
        rsps, client = client_setup
        future = client.ping()
        assert future.result(timeout=5) == {"token": "Key1", "slug": "core"}

    def test_connection_error(self, client_setup) -> None:
        rsps, client = client_setup
        rsps.add(responses_lib.GET, f"{client.api_url}system/ping/", body=ConnectionError("fail"))
        future = client.ping()
        with pytest.raises(ConnectionError):
            future.result(timeout=5)

    def test_timeout_maps_to_connection_error(self, client_setup) -> None:
        rsps, client = client_setup
        rsps.add(responses_lib.GET, f"{client.api_url}system/ping/", body=ReadTimeout("timed out"))

        future = client.ping()

        with pytest.raises(ConnectionError, match="Connection Error"):
            future.result(timeout=5)


class TestList:
    def test_list_events(self, client_setup, response_events) -> None:
        rsps, client = client_setup
        future = client.list_events("bitcaster", "bitcaster")
        result = future.result(timeout=5)
        assert len(result) == 2
        assert result[0]["active"]

    def test_list_users(self, client_setup, response_users) -> None:
        rsps, client = client_setup
        future = client.list_users()
        result = future.result(timeout=5)
        assert len(result) == 2
        assert result[0]["email"] == "u1@b.com"

    def test_list_projects(self, client_setup, response_projects) -> None:
        rsps, client = client_setup
        future = client.list_projects()
        result = future.result(timeout=5)
        assert len(result) == 2
        assert result[0]["slug"] == "proj1"

    def test_list_applications(self, client_setup, response_applications) -> None:
        rsps, client = client_setup
        future = client.list_applications("myapp")
        result = future.result(timeout=5)
        assert result == [{"slug": "app1"}]

    def test_list_distribution_lists(self, client_setup, response_lists) -> None:
        rsps, client = client_setup
        future = client.list_distribution_lists("myproject")
        result = future.result(timeout=5)
        assert result == [{"name": "Dis1", "id": 2}]

    def test_list_members(self, client_setup, response_members) -> None:
        rsps, client = client_setup
        future = client.list_members("myproject", "1")
        result = future.result(timeout=5)
        assert result == [{"id": 1, "address": "m1@b.com"}]


class TestAddUpdateUser:
    def test_add_user(self, client_setup) -> None:
        rsps, client = client_setup
        url = f"{client.base_url}u/"
        rsps.add(responses_lib.POST, url, json={"email": "new@b.com"}, status=201)
        future = client.add_user("new@b.com", "First", "Last")
        result = future.result(timeout=5)
        assert result == {"email": "new@b.com"}

    def test_update_user(self, client_setup) -> None:
        rsps, client = client_setup
        url = f"{client.base_url}u/new%40b.com/"
        rsps.add(responses_lib.PATCH, url, json={"email": "new@b.com", "first_name": "Updated"}, status=200)
        future = client.update_user("new@b.com", "Updated", "")
        result = future.result(timeout=5)
        assert result["first_name"] == "Updated"


def _submit_after_closing(client: AsyncClient) -> None:
    """Make the transport run submitted work synchronously, after dropping client.transport.

    Simulates a request whose execution starts only after the client has been
    shut down: the closure must fail with RuntimeError instead of using a
    dead transport.
    """
    transport = client.transport

    def submit(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Future[Any]:
        client.transport = None
        future: Future[Any] = Future()
        try:
            future.set_result(fn(*args, **kwargs))
        except Exception as e:  # noqa: BLE001
            future.set_exception(e)
        return future

    transport.submit = submit  # type: ignore[method-assign]


class TestTransportClosedBeforeExecution:
    @pytest.mark.parametrize(
        "call",
        [
            pytest.param(lambda c: c.ping(), id="ping"),
            pytest.param(lambda c: c.list_events("p", "a"), id="list_events"),
            pytest.param(lambda c: c.list_users(), id="list_users"),
            pytest.param(lambda c: c.list_projects(), id="list_projects"),
            pytest.param(lambda c: c.list_applications("p"), id="list_applications"),
            pytest.param(lambda c: c.list_distribution_lists("p"), id="list_distribution_lists"),
            pytest.param(lambda c: c.list_members("p", "1"), id="list_members"),
            pytest.param(lambda c: c.add_user("a@b.com", "F", "L"), id="add_user"),
            pytest.param(lambda c: c.update_user("a@b.com", "F", "L"), id="update_user"),
            pytest.param(lambda c: c.register_user("p", "a", "u1"), id="register_user"),
            pytest.param(lambda c: c.unregister_user("p", "a", "u1"), id="unregister_user"),
        ],
    )
    def test_methods_fail(self, bae: str, call: Callable[[AsyncClient], Future[Any]]) -> None:
        client = AsyncClient(bae)
        _submit_after_closing(client)
        future = call(client)
        with pytest.raises(RuntimeError, match="client not initialized"):
            future.result(timeout=5)

    def test_trigger_fails(self, bae: str) -> None:
        client = AsyncClient(bae)
        _submit_after_closing(client)
        with pytest.warns(DeprecationWarning, match="deprecated"):
            future = client.trigger("p", "a", "e")
        with pytest.raises(RuntimeError, match="client not initialized"):
            future.result(timeout=5)


class TestRegisterUser:
    def test_register_user(self, client_setup) -> None:
        rsps, client = client_setup
        url = f"{client.base_url}p/myproject/a/myapp/register/"
        rsps.add(responses_lib.POST, url, json={"created": True, "user": {"username": "u1"}}, status=201)
        future = client.register_user(
            "myproject",
            "myapp",
            "u1",
            email="u1@b.com",
            addresses=[{"value": "u1@b.com", "assign_to_preferred_channel": True}],
        )
        result = future.result(timeout=5)
        assert result["created"]

    def test_unregister_user(self, client_setup) -> None:
        rsps, client = client_setup
        url = f"{client.base_url}p/myproject/a/myapp/unregister/u1/"
        rsps.add(responses_lib.POST, url, json={"deleted": 1}, status=200)
        future = client.unregister_user("myproject", "myapp", "u1")
        result = future.result(timeout=5)
        assert result == {"deleted": 1}


class TestTimeout:
    def test_trigger_passes_timeout_to_request(self, bae: str) -> None:
        with RequestsMock() as rsps, AsyncClient(bae, timeout=7) as client:
            url = f"{client.base_url}p/bitcaster/a/bitcaster/e/a1/trigger/"
            rsps.add(responses_lib.POST, url, json={"occurrence": 15}, status=201)
            client.set_domain("bitcaster", "bitcaster")

            future = client.trigger_event("a1", context={})

            assert future.result(timeout=5) == {"occurrence": 15}
            assert rsps.calls[0].request.req_kwargs["timeout"] == 7


class TestInit:
    def test_valid_url(self, bae: str) -> None:
        client = AsyncClient(bae)
        assert client.transport is not None
        assert client.base_url == "http://app.bitcaster.io/api/o/os4d/"

    def test_configures_transport_timeout(self, bae: str) -> None:
        client = AsyncClient(bae, timeout=(3, 7))

        assert client.transport is not None
        assert client.transport.timeout == (3, 7)
        client.close()

    def test_no_bae_creates_no_transport(self) -> None:
        client = AsyncClient()
        assert client.transport is None

    def test_invalid_url_raises(self) -> None:
        with pytest.raises(ConfigurationError):
            AsyncClient("invalid-url")

    def test_partial_url_raises(self) -> None:
        with pytest.raises(ConfigurationError):
            AsyncClient("https://example.com")


class TestFlushClose:
    def test_flush(self, client_setup, response_trigger) -> None:
        rsps, client = client_setup
        future = client.trigger("bitcaster", "bitcaster", "a1")
        assert client.flush(timeout=5)
        assert future.result(timeout=1) == {"occurrence": 15}

    def test_close(self, client_setup, response_trigger) -> None:
        rsps, client = client_setup
        client.trigger("bitcaster", "bitcaster", "a1")
        client.close()
        assert client.transport is None

    def test_close_idempotent(self) -> None:
        client = AsyncClient()
        client.close()
        assert client.transport is None

    def test_flush_no_transport(self) -> None:
        client = AsyncClient()
        assert client.flush(timeout=1)

    def test_context_manager(self, bae: str) -> None:
        with AsyncClient(bae) as client:
            assert client.transport is not None
        assert client.transport is None


class TestSubmitErrors:
    def test_network_error_on_get(self, client_setup) -> None:
        rsps, client = client_setup
        rsps.add(responses_lib.GET, f"{client.base_url}p/", body=ConnectionError("fail"))
        future = client.list_projects()
        with pytest.raises(ConnectionError):
            future.result(timeout=5)

    def test_unexpected_status_code(self, client_setup) -> None:
        rsps, client = client_setup
        rsps.add(responses_lib.GET, f"{client.base_url}p/", status=500)
        future = client.list_projects()
        with pytest.raises(ConnectionError):
            future.result(timeout=5)

    def test_uninitialized_client(self) -> None:
        client = AsyncClient()
        with pytest.raises(RuntimeError, match="client not initialized"):
            client.list_projects().result(timeout=5)

    def test_trigger_uninitialized(self) -> None:
        client = AsyncClient()
        with pytest.raises(RuntimeError, match="client not initialized"):
            client.trigger("p", "a", "e").result(timeout=5)

    def test_ping_uninitialized(self) -> None:
        client = AsyncClient()
        with pytest.raises(RuntimeError, match="client not initialized"):
            client.ping().result(timeout=5)


class TestDomain:
    def test_set_domain(self, client: AsyncClient) -> None:
        client.set_domain("my-project", "my-app")
        assert client.project == "my-project"
        assert client.application == "my-app"

    def test_trigger_event(self, client_setup, response_trigger) -> None:
        rsps, client = client_setup
        client.set_domain("bitcaster", "bitcaster")
        future = client.trigger_event("a1", context={})
        assert future.result(timeout=5) == {"occurrence": 15}

    def test_trigger_event_no_domain(self, client: AsyncClient) -> None:
        with pytest.raises(ConfigurationError, match="set_domain"):
            client.trigger_event("a1")

    def test_trigger_event_uses_latest_domain(self, client_setup) -> None:
        rsps, client = client_setup
        url = f"{client.base_url}p/other-project/a/other-app/e/ev/trigger/"
        rsps.add(responses_lib.POST, url, json={"occurrence": 7}, status=201)
        client.set_domain("other-project", "other-app")
        future = client.trigger_event("ev", context={})
        assert future.result(timeout=5) == {"occurrence": 7}

    def test_trigger_deprecated(self, client_setup, response_trigger) -> None:
        rsps, client = client_setup
        with pytest.warns(DeprecationWarning):
            future = client.trigger("bitcaster", "bitcaster", "a1", context={})
            result = future.result(timeout=5)
            assert result == {"occurrence": 15}
