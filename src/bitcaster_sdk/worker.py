import atexit
import os
import threading
from queue import Full, Queue
from time import sleep, time
from requests.exceptions import (ConnectionError, HTTPError)
from typing import Optional, Callable
from .logging import logger

_TERMINATOR = object()


def check_thread_support():
    # type: () -> None
    try:
        from uwsgi import opt  # type: ignore
    except ImportError:
        return

    # When `threads` is passed in as a uwsgi option,
    # `enable-threads` is implied on.
    if "threads" in opt:
        return

    if str(opt.get("enable-threads", "0")).lower() in ("false", "off", "no", "0"):
        from warnings import warn

        warn(
            Warning(
                "We detected the use of uwsgi with disabled threads.  "
                "This will cause issues with the transport you are "
                "trying to use.  Please enable threading for uwsgi.  "
                '(Add the "enable-threads" flag).'
            )
        )


class AbstractWorker:
    def __init__(self, options: dict = None):
        pass

    def start(self):
        pass

    def submit(self, callback):
        raise NotImplementedError()

    def empty(self):
        raise NotImplementedError()

    def terminate(self):
        raise NotImplementedError()


class SynchronousWorker(AbstractWorker):
    def submit(self, callback):
        callback()

    def empty(self):
        return True

    def terminate(self):
        return True

class BackgroundWorker(AbstractWorker):
    def __init__(self, options: dict = None):
        super().__init__(options)
        check_thread_support()
        self.options = {'queue_size': 100, 'shutdown_timeout': 10,
                        'pause_on_error': 10, 'backoff': 1}
        if options:
            self.options.update(options)
        self.terminating = False
        self.errors = 0
        self._queue = Queue(self.options['queue_size'])  # type: Queue
        self._lock = threading.Lock()
        self._thread = None  # type: Optional[threading.Thread]
        self._thread_for_pid = None  # type: Optional[int]

    @property
    def is_alive(self):
        # type: () -> bool
        if self._thread_for_pid != os.getpid():
            return False
        if not self._thread:
            return False
        return self._thread.is_alive()

    def submit(self, callback):
        # type: (Callable[[], None]) -> None
        self._ensure_thread()
        try:
            self._queue.put_nowait(callback)
        except Full:
            logger.debug("background worker queue full, dropping event")

    def _ensure_thread(self):
        # type: () -> None
        if not self.is_alive:
            self.start()

    def _timed_queue_join(self, timeout):
        """
        implementation of Queue.join which takes a 'timeout' argument

        returns true on success, false on timeout
        """
        deadline = time() + timeout
        queue = self._queue

        queue.all_tasks_done.acquire()
        try:
            while queue.unfinished_tasks:
                delay = deadline - time()
                if delay <= 0:
                    # timed out
                    return False

                queue.all_tasks_done.wait(timeout=delay)

            return True

        finally:
            queue.all_tasks_done.release()

    def main_thread_terminated(self):
        with self._lock:
            if not self.is_alive:
                # thread not started or already stopped - nothing to do
                return

            # wake the processing thread up
            self._queue.put_nowait(_TERMINATOR)

            timeout = self.options['shutdown_timeout']

            # wait briefly, initially
            initial_timeout = min(0.1, timeout)

            if not self._timed_queue_join(initial_timeout):
                # if that didn't work, wait a bit longer
                # NB that size is an approximation, because other threads may
                # add or remove items
                size = self._queue.qsize()

                print("Bitcaster is attempting to send %i pending notifications"
                      % size)
                print("Waiting up to %s seconds" % timeout)

                if os.name == 'nt':
                    print("Press Ctrl-Break to quit")
                else:
                    print("Press Ctrl-C to quit")

                self._timed_queue_join(timeout - initial_timeout)

            self._thread = None

    def start(self):
        # type: () -> None
        with self._lock:
            try:
                if not self.is_alive:
                    self._thread = threading.Thread(
                        target=self._target, name="bitcaster_sdk.BackgroundWorker"
                    )
                    self._thread.setDaemon(True)
                    self._thread.start()
                    self._thread_for_pid = os.getpid()
            finally:
                atexit.register(self.main_thread_terminated)

    def terminate(self):
        self.terminating = True

    def backoff(self):
        return int(self.options['backoff'] * self.errors)

    def _target(self):
        # type: () -> None
        while not self.terminating:
            callback = self._queue.get()
            logger.debug(f'deque {callback}')
            try:
                if callback is _TERMINATOR:
                    logger.debug("Terminator found. Break")
                    break
                bk = self.backoff()
                sleep(bk)
                try:
                    callback()
                    self.errors = 0
                except (HTTPError, ConnectionError,):
                    logger.error('Reschedule due ConnectionError.')
                    self.errors += 1
                    self._queue.put_nowait(callback)
                except Exception:
                    self.errors += 1
                    logger.error("Failed processing job", exc_info=True)
            finally:
                self._queue.task_done()
            sleep(0)
        logger.debug("Exiting...")
