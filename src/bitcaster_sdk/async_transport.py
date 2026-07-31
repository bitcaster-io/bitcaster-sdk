from __future__ import annotations

from typing import TYPE_CHECKING, Any

from bitcaster_sdk.abstract_transport import AbstractTransport
from bitcaster_sdk.async_worker import BackgroundWorker
from .log import logger

if TYPE_CHECKING:
    from concurrent.futures import Future

    import requests


class AsyncTransport(AbstractTransport):
    def __init__(self, base_url: str, token: str, **kwargs: Any) -> None:
        super().__init__(base_url, token, **kwargs)
        self._worker = BackgroundWorker(queue_size=kwargs.get("queue_size", 100))

    def get(self, path: str) -> Future[requests.Response]:
        url = self.get_url(path)
        if self.debug:
            logger.info("get %s", url)

        def _call() -> requests.Response:
            return self.session.get(url, timeout=self.timeout)

        return self._worker.submit(_call)

    def post(self, path: str, arguments: dict[str, Any]) -> Future[requests.Response]:
        url = self.get_url(path)
        if self.debug:
            logger.info("post %s", url)

        def _call() -> requests.Response:
            with self.with_headers({"Content-Type": "application/json"}):
                return self.session.post(url, json=arguments, timeout=self.timeout)

        return self._worker.submit(_call)

    def patch(self, path: str, arguments: dict[str, Any]) -> Future[requests.Response]:
        url = self.get_url(path)
        if self.debug:
            logger.info("patch %s", url)

        def _call() -> requests.Response:
            with self.with_headers({"Content-Type": "application/json"}):
                return self.session.patch(url, json=arguments, timeout=self.timeout)

        return self._worker.submit(_call)

    def put(self, path: str, arguments: dict[str, Any]) -> Future[requests.Response]:
        url = self.get_url(path)
        if self.debug:
            logger.info("put %s", url)

        def _call() -> requests.Response:
            with self.with_headers({"Content-Type": "application/json"}):
                return self.session.put(url, json=arguments, timeout=self.timeout)

        return self._worker.submit(_call)

    def submit(self, fn: Any, *args: Any, **kwargs: Any) -> Any:
        return self._worker.submit(fn, *args, **kwargs)

    def flush(self, timeout: float | None = None) -> bool:
        return self._worker.flush(timeout)

    def kill(self) -> None:
        self._worker.kill()
