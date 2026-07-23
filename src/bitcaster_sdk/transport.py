from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bitcaster_sdk.abstract_transport import AbstractTransport
from .log import logger

if TYPE_CHECKING:
    import requests


class Transport(AbstractTransport):
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

    def patch(self, path: str, arguments: dict[str, Any]) -> requests.Response:
        if self.debug:
            logger.info(f"post {path}")
        with self.with_headers({"Content-Type": "application/json"}):
            self.last_url = self.get_url(path)
            return self.session.patch(self.last_url, json=arguments)

    def put(self, path: str, arguments: dict[str, Any]) -> requests.Response:
        if self.debug:
            logger.info(f"post {path}")
        with self.with_headers({"Content-Type": "application/json"}):
            self.last_url = self.get_url(path)
            return self.session.put(self.last_url, json=arguments)
