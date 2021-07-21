import json
from functools import wraps
from requests import Session
from urllib.parse import ParseResult, urlencode, urlparse

from .client import AbstractClient
from .exceptions import RemoteAPIException, Http404, RateLimited, RemoteValidationError

from .logging import logger


def avoid_double_slash(path):
    parts = path.split('/')
    not_empties = [part for part in parts if part]
    return '/'.join(not_empties)


def extends(f):
    @wraps(f)
    def _inner(*args, **kwargs):
        serialize = kwargs.pop('serialize', None)
        fields = kwargs.pop('_fields', None)
        raw = kwargs.pop('_raw', None)
        ret = f(*args, **kwargs)
        if ret.status_code >= 500:
            raise RemoteAPIException(ret)
        if ret.status_code == 429:
            raise TooManyRequestsError(ret)
        if ret.status_code >= 400:
            logger.error(ret.content)
            raise RemoteValidationError(ret)
        if raw:
            return ret
        data = ret.json()
        if fields:
            data = [{k: record[k] for k in fields} for record in data]
        if serialize:
            data = mark_safe(json.dumps(data))
        return data

    return _inner


class Bitcaster(AbstractClient):
    url_regex = r"(?P<schema>https?):\/\/(?P<token>.*)@" \
                r"(?P<host>.*)\/api\/o\/(?P<organization>.*)\/"

    def __init__(self, sdt, user_agent='Bitcaster-API'):
        self.sdt = sdt
        self.options = {}
        self.parse_url(sdt)
        # self.api_url = api_url
        # parts: ParseResult = urlparse(api_url)
        # self.host = f'{parts.scheme}://{parts.netloc}'
        self.session = Session()
        self.session.headers.update({'Authorization': f'Token {self.options["token"]}',
                                     'Content-Type': 'application/json',
                                     'Accept-Language': 'it-IT',
                                     'User-Agent': user_agent})
        self.base_api = None
        self.organization = None
        self.slug = None
        self.conn = None
        self.host = None
        self.calls = []

    @property
    def base_url(self):
        return "{schema}://{host}/api/o/{organization}/".format(**self.options)

    def init(self):
        try:
            url = "{schema}://{host}/api/system/ping/".format(**self.options)
            res = self.session.get(url)
            if res.status_code != 200:
                raise Exception(f'Error {res.status_code} connecting API: {url}')
            data = res.json()
            self.base_api = data['base_api']
            self.slug = data['slug']
            self.organization = data['org']
            self.conn = urlparse(self.base_url)
            self.host = f'{self.conn.scheme}://{self.conn.netloc}'
        except Exception as e:
            logger.exception(e)
            raise ConnectionError(e)

    def get_page(self, path):
        if not self.conn:
            self.init()
        if '?' in path:
            path, args = path.split('?', 1)
        else:
            args = ''
        return f'{self.base_url}{avoid_double_slash("/" + path)}/?{args}'

    def get_url(self, path):
        if not self.conn:
            self.init()
        if path.startswith('http'):
            return path
        if '?' in path:
            path, args = path.split('?', 1)
        else:
            args = ''
        return f'{self.conn.scheme}://{self.conn.netloc}/{avoid_double_slash(self.conn.path + path)}/?{args}'

    # def ping(self):
    #     res = self._get('/')
    #     if res.status_code != 200:
    #         raise RemoteAPIException(res)

    def _invoke(self, method, path, arguments=None):
        func = getattr(self.session, method.lower(), )
        full_url = self.get_url(path)
        try:
            self.calls.append(full_url)
            return func(full_url, json=arguments)
        except Exception as e:
            logger.exception(e)
            raise Exception(f'Unable to contact remote server: {full_url}')

    def _get(self, path):
        return self._invoke('get', path)

    def _post(self, path, arguments):
        return self._invoke('post', path, arguments)

    def _patch(self, path, arguments):
        return self.session.patch(self.get_url(path), json=arguments)

    def _delete(self, path):
        full_url = self.get_url(path)
        self.calls.append(full_url)
        return self.session.delete(full_url)

    def _put(self, path, arguments):
        return self._invoke('put', path, arguments)

    def add_member(self, **data):
        return self._post('m/', data)

    def update_member(self, id, **data):
        return self._put(f'm/{id}/', data)

    def update_extras(self, member_id, **data):
        return self._put(f'm/{member_id}/extras/', data)

    def delete_member(self, id):
        return self._delete(f'm/{id}/')

    def get_members(self, **filters):
        return self._get(f'm/?{urlencode(filters)}')

    def get_member(self, id):
        return self._get(f'm/{id}/')

    def filter_members(self, **filters):
        return self._get(f'm/?{urlencode(filters)}')

    def get_channels(self, **filters):
        ret = self._get(f'c/?{urlencode(filters)}')
        return ret.json()

    def get_assignments(self, member_id, **filters):
        res = self._get(f'm/{member_id}/aa/?{urlencode(filters)}')
        return res.json()

    @extends
    def get_assignment(self, member_id, asm_id):
        return self._get(f'm/{member_id}/aa/{asm_id}/')

    @extends
    def send_code_for_assignment(self, member_id, asm_id, **extras):
        payload = dict(extras)
        return self._post(f'm/{member_id}/aa/{asm_id}/send_code/', payload)

    @extends
    def send_code_for_channel(self, member_id, address_id, channel_id, **extras):
        payload = dict(extras)
        payload['channel_id'] = channel_id
        return self._post(f'm/{member_id}/a/{address_id}/send_code/', payload)

    def validate_remote_address(self, otp):
        url = f'{self.host}/validate/?r=json&k={otp}'
        return self._get(url)

    @extends
    def verify_assignment(self, member_id, assignment_id):
        return self._post(f'm/{member_id}/aa/{assignment_id}/verify/', {})

    @extends
    def verify_multi(self, member_id, code):
        return self._post(f'm/{member_id}/aa/verify_multi/', {'code': code})

    @extends
    def verify_code(self, member_id, assignment_id):
        return self._post(f'm/{member_id}/aa/{assignment_id}/verify/', {})

    # @extends
    # def verify_assignment_(self, member_id, assignment_id):
    #     return self._post(f'm/{member_id}/aa/{assignment_id}/verify/', {})

    # def verify_assignment(self, member_id, address_id, channel_id, code):
    # return self._post(f'm/{member_id}/a/{address_id}/verify_code/',
    #                   {'channel_id': channel_id,
    #                    'code': code})

    # @extends
    def create_assignment(self, member_id, **data):
        return self._post(f'm/{member_id}/aa/', data)

    @extends
    def patch_assignment(self, member_id, id, **data):
        return self._patch(f'm/{member_id}/aa/{id}/', data)

    @extends
    def filter_addresses(self, member_id, **filters):
        return self._get(f'm/{member_id}/a/?{urlencode(filters)}')

    def get_addresses(self, member_id):
        return self.filter_addresses(member_id)

    def get_org_addresses(self, **filters):
        return self._get(f'addrs/?{urlencode(filters)}')

    def delete_org_address(self, id):
        return self._delete(f'addrs/{id}/')

    @extends
    def get_address(self, member_id, id):
        return self._get(f'm/{member_id}/a/{id}/')

    @extends
    def validate_address(self, member_id, id, **data):
        return self._post(f'm/{member_id}/a/{id}/validate/', data)

    @extends
    def patch_address(self, member_id, id, **data):
        return self._patch(f'm/{member_id}/a/{id}/', data)

    def subscribe(self, app_pk, stream_pk, assignment):
        return self._post(f'a/{app_pk}/s/{stream_pk}/subscribe/',
                          {'assignment': assignment})

    def get_subscribers(self, app_pk, stream_pk):
        return self._get(f'a/{app_pk}/s/{stream_pk}/s/')

    def set_subscriptions(self, app_pk, stream_pk, assignments: [int]):
        return self._post(f'a/{app_pk}/s/{stream_pk}/set_subscriptions/',
                          {'assignments': assignments})

    def add_address(self, member_id, **data):
        if not member_id:
            raise ValueError(f'Invalid value "{member_id}" for member_id')
        return self._post(f'm/{member_id}/a/', data)

    def delete_address(self, member_id, pk):
        return self._delete(f'm/{member_id}/a/{pk}/')

    def get_application(self, app_id):
        # http://localhost:8000/api/v0/o/sos/a/50/s/
        ret = self._get(f'a/{app_id}/')
        if ret.status_code == 404:
            raise Http404()
        return ret

    def create_application(self, **data):
        return self._post('a/', data)

    def delete_application(self, id):
        return self._delete(f'a/{id}/')

    def filter_applications(self, **filters):
        return self._get(f'a/?{urlencode(filters)}')

    def get_stream(self, app_id, pk):
        # http://localhost:8000/api/v0/o/sos/a/50/s/
        ret = self._get(f'a/{app_id}/s/{pk}/')
        return ret

    def delete_stream(self, app_id, pk):
        # http://localhost:8000/api/v0/o/sos/a/50/s/
        ret = self._delete(f'a/{app_id}/s/{pk}/')
        if ret.status_code == 404:
            raise Http404
        if ret.status_code != 204:
            raise RemoteAPIException(ret)
        return ret

    def filter_streams(self, app_id, **filters):
        ret = self._get(f'a/{app_id}/s/?{urlencode(filters)}')
        return ret.json()

    def trigger(self, app_id, pk, payload):
        # http://localhost:8000/api/v0/o/sos/a/50/s/
        ret = self._post(f'a/{app_id}/s/{pk}/trigger/', payload)
        return ret

    def create_stream(self, app_id, **data):
        # http://localhost:8000/api/v0/o/sos/a/50/s/
        # if 'channels' not in data:
        #     data['channels'] = [a['id'] for a in self.get_channels()]
        res = self._post(f'a/{app_id}/s/', data)
        if res.status_code not in [201, 409]:
            raise RemoteAPIException(res)

        return res

    def update_stream(self, app_id, stream_id, **data):
        # http://localhost:8000/api/v0/o/sos/a/50/s/
        # if 'channels' not in data:
        #     data['channels'] = [a['id'] for a in self.get_channels()]
        res = self._patch(f'a/{app_id}/s/{stream_id}/', data)
        if res.status_code == 404:
            raise Http404
        if res.status_code != 200:
            raise RemoteAPIException(res)
        return res

