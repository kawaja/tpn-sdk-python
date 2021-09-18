import telstra_pn.rest
from urllib.parse import urlencode
from telstra_pn.exceptions import TPNDataError, TPNInvalidLogin
from telstra_pn.models.tpn_model import TPNModel


class Session(TPNModel):
    def __init__(self,
                 accountid: str = None,
                 username: str = None,
                 password: str = None,
                 otp: str = None) -> None:
        super().__init__(None)
        self.api_session = telstra_pn.rest.ApiSession()
        self.refresh_if_null = ['customeruuid']
        self._keyname_mappings = [
            ('useruuid', 'userid'),
            ('customeruuid', 'customerid')
        ]
        self._url_path = '/1.0.0/auth/validatetoken'

        self._datacentres = None
        self._p2plinks = None
        self._endpoints = None
        self._topologies = None

        self.login(accountid, username, password, otp)

    def login(self, accountid, username, password, otp):
        if not accountid:
            raise ValueError('Session: accountid is required')

        if not username:
            raise ValueError('Session: username is required')

        if not password:
            raise ValueError('Session: password is required')

        login = {
            'grant_type': 'password',
            'username': f'{accountid}/{username}',
            'password': password
        }
        if otp is not None:
            login['otp'] = otp

        try:
            response = self.api_session.call_api(
                path='/is/1.0.0/generatetoken',
                method='POST',
                noauth=True,
                body=urlencode(login),
                headers={'content-type': 'application/x-www-form-urlencoded'}
            )
        except TPNDataError as exc:
            print(f'session exception: {exc}')
            if exc.status_code == 412:
                raise TPNInvalidLogin()
            raise(exc)

        if self.debug:
            print(f'Session.__init__.response: {response}')

        self.sessionkey = response.get('access_token')
        self.api_session.set_auth(f'Bearer {self.sessionkey}')
        self.data = {**self.data, **response}

    def validate(self) -> None:
        self.refresh()

    def _update_data(self, data: dict) -> None:
        self.data = {**self.data, **data}
        self._update_keys(data)

    @property
    def datacentres(self) -> telstra_pn.Datacentres:
        if getattr(self, '_datacentres', None) is None:
            self._datacentres = telstra_pn.Datacentres(self)

        return getattr(self, '_datacentres', None)

    @property
    def p2plinks(self) -> telstra_pn.P2PLinks:
        if self._p2plinks is None:
            self._p2plinks = telstra_pn.P2PLinks(self)

        print(self)
        return self._p2plinks

    @property
    def endpoints(self) -> telstra_pn.Endpoints:
        if getattr(self, '_endpoints', None) is None:
            self._endpoints = telstra_pn.Endpoints(self)

        return getattr(self, '_endpoints', None)

    @property
    def topologies(self) -> telstra_pn.Topologies:
        if getattr(self, '_topologies', None) is None:
            self._topologies = telstra_pn.Topologies(self)

        return getattr(self, '_topologies', None)
