from json import JSONDecodeError

import requests


class StreamNotFound(Exception):
    pass


class ConfigurationError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class RateLimited(Exception):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return 'Too many requests. Please retry in %s' % humanfriendly.format_timespan(self.data['time_left'],
                                                                                       max_units=1)


class RemoteAPIException(Exception):
    message = 'Error %(status_code)s on remote server: %(body)s'

    def __init__(self, response: requests.Response, **extra):
        self.response = response
        self.message = extra.pop('message', self.message)
        self.extra = extra

    @property
    def status(self):
        return self.response.status_code

    def __str__(self):
        params = dict(self.extra)
        params['response'] = self.response
        params['status_code'] = self.response.status_code

        try:
            params['body'] = str(self.response.json())
        except Exception:
            params['body'] = self.response.content

        return self.message % params

    def __repr__(self):
        return self.__str__()


class RemoteValidationError(RemoteAPIException):
    message = 'Error %(status_code)s on remote server: %(detail)s'

    def json(self):
        try:
            return self.response.json()
        except JSONDecodeError:
            return {}

    def __str__(self):
        info = self.json()
        return self.message % {'status_code': self.response.status_code,
                               'detail': info.get('error', '')}

class Http404(RemoteAPIException):
    pass
