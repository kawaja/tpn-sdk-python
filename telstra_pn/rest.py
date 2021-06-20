import requests
from telstra_pn import __flags__
from telstra_pn.exceptions import TPNAPIUnavailable, TPNDataError

default_endpoint = 'https://api.pn.telstra.com'
stdargs = {'allow_redirects': False}


class ApiSession():
    def __init__(self):
        self.session = requests.Session()
        self.debug = __flags__.get('debug')
        self.auth = None

    def set_auth(self, auth):
        self.auth = auth

    def call_api(self,
                 path: str = None,
                 method: str = 'GET',
                 body: str = None,
                 **kwargs):

        headers = {}

        if 'headers' in kwargs:
            headers = {**(kwargs['headers'])}
            del kwargs['headers']

        if not kwargs.get('noauth'):
            headers['authorization'] = self.auth

        if 'noauth' in kwargs:
            del kwargs['noauth']

        method = method.upper()

        if self.debug:
            print(f'{method} {default_endpoint}{path} [{headers}]')

        r = None

        if method == 'GET':
            try:
                r = requests.get(
                    f'{default_endpoint}{path}',
                    headers=headers,
                    **stdargs, **kwargs)
            except BaseException as exc:
                raise TPNAPIUnavailable(exc)

        if method == 'POST':
            try:
                r = requests.post(
                    f'{default_endpoint}{path}',
                    data=body,
                    headers=headers,
                    **stdargs, **kwargs)
            except BaseException as exc:
                raise TPNAPIUnavailable(exc)

        if method == 'DELETE':
            try:
                r = requests.delete(
                    f'{default_endpoint}{path}',
                    data=body,
                    headers=headers,
                    **stdargs, **kwargs)
            except BaseException as exc:
                raise TPNAPIUnavailable(exc)

        if method == 'PUT':
            try:
                r = requests.put(
                    f'{default_endpoint}{path}',
                    data=body,
                    headers=headers,
                    **stdargs, **kwargs)
            except BaseException as exc:
                raise TPNAPIUnavailable(exc)

        if r is None:
            raise TPNAPIUnavailable(f'method {method} not implemented')

        if self.debug:
            print(f'<-- {r.status_code}')
            print(f'<-- {r.text}')
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise TPNDataError(exc)
        return(r.json())
