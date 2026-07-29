from __future__ import annotations

import threading
from time import sleep

import pytest

from bitcaster_sdk.async_queue import EmptyError, FullError, Queue


def test_put_and_get() -> None:
    q: Queue = Queue(maxsize=10)
    q.put("a")
    q.put("b")
    assert q.get() == "a"
    assert q.get() == "b"


def test_fifo_order() -> None:
    q: Queue = Queue()
    for i in range(5):
        q.put(i)
    for i in range(5):
        assert q.get() == i


def test_put_nowait_get_nowait() -> None:
    q: Queue = Queue(maxsize=2)
    q.put_nowait("a")
    q.put_nowait("b")
    assert q.get_nowait() == "a"
    assert q.get_nowait() == "b"


def test_put_nowait_full() -> None:
    q: Queue = Queue(maxsize=1)
    q.put_nowait("a")
    with pytest.raises(FullError):
        q.put_nowait("b")


def test_get_nowait_empty() -> None:
    q: Queue = Queue()
    with pytest.raises(EmptyError):
        q.get_nowait()


def test_qsize() -> None:
    q: Queue = Queue()
    assert q.qsize() == 0
    q.put("a")
    assert q.qsize() == 1
    q.put("b")
    assert q.qsize() == 2
    q.get()
    assert q.qsize() == 1


def test_empty_full() -> None:
    q: Queue = Queue(maxsize=2)
    assert q.empty()
    assert not q.full()
    q.put("a")
    assert not q.empty()
    assert not q.full()
    q.put("b")
    assert not q.empty()
    assert q.full()
    q.get()
    assert not q.full()


def test_infinite_queue() -> None:
    q: Queue = Queue(maxsize=0)
    for i in range(1000):
        q.put(i)
    assert q.qsize() == 1000
    assert not q.full()


def test_task_done_and_join() -> None:
    q: Queue = Queue()
    results: list[str] = []

    def consumer() -> None:
        while True:
            item = q.get()
            if item is None:
                q.task_done()
                break
            results.append(item)
            q.task_done()

    t = threading.Thread(target=consumer, daemon=True)
    t.start()

    q.put("a")
    q.put("b")
    q.put(None)
    q.join()
    assert results == ["a", "b"]


def test_join_timeout_blocks() -> None:
    q: Queue = Queue()
    q.put("a")

    def delayed_consume() -> None:
        sleep(0.05)
        q.get()
        q.task_done()

    t = threading.Thread(target=delayed_consume, daemon=True)
    t.start()
    q.join()
    assert q.qsize() == 0


def test_task_done_too_many() -> None:
    q: Queue = Queue()
    q.put("a")
    q.get()
    q.task_done()
    with pytest.raises(ValueError, match="too many"):
        q.task_done()


def test_get_block_with_timeout() -> None:
    q: Queue = Queue()
    with pytest.raises(EmptyError):
        q.get(timeout=0.05)


def test_put_block_with_timeout() -> None:
    q: Queue = Queue(maxsize=1)
    q.put("a")
    with pytest.raises(FullError):
        q.put("b", timeout=0.05)


def test_put_block_false_on_full() -> None:
    q: Queue = Queue(maxsize=1)
    q.put("a")
    with pytest.raises(FullError):
        q.put("b", block=False)


def test_get_block_false_on_empty() -> None:
    q: Queue = Queue()
    with pytest.raises(EmptyError):
        q.get(block=False)


def test_put_block_no_timeout_waits() -> None:
    q: Queue = Queue(maxsize=1)
    q.put("a")

    def putter() -> None:
        q.put("b")

    t = threading.Thread(target=putter, daemon=True)
    t.start()
    sleep(0.2)
    assert q.qsize() == 1
    assert q.get() == "a"
    t.join(timeout=5)
    assert q.qsize() == 1
    assert q.get() == "b"


def test_put_with_timeout_consumed_before_expiry() -> None:
    q: Queue = Queue(maxsize=1)
    q.put("a")

    def delayed_consume() -> None:
        sleep(0.05)
        q.get()

    t = threading.Thread(target=delayed_consume, daemon=True)
    t.start()
    q.put("b", timeout=5)
    t.join()
    assert q.get() == "b"


def test_get_with_timeout_produced_before_expiry() -> None:
    q: Queue = Queue()

    def delayed_produce() -> None:
        sleep(0.05)
        q.put("x")

    t = threading.Thread(target=delayed_produce, daemon=True)
    t.start()
    result = q.get(timeout=5)
    t.join()
    assert result == "x"


def test_thread_safety() -> None:
    q: Queue = Queue(maxsize=100)
    n = 100
    results: list[int] = []

    def producer() -> None:
        for i in range(n):
            q.put(i)

    def consumer() -> None:
        for _ in range(n):
            item = q.get()
            results.append(item)
            q.task_done()

    threads = [
        threading.Thread(target=producer, daemon=True),
        threading.Thread(target=consumer, daemon=True),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    q.join()
    assert sorted(results) == list(range(n))
