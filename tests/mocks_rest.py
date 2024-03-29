from requests.exceptions import ConnectTimeout

mock_rest_responses = {
    '/testpath': {
        ('default', 'POST'): {
            'json': {
                'testpost': True
            }
        },
        ('default', 'GET'): {
            'json': {
                'testget': True
            }
        },
        ('default', 'DELETE'): {
            'json': {
                'testdelete': True
            }
        },
        ('default', 'PUT'): {
            'json': {
                'testput': True
            }
        },
        ('default', 'PATCH'): {
            'json': {
                'testpatch': True
            }
        },
        ('500', 'GET'): {
            'status_code': 500
        },
        ('500', 'POST'): {
            'status_code': 500
        },
        ('500', 'PUT'): {
            'status_code': 500
        },
        ('500', 'DELETE'): {
            'status_code': 500
        },
        ('timeout', 'GET'): {
            'exc': ConnectTimeout
        },
        ('timeout', 'POST'): {
            'exc': ConnectTimeout
        },
        ('timeout', 'PUT'): {
            'exc': ConnectTimeout
        },
        ('timeout', 'DELETE'): {
            'exc': ConnectTimeout
        }
    }
}
