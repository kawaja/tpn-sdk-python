import telstra_pn.rest
from telstra_pn.exceptions import TPNDataError, TPNInvalidLogin
from telstra_pn.models.tpn_model import TPNModel


class Session(TPNModel):
    def __init__(self,
                 accountid: str = None,
                 username: str = None,
                 password: str = None) -> None:
        super().__init__(None)
        self.api_session = telstra_pn.rest.ApiSession()
        self.refresh_if_null = ['customeruuid']

        self._datacentres = None
        self._p2plinks = None
        self._endpoints = None
        self._topologies = None

        if not accountid:
            raise ValueError('Session: accountid is required')

        if not username:
            raise ValueError('Session: username is required')

        if not password:
            raise ValueError('Session: password is required')

        try:
            response = self.api_session.call_api(
                path='/is/1.0.0/generatetoken',
                method='POST',
                noauth=True,
                body=f'grant_type=password&'
                     f'username={accountid}/{username}&password={password}',
                headers={'content-type': 'application/x-www-form-urlencoded'}
            )
        except TPNDataError as exc:
            if exc.status_code == 412:
                raise TPNInvalidLogin()
            raise(exc)

        if self.debug:
            print(f'Session.__init__.response: {response}')

        self.sessionkey = response.get('access_token')
        self.api_session.set_auth(f'Bearer {self.sessionkey}')
        self.data = {**self.data, **response}

    def validate(self) -> None:
        self.get_data()

    def get_data(self) -> None:
        response = self.api_session.call_api(
            path='/1.0.0/auth/validatetoken'
        )

        response['useruuid'] = response['userid']
        response['customeruuid'] = response['customerid']
        del response['userid']
        del response['customerid']
        self.data = {**self.data, **response}

    # debugging note:
    # if an AttributeError occurs within the setup of any of these
    # models, it will be re-raised and appear as if the model itself
    # does not exist. Use the __flags__['debug_getattr'] flag to debug
    @property
    def datacentres(self) -> telstra_pn.Datacentres:
        if self._datacentres is None:
            self._datacentres = telstra_pn.Datacentres(self)

        return self._datacentres

    @property
    def p2plinks(self) -> telstra_pn.P2PLinks:
        if self._p2plinks is None:
            self._p2plinks = telstra_pn.P2PLinks(self)

        return self._p2plinks

    @property
    def endpoints(self) -> telstra_pn.Endpoints:
        if self._endpoints is None:
            self._endpoints = telstra_pn.Endpoints(self)

        return self._endpoints

    @property
    def topologies(self) -> telstra_pn.Topologies:
        if self._topologies is None:
            self._topologies = telstra_pn.Topologies(self)

        return self._topologies
