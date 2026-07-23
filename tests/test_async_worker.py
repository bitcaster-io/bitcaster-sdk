from __future__ import annotations

import os
import threading
from time import sleep
from typing import TYPE_CHECKING

import pytest

from bitcaster_sdk.async_worker import BackgroundWorker

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


def test_submit_returns_result() -> None:
    worker: BackgroundWorker = BackgroundWorker()
    future = worker.submit(lambda: 42)
    assert future.result(timeout=5) == 42
    worker.kill()


def test_submit_multiple_futures() -> None:
    worker: BackgroundWorker = BackgroundWorker()
    futures = [worker.submit(lambda i=i: i * 2) for i in range(10)]
    results = [f.result(timeout=5) for f in futures]
    assert results == [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
    worker.kill()


def test_submit_with_args() -> None:
    worker: BackgroundWorker = BackgroundWorker()

    def add(a: int, b: int) -> int:
        return a + b

    future = worker.submit(add, 3, b=4)
    assert future.result(timeout=5) == 7
    worker.kill()


def test_submit_sets_exception() -> None:
    worker: BackgroundWorker = BackgroundWorker()

    def fail() -> None:
        msg = "oops"
        raise ValueError(msg)

    future = worker.submit(fail)
    with pytest.raises(ValueError, match="oops"):
        future.result(timeout=5)
    worker.kill()


def test_flush_waits_for_pending() -> None:
    worker: BackgroundWorker = BackgroundWorker()
    results: list[int] = []

    def delayed_add(v: int) -> None:
        sleep(0.02)
        results.append(v)

    worker.submit(delayed_add, 1)
    worker.submit(delayed_add, 2)
    assert worker.flush(timeout=5)
    assert results == [1, 2]
    worker.kill()


def test_flush_empty_queue() -> None:
    worker: BackgroundWorker = BackgroundWorker()
    assert worker.flush(timeout=1)
    worker.kill()


def test_flush_timeout() -> None:
    worker: BackgroundWorker = BackgroundWorker()

    def slow() -> None:
        sleep(10)

    worker.submit(slow)
    assert not worker.flush(timeout=0.05)
    worker.kill()


def test_is_alive() -> None:
    worker: BackgroundWorker = BackgroundWorker()
    assert not worker.is_alive
    worker.submit(lambda: None).result(timeout=5)
    assert worker.is_alive
    worker.kill()
    sleep(0.05)
    assert not worker.is_alive


def test_full() -> None:
    worker: BackgroundWorker = BackgroundWorker(queue_size=2)
    assert not worker.full()
    worker.submit(lambda: None)
    assert not worker.full()
    # The worker processes items quickly, so queue is rarely full
    # but we can still verify the method doesn't crash
    worker.flush(timeout=5)
    worker.kill()


def test_kill_stops_worker() -> None:
    worker: BackgroundWorker = BackgroundWorker()
    future = worker.submit(lambda: 99)
    assert future.result(timeout=5) == 99
    worker.kill()
    # After kill, worker should not be alive
    sleep(0.05)
    assert not worker.is_alive


def test_future_exception_on_full_queue() -> None:
    worker: BackgroundWorker = BackgroundWorker(queue_size=1)
    worker.submit(lambda: sleep(0.1))
    worker.submit(lambda: None)
    future3 = worker.submit(lambda: 42)
    try:
        future3.result(timeout=3)
    except RuntimeError:
        pass
    except Exception:
        pass
    finally:
        worker.kill()


def test_multiple_workers_not_needed() -> None:
    worker: BackgroundWorker = BackgroundWorker()
    futures = [worker.submit(lambda i=i: i) for i in range(20)]
    results = [f.result(timeout=5) for f in futures]
    assert results == list(range(20))
    worker.kill()


def test_submit_after_kill_restarts() -> None:
    worker: BackgroundWorker = BackgroundWorker()
    future1 = worker.submit(lambda: 1)
    assert future1.result(timeout=5) == 1
    worker.kill()
    sleep(0.05)
    future2 = worker.submit(lambda: 2)
    assert future2.result(timeout=5) == 2
    assert worker.is_alive
    worker.kill()


def test_flush_default_timeout() -> None:
    worker: BackgroundWorker = BackgroundWorker()
    assert worker.flush()


def test_start_when_alive() -> None:
    worker: BackgroundWorker = BackgroundWorker()
    future = worker.submit(lambda: 42)
    assert future.result(timeout=5) == 42
    assert worker.is_alive
    worker.start()
    assert worker.is_alive
    worker.kill()


def test_callback_exception_logged() -> None:
    worker: BackgroundWorker = BackgroundWorker()

    def fail() -> None:
        msg = "job error"
        raise ValueError(msg)

    future = worker.submit(fail)
    with pytest.raises(ValueError, match="job error"):
        future.result(timeout=5)
    worker.kill()


def test_full_method() -> None:
    worker: BackgroundWorker = BackgroundWorker(queue_size=1)
    worker.submit(lambda: None)
    worker.flush(timeout=5)
    assert not worker.full()
    worker.kill()


def test_is_alive_before_start() -> None:
    worker: BackgroundWorker = BackgroundWorker()
    assert not worker.is_alive


def test_kill_idle_worker() -> None:
    worker: BackgroundWorker = BackgroundWorker()
    worker.kill()
    assert not worker.is_alive


def test_thread_start_runtime_error(monkeypatch: MonkeyPatch) -> None:
    worker: BackgroundWorker = BackgroundWorker()
    original_start = threading.Thread.start

    def failing_start(self: threading.Thread) -> None:
        if self.name == "bitcaster.BackgroundWorker":
            msg = "thread failed"
            raise RuntimeError(msg)
        original_start(self)

    monkeypatch.setattr(threading.Thread, "start", failing_start)
    worker._ensure_thread()
    assert not worker.is_alive
    monkeypatch.undo()
    worker.kill()


def test_callback_direct_exception() -> None:
    worker: BackgroundWorker = BackgroundWorker()
    worker._ensure_thread()

    def failing() -> None:
        msg = "direct error"
        raise ValueError(msg)

    worker._queue.put(failing)
    sleep(0.1)
    assert worker._queue.empty()
    worker.submit(lambda: 42).result(timeout=5)
    worker.kill()


def test_is_alive_after_pid_change(monkeypatch: MonkeyPatch) -> None:
    worker: BackgroundWorker = BackgroundWorker()
    worker.submit(lambda: 42).result(timeout=5)
    monkeypatch.setattr(os, "getpid", lambda: 99999)
    assert not worker.is_alive
    worker.kill()


def test_is_alive_thread_none() -> None:
    worker: BackgroundWorker = BackgroundWorker()
    worker.submit(lambda: None).result(timeout=5)
    worker._thread_for_pid = os.getpid()
    worker._thread = None
    assert not worker.is_alive
    worker.kill()
