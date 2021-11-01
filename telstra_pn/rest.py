from typing import Any
import requests
from requests_futures.sessions import FuturesSession
from concurrent.futures import Future, as_completed
import datetime
from telstra_pn import __flags__
from telstra_pn.exceptions import TPNAPIUnavailable, TPNDataError

default_endpoint = 'https://api.pn.telstra.com'
stdargs = {'allow_redirects': False}


class ApiSession():
    def __init__(self):
        self.session = FuturesSession(max_workers=20)
        self.debug = __flags__.get('debug_api')
        self.auth = None

    def set_auth(self, auth):
        self.auth = auth

    def call_api(self, **kwargs) -> Any:
        try:
            r = self._call_api(**kwargs).result()
        except BaseException as exc:
            raise TPNAPIUnavailable(exc) from None

        if self.debug:
            print(f'<-- {r.status_code}')
            print(f'<-- {r.text}')
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise TPNDataError(exc) from None
        return(r.json())

    def call_apis(self, items: list) -> Any:
        results = []
        futures = [
            {
                'starttime': datetime.datetime.now(),
                'future': self._call_api(**item)
            }
            for item in items]

        seq = 0
        for future in as_completed([f['future'] for f in futures]):
            try:
                r = future.result()
                future.endtime = datetime.datetime.now()
                future.seq = seq
                seq += 1
            except BaseException as exc:
                raise TPNAPIUnavailable(exc) from None

            if self.debug:
                print(f'<-- {r.status_code}')
                print(f'<-- {r.text}')
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError as exc:
                raise TPNDataError(exc) from None
            results.append(r.json())

        if self.debug:
            for call in sorted(futures, key=lambda x: x['starttime']):
                total_elapsed = (call["future"].endtime - call["starttime"]
                                 ) / datetime.timedelta(microseconds=1)
                query_time = (call["future"].result().elapsed /
                              datetime.timedelta(microseconds=1))
                print(
                    f'{call["future"].result().request.url}, '
                    f'{call["future"].seq}, '
                    f'{call["starttime"]}, '
                    f'{call["future"].endtime}, '
                    f'{total_elapsed}, ',
                    f'{query_time}'
                )

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

        raise TPNAPIUnavailable(f'method {method} not implemented') from None
