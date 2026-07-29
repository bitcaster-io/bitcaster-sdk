from __future__ import annotations

import os
import threading
from concurrent.futures import Future
from contextlib import suppress
from time import sleep, time
from typing import Any, Callable

from bitcaster_sdk.async_queue import FullError, Queue
from .log import logger


_TERMINATOR = object()
_DEFAULT_QUEUE_SIZE = 100


class BackgroundWorker:
    def __init__(self, queue_size: int = _DEFAULT_QUEUE_SIZE) -> None:
        self._queue: Queue = Queue(queue_size)
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._thread_for_pid: int | None = None

    @property
    def is_alive(self) -> bool:
        if self._thread_for_pid != os.getpid():
            return False
        if not self._thread:
            return False
        return self._thread.is_alive()

    def _ensure_thread(self) -> None:
        if not self.is_alive:
            self.start()

    def start(self) -> None:
        with self._lock:
            if not self.is_alive:
                self._thread = threading.Thread(target=self._target, name="bitcaster.BackgroundWorker", daemon=True)
                try:
                    self._thread.start()
                    self._thread_for_pid = os.getpid()
                except RuntimeError:
                    self._thread = None

    def kill(self) -> None:
        with self._lock:
            if self._thread:
                with suppress(FullError):
                    self._queue.put_nowait(_TERMINATOR)
                self._thread = None
                self._thread_for_pid = None

    def flush(self, timeout: float | None = None) -> bool:
        if timeout is None:
            timeout = 10.0
        with self._lock:
            if self.is_alive and timeout > 0.0:
                return self._wait_flush(timeout)
        return True

    def full(self) -> bool:
        return self._queue.full()

    def _wait_flush(self, timeout: float) -> bool:
        deadline = time() + timeout
        queue = self._queue

        queue.all_tasks_done.acquire()
        try:
            while queue.unfinished_tasks:
                delay = deadline - time()
                if delay <= 0:
                    return False
                queue.all_tasks_done.wait(timeout=delay)
            return True
        finally:
            queue.all_tasks_done.release()

    def submit(self, fn: Callable[..., Any], /, *args: Any, **kwargs: Any) -> Future[Any]:
        future: Future[Any] = Future()

        def callback() -> None:
            try:
                result = fn(*args, **kwargs)
                future.set_result(result)
            except BaseException as e:
                future.set_exception(e)

        self._ensure_thread()
        try:
            self._queue.put_nowait(callback)
        except FullError:
            future.set_exception(RuntimeError("queue is full"))
        return future

    def _target(self) -> None:
        while True:
            callback = self._queue.get()
            try:
                if callback is _TERMINATOR:
                    break
                try:
                    callback()
                except Exception:
                    logger.error("Failed processing job", exc_info=True)
            finally:
                self._queue.task_done()
            sleep(0)
