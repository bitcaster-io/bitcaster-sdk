from contextlib import contextmanager
from typing import Any, Iterator
from urllib.parse import urlparse

import requests

from .logging import logger


class Transport:
    def __init__(self, base_url: str, token: str, **kwargs: Any) -> None:
        self.session = requests.Session()
        self.base_url = base_url
        self.debug = kwargs.get("debug")
        self.session.headers.update({"Authorization": f"Key {token}", "User-Agent": "Bitcaster-SDK"})
        self.conn = urlparse(base_url)

    def get_url(self, path: str) -> str:
        # return f"{self.conn.scheme}://{self.conn.netloc}{self.conn.path}{path}"
        if path.startswith("http:"):
            return path
        elif path.startswith("/"):
            return f"{self.conn.scheme}://{self.conn.netloc}{path}"
        else:
            return f"{self.conn.scheme}://{self.conn.netloc}{self.conn.path}{path}"

    @contextmanager
    def with_headers(self, values: dict[str, str]) -> Iterator[None]:
        c = dict(self.session.headers)
        self.session.headers.update(values)
        yield
        self.session.headers = c

    def get(self, path: str) -> requests.Response:
        self.last_url = self.get_url(path)

        if self.debug:
            logger.info(f"get {self.last_url}")

        return self.session.get(self.last_url)

    def post(self, path: str, arguments: dict[str, Any]) -> requests.Response:
        if self.debug:
            logger.info(f"post {path}")
        with self.with_headers({"Content-Type": "application/json"}):
            self.last_url = self.get_url(path)
            return self.session.post(self.last_url, json=arguments)
