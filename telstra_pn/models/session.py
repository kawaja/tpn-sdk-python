import telstra_pn.rest
from urllib.parse import urlencode
from telstra_pn.exceptions import TPNDataError, TPNInvalidLogin
from telstra_pn.models.tpn_model import TPNModel


def without_getattr(func):
    def wrapper(*args, **kwargs):
        print(f'before {func.__name__}')
        oldgetattr = args[0].__getattr__
        del args[0].__getattr__
        ret = func(*args, **kwargs)
        args[0].__getattr__ = oldgetattr
        print(f'after {func}')
        print(f'wrapper: {ret}')
        return ret
    return wrapper


class Session(TPNModel):
    def __init__(self,
                 accountid: str = None,
                 username: str = None,
                 password: str = None,
                 otp: str = None) -> None:
        super().__init__(None)
        self.api_session = telstra_pn.rest.ApiSession()
        self.refresh_if_null = ['customeruuid']
        self._url_path = '/1.0.0/auth/validatetoken'

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

    # def _get_data(self) -> None:
    #     response = self.api_session.call_api(
    #         path='/1.0.0/auth/validatetoken'
    #     )

    #     return response

    def _update_data(self, data: dict) -> None:
        data['useruuid'] = data['userid']
        data['customeruuid'] = data['customerid']
        del data['userid']
        del data['customerid']
        self.data = {**self.data, **data}

    @property
    def datacentres(self) -> telstra_pn.Datacentres:
        if getattr(self, '_datacentres', None) is None:
            self._datacentres = telstra_pn.Datacentres(self)

        return getattr(self, '_datacentres', None)

    @property
    @without_getattr
    def p2plinks(self) -> telstra_pn.P2PLinks:
        if self._p2plinks is None:
            self._p2plinks = telstra_pn.P2PLinks(self)

        print(self)
        return self._p2plinks

    @property
    @without_getattr
    def endpoints(self) -> telstra_pn.Endpoints:
        if getattr(self, '_endpoints', None) is None:
            self._endpoints = telstra_pn.Endpoints(self)

        return getattr(self, '_endpoints', None)

    @property
    def topologies(self) -> telstra_pn.Topologies:
        if getattr(self, '_topologies', None) is None:
            self._topologies = telstra_pn.Topologies(self)

        return getattr(self, '_topologies', None)
