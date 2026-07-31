from __future__ import annotations

import pytest
import responses as responses_lib
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


class TestUnregisterUser:
    def test_unregister_user_from_application(self, client_setup) -> None:
        rsps, client = client_setup
        url = f"{client.base_url}p/myproject/a/myapp/unregister/user%40b.com/"
        rsps.add(responses_lib.POST, url, json={"deleted": 3})
        future = client.unregister_user("myproject", "user@b.com", application="myapp")
        result = future.result(timeout=5)
        assert result == {"deleted": 3}

    def test_unregister_user_from_project(self, client_setup) -> None:
        rsps, client = client_setup
        url = f"{client.base_url}p/myproject/unregister/user%40b.com/"
        rsps.add(responses_lib.POST, url, json={"deleted": 5})
        future = client.unregister_user("myproject", "user@b.com")
        result = future.result(timeout=5)
        assert result == {"deleted": 5}


class TestInit:
    def test_valid_url(self, bae: str) -> None:
        client = AsyncClient(bae)
        assert client.transport is not None
        assert client.base_url == "http://app.bitcaster.io/api/o/os4d/"

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
