from requests.models import HTTPError


class TPNAPIUnavailable(RuntimeError):
    pass


class TPNDataError(RuntimeError):
    def __init__(self, http_error: HTTPError):
        self.status_code = int(http_error.response.status_code)


class TPNInvalidLogin(RuntimeError):
    pass


class TPNLogicalError(RuntimeError):
    pass


class TPNRefreshInconsistency(TPNLogicalError):
    pass


class TPNLibraryInternalError(TPNLogicalError):
    '''The TPN Library has an implementation issue'''
