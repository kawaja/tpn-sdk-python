from requests.models import HTTPError


class TPNAPIUnavailable(RuntimeError):
    pass


class TPNDataError(RuntimeError):
    def __init__(self, http_error: HTTPError):
        #        print(f'http_error: {http_error.__dict__}')
        #        print(f'http_error.response: {http_error.response.__dict__}')
        self.status_code = int(http_error.response.status_code)
        self.error = http_error

    def __repr__(self):
        return str(f'{self.error}, '
                   f'url={self.error.request.url}, '
                   f'statuscode={self.status_code}')


class TPNInvalidLogin(RuntimeError):
    pass


class TPNLogicalError(RuntimeError):
    pass


class TPNRefreshInconsistency(TPNLogicalError):
    pass


class TPNLibraryInternalError(TPNLogicalError):
    '''The TPN Library has an implementation issue'''
