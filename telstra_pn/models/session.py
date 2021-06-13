import telstra_pn.rest
import telstra_pn.exceptions
from typing import Any


class Session:
    def __init__(self,
                 accountid: str = None,
                 username: str = None,
                 password: str = None):
        self.api_session = telstra_pn.rest.ApiSession()
        self.data = {}

        if not accountid:
            raise ValueError('Session: accountid is required')

        if not username:
            raise ValueError('Session: username is required')

        if not password:
            raise ValueError('Session: password is required')

        response = self.api_session.call_api(
            path='/is/1.0.0/generatetoken',
            method='POST',
            noauth=True,
            body=f'grant_type=password&'
                 f'username={accountid}/{username}&password={password}',
            headers={'content-type': 'application/x-www-form-urlencoded'}
        )

        print(f'Session.__init__.response: {response}')

        self.sessionkey = response.get('access_token')
        self.api_session.set_auth(f'Bearer {self.sessionkey}')
        self.data = {**self.data, **response}

    def validate(self):
        response = self.api_session.call_api(
            path='/1.0.0/auth/validatetoken'
        )

        response['useruuid'] = response['userid']
        response['customeruuid'] = response['customerid']
        del response['userid']
        del response['customerid']
        self.data = {**self.data, **response}

    def __getattr__(self, name: str) -> Any:
        d = self.data
        if name in d:
            return d[name]
