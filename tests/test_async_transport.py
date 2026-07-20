from __future__ import annotations

import pytest
import responses as responses_lib

from bitcaster_sdk.async_transport import AsyncTransport


@pytest.fixture
def transport() -> AsyncTransport:
    return AsyncTransport("http://app.bitcaster.io/api/o/os4d/", "key-11")


@pytest.fixture
def timeout_transport() -> AsyncTransport:
    return AsyncTransport("http://app.bitcaster.io/api/o/os4d/", "key-11", timeout=7)


@pytest.fixture
def timeout_transport_setup(timeout_transport: AsyncTransport):
    with responses_lib.RequestsMock() as rsps:
        yield rsps, timeout_transport


class TestGetUrl:
    def test_relative_path(self, transport: AsyncTransport) -> None:
        assert transport.get_url("u/") == "http://app.bitcaster.io/api/o/os4d/u/"

    def test_absolute_path(self, transport: AsyncTransport) -> None:
        assert transport.get_url("/api/system/ping/") == "http://app.bitcaster.io/api/system/ping/"

    def test_full_url(self, transport: AsyncTransport) -> None:
        assert transport.get_url("http://other.com/api/") == "http://other.com/api/"


class TestGet:
    def test_success(self, timeout_transport_setup) -> None:
        rsps, transport = timeout_transport_setup
        rsps.add(responses_lib.GET, "http://app.bitcaster.io/api/o/os4d/p/", json=[{"slug": "p1"}])
        future = transport.get("p/")
        response = future.result(timeout=5)
        assert response.json() == [{"slug": "p1"}]
        assert rsps.calls[0].request.req_kwargs["timeout"] == 7

    def test_url_tracking(self, transport: AsyncTransport) -> None:
        assert transport.last_url == ""


class TestPost:
    def test_success(self, timeout_transport_setup) -> None:
        rsps, transport = timeout_transport_setup
        rsps.add(responses_lib.POST, "http://app.bitcaster.io/api/o/os4d/u/", json={"email": "a@b.com"}, status=201)
        future = transport.post("u/", {"email": "a@b.com"})
        response = future.result(timeout=5)
        assert response.json() == {"email": "a@b.com"}
        assert response.status_code == 201
        assert rsps.calls[0].request.req_kwargs["timeout"] == 7


class TestPatch:
    def test_success(self, timeout_transport_setup) -> None:
        rsps, transport = timeout_transport_setup
        rsps.add(responses_lib.PATCH, "http://app.bitcaster.io/api/o/os4d/u/a%40b.com/", json={"email": "a@b.com"})
        future = transport.patch("u/a%40b.com/", {"first_name": "A"})
        response = future.result(timeout=5)
        assert response.json() == {"email": "a@b.com"}
        assert rsps.calls[0].request.req_kwargs["timeout"] == 7


class TestPut:
    def test_success(self, timeout_transport_setup) -> None:
        rsps, transport = timeout_transport_setup
        rsps.add(responses_lib.PUT, "http://app.bitcaster.io/api/o/os4d/u/a%40b.com/", json={"email": "a@b.com"})
        future = transport.put("u/a%40b.com/", {"email": "a@b.com"})
        response = future.result(timeout=5)
        assert response.json() == {"email": "a@b.com"}
        assert rsps.calls[0].request.req_kwargs["timeout"] == 7


class TestSubmit:
    def test_submit_function(self, transport: AsyncTransport) -> None:
        future = transport.submit(lambda: 42)
        assert future.result(timeout=5) == 42

    def test_submit_with_args(self, transport: AsyncTransport) -> None:
        future = transport.submit(lambda a, b: a + b, 3, b=4)
        assert future.result(timeout=5) == 7


class TestFlushKill:
    def test_flush(self, transport: AsyncTransport) -> None:
        future = transport.submit(lambda: 1)
        assert transport.flush(timeout=5)
        assert future.result(timeout=1) == 1

    def test_kill(self, transport: AsyncTransport) -> None:
        transport.submit(lambda: 1)
        transport.kill()
        # Worker should restart on next submit
        future = transport.submit(lambda: 2)
        assert future.result(timeout=5) == 2
        transport.kill()

    def test_flush_no_timeout(self, transport: AsyncTransport) -> None:
        future = transport.submit(lambda: 99)
        assert transport.flush()
        assert future.result(timeout=1) == 99


class TestWithHeaders:
    def test_with_headers_context(self, transport: AsyncTransport) -> None:
        with transport.with_headers({"X-Test": "value"}):
            assert transport.session.headers.get("X-Test") == "value"
        assert "X-Test" not in transport.session.headers


class TestDebug:
    def test_debug_mode(self) -> None:
        transport = AsyncTransport("http://app.bitcaster.io/api/o/os4d/", "key-11", debug=True)
        assert transport.debug

    def test_default_debug_false(self, transport: AsyncTransport) -> None:
        assert not transport.debug
