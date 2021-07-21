from contextlib import contextmanager
from urllib.parse import urlparse

import requests

from .logging import logger
from .worker import BackgroundWorker, SynchronousWorker


class Transport:
    def __init__(self, base_url, token, **kwargs):
        self.session = requests.Session()
        self.base_url = base_url
        self.debug = kwargs.get('debug')
        self.session.headers.update({'Authorization': f'Key {token}',
                                     'User-Agent': 'Bitcaster-SDK'})
        self.conn = urlparse(base_url)
        # self.thread = BackgroundWorker()
        self.thread = SynchronousWorker()
        self.thread.start()

    def get_url(self, path):
        return f"{self.conn.scheme}://{self.conn.netloc}{self.conn.path}{path}"

    @contextmanager
    def with_headers(self, values: dict):
        c = dict(self.session.headers)
        self.session.headers.update(values)
        yield
        self.session.headers = c

    def get(self, path):
        if self.debug:
            logger.info(f"get {path}")

        return self.session.get(self.get_url(path))

    def post(self, path, arguments):
        if self.debug:
            logger.info(f"post {path}")
        with self.with_headers({'Content-Type': 'application/json'}):
            return self.session.post(self.get_url(path), json=arguments)

    def submit(self, callback):
        self.thread.submit(callback)

    def terminate(self):
        self.thread.terminate()
