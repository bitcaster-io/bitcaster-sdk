import re
from typing import Any

from bitcaster_sdk.exceptions import (AuthenticationError, ConfigurationError,
                                      StreamNotFound)

from .logging import logger
from .transport import Transport

client = None


class AbstractClient:
    url_regex = ''

    def parse_url(self, url):
        try:
            m = re.compile(self.url_regex).match(url).groupdict()
            self.options.update(m)
            self.options['base_url'] = self.base_url
            if not m:
                raise ConfigurationError(f'Unable to parse Bitcaster url: "{url}"')
        except Exception as e:
            raise ConfigurationError(f'Unable to parse Bitcaster url: "{url}"" {e}')


class Client(AbstractClient):
    url_regex = r"(?P<schema>https?):\/\/(?P<token>.*)@" \
                r"(?P<host>.*)\/api\/o\/(?P<organization>.*)\/" \
                r"a\/(?P<application>\d+)\/"

    def __init__(self, bae, debug=False, *args, **kwargs):
        # type: (str, bool, *Any, **Any) -> None
        # bae -> Bitcaster Application Endpoint
        self.bae = bae
        self.options = {'debug': debug, 'shutdown_timeout': 10}
        self.parse_url(bae)
        self.transport = Transport(**self.options)

    @property
    def debug(self):
        return self.options['debug']

    @property
    def base_url(self):
        return "{schema}://{host}/api/o/{organization}/a/{application}/".format(**self.options)

    def assert_response(self, response):
        if response.status_code in [401, 403]:
            raise AuthenticationError(f"Invalid token: {response.url}")

        if response.status_code in [404]:
            raise StreamNotFound("Invalid Stream ")

        if response.status_code not in [201, 200]:
            raise ConnectionError(response.status_code, response.url)

    def ping(self):
        response = self.transport.get('/api/system/ping/')
        self.assert_response(response)

    def empty(self):
        return self.transport.thread.empty()

    def queue(self, stream, context, callback=None):
        def send():
            self.send(stream, context)

        self.transport.submit(send)

    def send(self, stream, context):
        if self.debug:
            logger.debug(f'sending to {stream}')
        response = self.transport.post(f's/{stream}/trigger/', context)
        self.assert_response(response)
        return response

    def terminate(self):
        self.transport.thread.terminate()
