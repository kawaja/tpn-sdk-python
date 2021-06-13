from tests.mocks_auth import *  # noqa
from tests.mocks_datacentres import *  # noqa
import re

mock_responses = {
    **mock_auth_responses,  # noqa
    **mock_datacentres_responses  # noqa
}


def setup_mocks(mock, paths):
    for rpath in mock_responses:
        for mpath in paths:
            if re.search(mpath, rpath):
                for (method, status_code) in [('GET', 200),
                                              ('POST', 201),
                                              ('PUT', 200),
                                              ('DELETE', 200)]:
                    if method in mock_responses[rpath]:
                        print(f'adding mock for {method} {rpath}')
                        mock.request(
                            method,
                            rpath,
                            status_code=mock_responses[rpath][method].get(
                                'status_code', status_code),
                            json=mock_responses[rpath][method].get(
                                'response', {})
                        )
