import telstra_pn
from tests.mocks_rest import *  # noqa
from tests.mocks_auth import *  # noqa
from tests.mocks_datacentres import *  # noqa
from tests.mocks_endpoints import *  # noqa
from tests.mocks_p2plinks import *  # noqa
from tests.mocks_endpoints import *  # noqa
from tests.mocks_topologies import *  # noqa
from requests_mock.contrib.fixture import Fixture
import re

mock_responses = {
    **mock_rest_responses,  # noqa
    **mock_auth_responses,  # noqa
    **mock_datacentres_responses,  # noqa
    **mock_endpoints_responses,  # noqa
    **mock_p2plinks_responses,  # noqa
    **mock_topologies_responses,  # noqa
#    **mock_endpoints_responses  # noqa
}


default_code = {
    'GET': 200,
    'POST': 201,
    'PUT': 200,
    'DELETE': 200
}


def setup_mocks(mock: Fixture, mockspecs: tuple):
    apimocks = {}
    for mockspec in mockspecs:
        mockspec = list(mockspec)
        if len(mockspec) == 1:
            mockspec.append('GET')
        if len(mockspec) == 2:
            mockspec.append('default')
        if telstra_pn.__flags__['debug_mocks']:
            print(f'looking for mock for: {mockspec}')
        (mpathpat, mmethod, mvariant) = mockspec
        for rpath in mock_responses:
            if telstra_pn.__flags__['debug_mocks']:
                print(f'searching {rpath}: ')
            if re.search(mpathpat, rpath):
                if (mvariant, mmethod) in mock_responses[rpath]:
                    if telstra_pn.__flags__['debug_mocks']:
                        print(f'+ mmethod: {mmethod}, rpath: {rpath}')
                    apimocks.setdefault((mmethod, rpath), [])
                    if telstra_pn.__flags__['debug_mocks']:
                        print(f'+ mvariant: {mvariant}, apimocks: {apimocks}')
                    apimocks[(mmethod, rpath)].append(
                        mock_responses[rpath][(mvariant, mmethod)])

    for rkey in apimocks.keys():
        mock_response = apimocks[rkey]
        (method, path) = rkey

        # fill in missing status codes
        for item in mock_response:
            if 'exc' not in item:
                item['status_code'] = (
                    item.get('status_code') or default_code.get(method))

        if telstra_pn.__flags__['debug_mocks']:
            print(f'adding mock for {method} {path} ')

        # create the mocks
        mock.request(method, path, mock_response)


def mock_history(mock: Fixture):
    history = '\n'

    for item in mock.request_history:
        history = f'{history}{item.method} {item.url}\n'

    return history
