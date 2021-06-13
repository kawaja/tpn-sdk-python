MockAuthSessionKey = '76f7e712abd55921d4bcad43a92c20'
MockAuthCustomerUUID = 'd632c88d-2555-440d-9ade-a850e91cd3a8'
MockAuthUserUUID = '290fff0a-61dc-42ca-ba54-0efa4b519eeb'
MockAuthUsername = 'abcdef'
MockAuthPassword = 'fdjsak'
MockAuthAccountid = '14322314'

mock_auth_responses = {
    '/is/1.0.0/generatetoken': {
        'POST': {
            'response': {
                'token_type': 'bearer',
                'expires_in': 6899,
                'refresh_token': '903c481cb5dffcfc52e292867075037',
                'access_token': MockAuthSessionKey
            },
            'status_code': 200
        }
    },
    '/1.0.0/auth/validatetoken': {
        'GET': {
            'response': {
                'customerid': MockAuthCustomerUUID,
                'userid': MockAuthUserUUID,
                'username': f'{MockAuthAccountid}/{MockAuthUsername}'
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
