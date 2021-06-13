import telstra_pn.rest
import telstra_pn.exceptions


class Session:
    def __init__(self,
                 accountid: str = None,
                 username: str = None,
                 password: str = None):
        self.api_session = telstra_pn.rest.ApiSession()

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
        self.token_type = response.get('token_type')
        self.access_token = response.get('access_token')
        self.expires_in = response.get('expires_in')
        self.refresh_token = response.get('refresh_token')
        self.api_session.set_auth(f'Bearer {self.sessionkey}')

    def validate(self):
        response = self.api_session.call_api(
            path='/1.0.0/auth/validatetoken'
        )

        self.useruuid = response.get('userid')
        self.customeruuid = response.get('customerid')
        self.username = response.get('username')
