import requests
from telstra_pn import __flags__
import telstra_pn.exceptions

default_endpoint = 'https://api.pn.telstra.com'
stdargs = {'allow_redirects': False}


class ApiSession():
    def __init__(self):
        self.session = requests.Session()
        self.auth = None
        self.debug = __flags__.get('debug')

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

        if method == 'GET':
            if self.debug:
                print(f'GET {default_endpoint}{path} [{headers}]')
            r = requests.get(
                f'{default_endpoint}{path}',
                headers=headers,
                **stdargs, **kwargs)
            if r is not None:
                if self.debug:
                    print(f'<-- {r.status_code}')
                    print(f'<-- {r.text}')
                r.raise_for_status()
                return(r.json())
            raise telstra_pn.exceptions.TPNAPIUnavailable()

        if method == 'POST':
            if self.debug:
                print(f'POST {default_endpoint}{path}')
                print(f'-->{body}')
            r = requests.post(
                f'{default_endpoint}{path}',
                data=body,
                headers=headers,
                **stdargs, **kwargs)
            if r is not None:
                if self.debug:
                    print(f'<-- {r.status_code}')
                    print(f'<-- {r.text}')
                r.raise_for_status()
                return(r.json())
            raise telstra_pn.exceptions.TPNAPIUnavailable()
