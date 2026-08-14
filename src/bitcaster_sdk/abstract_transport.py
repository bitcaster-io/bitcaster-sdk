from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Iterator
from urllib.parse import urlparse

import requests

if TYPE_CHECKING:
    from concurrent.futures import Future


class AbstractTransport(ABC):
    def __init__(self, base_url: str, token: str, **kwargs: Any) -> None:
        self.session = requests.Session()
        self.base_url = base_url
        self.debug = kwargs.get("debug")
        self.timeout: float | tuple[float, float] | None = kwargs.get("timeout")
        self.session.headers.update({"Authorization": f"Key {token}", "User-Agent": "Bitcaster-SDK"})
        self.conn = urlparse(base_url)
        self.last_url = ""

    def get_url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        if path.startswith("/"):
            return f"{self.conn.scheme}://{self.conn.netloc}{path}"
        return f"{self.conn.scheme}://{self.conn.netloc}{self.conn.path}{path}"

    @contextmanager
    def with_headers(self, values: dict[str, str]) -> Iterator[None]:
        c = dict(self.session.headers)
        self.session.headers.update(values)
        try:
            yield
        finally:
            self.session.headers = c

    @abstractmethod
    def get(self, path: str) -> Any: ...  # pragma: no cover

    @abstractmethod
    def post(self, path: str, arguments: dict[str, Any]) -> Any: ...  # pragma: no cover

    @abstractmethod
    def patch(self, path: str, arguments: dict[str, Any]) -> Any: ...  # pragma: no cover

    @abstractmethod
    def put(self, path: str, arguments: dict[str, Any]) -> Any: ...  # pragma: no cover

    def submit(self, fn: Any, *args: Any, **kwargs: Any) -> Future[Any]:
        raise NotImplementedError

    def flush(self, timeout: float | None = None) -> bool:
        return True

    def kill(self) -> None:
        return None
