import re

MockSessionKey = '76f7e712abd55921d4bcad43a92c20'
MockCustomerUUID = 'd632c88d-2555-440d-9ade-a850e91cd3a8'
MockUserUUID = '290fff0a-61dc-42ca-ba54-0efa4b519eeb'
MockUsername = 'abcdef'
MockPassword = 'fdjsak'
MockAccountid = '14322314'

mock_responses = {
    '/is/1.0.0/generatetoken': {
        'POST': {
            'response': {
                'token_type': 'bearer',
                'expires_in': 6899,
                'refresh_token': '903c481cb5dffcfc52e292867075037',
                'access_token': MockSessionKey
            },
            'status_code': 200
        }
    },
    '/1.0.0/auth/validatetoken': {
        'GET': {
            'response': {
                'customerid': MockCustomerUUID,
                'userid': MockUserUUID,
                'username': f'{MockAccountid}/{MockUsername}'
            },
            'status_code': 200
        }
    },
    'nopath': {
        'POST': {
            'response': {
                'testpost': True
            }
        },
        'GET': {
            'response': {
                'testget': True
            }
        }
    }
}


def setup_mocks(mock, paths):
    for rpath in mock_responses:
        for mpath in paths:
            print(f'rpath={rpath}, mpath={mpath}')
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
