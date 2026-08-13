from __future__ import annotations

from typing import Any

import pytest

from bitcaster_sdk.abstract_transport import AbstractTransport


class _ConcreteTransport(AbstractTransport):
    def get(self, path: str) -> Any: ...

    def post(self, path: str, arguments: dict[str, Any]) -> Any: ...

    def patch(self, path: str, arguments: dict[str, Any]) -> Any: ...

    def put(self, path: str, arguments: dict[str, Any]) -> Any: ...


@pytest.fixture
def transport() -> _ConcreteTransport:
    return _ConcreteTransport("http://app.bitcaster.io/api/o/os4d/", "key-11")


class TestInit:
    def test_session_created(self, transport: _ConcreteTransport) -> None:
        assert transport.session is not None

    def test_headers(self, transport: _ConcreteTransport) -> None:
        assert transport.session.headers["Authorization"] == "Key key-11"
        assert transport.session.headers["User-Agent"] == "Bitcaster-SDK"

    def test_last_url_default(self, transport: _ConcreteTransport) -> None:
        assert transport.last_url == ""

    def test_default_timeout(self, transport: _ConcreteTransport) -> None:
        assert transport.timeout is None

    def test_configured_timeout(self) -> None:
        transport = _ConcreteTransport("http://app.bitcaster.io/api/o/os4d/", "key-11", timeout=(3, 7))

        assert transport.timeout == (3, 7)


class TestGetUrl:
    def test_relative_path(self, transport: _ConcreteTransport) -> None:
        assert transport.get_url("u/") == "http://app.bitcaster.io/api/o/os4d/u/"

    def test_absolute_path(self, transport: _ConcreteTransport) -> None:
        assert transport.get_url("/api/system/ping/") == "http://app.bitcaster.io/api/system/ping/"

    def test_full_url(self, transport: _ConcreteTransport) -> None:
        assert transport.get_url("http://other.com/api/") == "http://other.com/api/"

    def test_full_https_url(self, transport: _ConcreteTransport) -> None:
        assert transport.get_url("https://other.com/api/") == "https://other.com/api/"


class TestWithHeaders:
    def test_headers_restored(self, transport: _ConcreteTransport) -> None:
        original = dict(transport.session.headers)
        with transport.with_headers({"X-Test": "val"}):
            assert transport.session.headers.get("X-Test") == "val"
        assert transport.session.headers == original

    def test_headers_restored_on_exception(self, transport: _ConcreteTransport) -> None:
        original = dict(transport.session.headers)
        with pytest.raises(RuntimeError, match="boom"), transport.with_headers({"X-Test": "val"}):
            raise RuntimeError("boom")
        assert transport.session.headers == original


class TestDefaults:
    def test_submit_raises(self, transport: _ConcreteTransport) -> None:
        with pytest.raises(NotImplementedError):
            transport.submit(lambda: 42)

    def test_flush_returns_true(self, transport: _ConcreteTransport) -> None:
        assert transport.flush() is True

    def test_flush_with_timeout(self, transport: _ConcreteTransport) -> None:
        assert transport.flush(timeout=5) is True

    def test_kill_returns_none(self, transport: _ConcreteTransport) -> None:
        assert transport.kill() is None
