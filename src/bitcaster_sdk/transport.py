from contextlib import contextmanager
from urllib.parse import urlparse

import requests

from .logging import logger


class Transport:
    def __init__(self, base_url, token, **kwargs):
        self.session = requests.Session()
        self.base_url = base_url
        self.debug = kwargs.get("debug")
        self.session.headers.update({"Authorization": f"Key {token}", "User-Agent": "Bitcaster-SDK"})
        self.conn = urlparse(base_url)

    def get_url(self, path):
        if path.startswith("/"):
            return f"{self.conn.scheme}://{self.conn.netloc}{path}"
        else:
            return f"{self.conn.scheme}://{self.conn.netloc}{self.conn.path}{path}"

    @contextmanager
    def with_headers(self, values: dict):
        c = dict(self.session.headers)
        self.session.headers.update(values)
        yield
        self.session.headers = c

    def get(self, path):
        url = self.get_url(path)
        if self.debug:
            logger.info(f"get {url}")

        return self.session.get(url)

    def post(self, path, arguments):
        if self.debug:
            logger.info(f"post {path}")
        with self.with_headers({"Content-Type": "application/json"}):
            return self.session.post(self.get_url(path), json=arguments)
