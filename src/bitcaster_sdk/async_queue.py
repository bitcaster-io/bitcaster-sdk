from __future__ import annotations

import threading
from collections import deque
from time import time
from typing import Any

__all__ = ["EmptyError", "FullError", "Queue"]


class EmptyError(Exception):
    pass


class FullError(Exception):
    pass


class Queue:
    def __init__(self, maxsize: int = 0) -> None:
        self.maxsize = maxsize
        self._init(maxsize)
        self.mutex = threading.RLock()
        self.not_empty = threading.Condition(self.mutex)
        self.not_full = threading.Condition(self.mutex)
        self.all_tasks_done = threading.Condition(self.mutex)
        self.unfinished_tasks = 0

    def task_done(self) -> None:
        with self.all_tasks_done:
            unfinished = self.unfinished_tasks - 1
            if unfinished <= 0:
                if unfinished < 0:
                    raise ValueError("task_done() called too many times")
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished

    def join(self) -> None:
        with self.all_tasks_done:
            while self.unfinished_tasks:
                self.all_tasks_done.wait()

    def qsize(self) -> int:
        with self.mutex:
            return self._qsize()

    def empty(self) -> bool:
        with self.mutex:
            return not self._qsize()

    def full(self) -> bool:
        with self.mutex:
            return 0 < self.maxsize <= self._qsize()

    def put(self, item: Any, block: bool = True, timeout: float | None = None) -> None:
        with self.not_full:
            if self.maxsize > 0:
                if not block:
                    if self._qsize() >= self.maxsize:
                        raise FullError
                elif timeout is None:
                    while self._qsize() >= self.maxsize:
                        self.not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = time() + timeout
                    while self._qsize() >= self.maxsize:
                        remaining = endtime - time()
                        if remaining <= 0.0:
                            raise FullError
                        self.not_full.wait(remaining)
            self._put(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()

    def get(self, block: bool = True, timeout: float | None = None) -> Any:
        with self.not_empty:
            if not block:
                if not self._qsize():
                    raise EmptyError
            elif timeout is None:
                while not self._qsize():
                    self.not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = time() + timeout
                while not self._qsize():
                    remaining = endtime - time()
                    if remaining <= 0.0:
                        raise EmptyError
                    self.not_empty.wait(remaining)
            item = self._get()
            self.not_full.notify()
            return item

    def put_nowait(self, item: Any) -> None:
        return self.put(item, block=False)

    def get_nowait(self) -> Any:
        return self.get(block=False)

    def _init(self, maxsize: int) -> None:
        self.queue: deque[Any] = deque()

    def _qsize(self) -> int:
        return len(self.queue)

    def _put(self, item: Any) -> None:
        self.queue.append(item)

    def _get(self) -> Any:
        return self.queue.popleft()
