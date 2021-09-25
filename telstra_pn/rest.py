from typing import Any
import requests
from requests_futures.sessions import FuturesSession
from concurrent.futures import Future, as_completed
from telstra_pn import __flags__
from telstra_pn.exceptions import TPNAPIUnavailable, TPNDataError

default_endpoint = 'https://api.pn.telstra.com'
stdargs = {'allow_redirects': False}


class ApiSession():
    def __init__(self):
        self.session = FuturesSession()
        self.debug = __flags__.get('debug_api')
        self.auth = None

    def set_auth(self, auth):
        self.auth = auth

    def call_api(self, **kwargs) -> Any:
        try:
            r = self._call_api(**kwargs).result()
        except BaseException as exc:
            raise TPNAPIUnavailable(exc)

        if self.debug:
            print(f'<-- {r.status_code}')
            print(f'<-- {r.text}')
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise TPNDataError(exc)
        return(r.json())

    def call_apis(self, items: list) -> Any:
        results = []
        futures = [self._call_api(**item) for item in items]

        for future in as_completed(futures):
            try:
                r = future.result()
            except BaseException as exc:
                raise TPNAPIUnavailable(exc)

            if self.debug:
                print(f'<-- {r.status_code}')
                print(f'<-- {r.text}')
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError as exc:
                raise TPNDataError(f'{r.request.url}: {exc}')
            results.append(r.json())

        return results

    def _call_api(self,
                  path: str = None,
                  method: str = 'GET',
                  body: str = None,
                  **kwargs) -> Future:

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

        if method == 'GET':
            return self.session.get(
                f'{default_endpoint}{path}',
                headers=headers,
                **stdargs, **kwargs)

        if method == 'POST':
            return self.session.post(
                f'{default_endpoint}{path}',
                data=body,
                headers=headers,
                **stdargs, **kwargs)

        if method == 'DELETE':
            return self.session.delete(
                f'{default_endpoint}{path}',
                data=body,
                headers=headers,
                **stdargs, **kwargs)

        if method == 'PUT':
            return self.session.put(
                f'{default_endpoint}{path}',
                data=body,
                headers=headers,
                **stdargs, **kwargs)

        raise TPNAPIUnavailable(f'method {method} not implemented')
