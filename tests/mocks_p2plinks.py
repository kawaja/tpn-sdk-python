from tests.mocks_endpoints import MockEndpoint1UUID, MockEndpoint2UUID
from tests.mocks_auth import MockAuthCustomerUUID
from copy import deepcopy

MockLink1ID = '470c122868ab4af9'
MockLink2ID = 'ceb4c87dcb1e47ab'
MockLink3ID = '3503990657974fe0'

link1 = {
    "description": "Test link #1",
    "latency": "2",
    "linkid": MockLink1ID,
    "contracts": [],
    "tag": "production",
    "interfacetypes": [],
    "connections": [MockEndpoint1UUID, MockEndpoint2UUID],
    "type": "0",
    "linkStatus": 1,
    "enabled": None,
    "cp_uuid": None,
    "billing-id": "6dc48db4-ea9a-485b-a1f8-21dabd33f002",
    "is_protected": False,
    "primary_flow_id": None,
    "protected_latency": None,
    "protected_path_linkid": None,
    "creationDate": None,
    "latency_value": 0,
    "protected_latency_value": None,
    "delete_connections": [
        MockEndpoint1UUID
    ]
}

link2_contract1 = {
    "contractid": f'{MockLink2ID}.1',
    "duration": 3600,
    "bandwidth": 500,
    "price": 78,
    "contractStatus": 8,
    "version": 2,
    "deletedtimestamp": 0,
    "currencyCode": "AUD",
    "contractVersionId": 1,
    "renewedVersion": 2,
    "currencyID": "18",
    "renewal-option": "1",
    "contract-start-time": 1535330427000,
    "contract-end-time": 1535334026000
}

link2_contract1_extra = {
    "description": "Test link #2",
    "latency": "1",
    "linkid": MockLink2ID,
    "connection": [MockEndpoint1UUID, MockEndpoint2UUID],
    "tag": "production",
    "type": "0",
    "protected_latency": None,
    "latency_value": 0,
    "protected_latency_value": None,
    "billing-id": "6dc48db4-ea9a-485b-a1f8-21dabd33f002",
}

link2 = {
    "description": "Test link #2",
    "latency": "1",
    "linkid": MockLink2ID,
    "contracts": [link2_contract1],
    "tag": "production",
    "interfacetypes": [],
    "connections": [MockEndpoint1UUID, MockEndpoint2UUID],
    "type": "0",
    "linkStatus": 1,
    "cp_uuid": None,
    "billing-id": "6dc48db4-ea9a-485b-a1f8-21dabd33f002",
    "is_protected": False,
    "primary_flow_id": None,
    "protected_latency": None,
    "protected_path_linkid": None,
    "creationDate": None,
    "latency_value": 0,
    "protected_latency_value": None,
    "delete_connections": []
}

link3_contract1 = {
    "contractid": f'{MockLink3ID}.1',
    "duration": 3600,
    "bandwidth": 500,
    "price": 39,
    "contractStatus": 8,
    "version": 1,
    "deletedtimestamp": 0,
    "currencyCode": "AUD",
    "contractVersionId": 1,
    "renewedVersion": 2,
    "currencyID": "18",
    "renewal-option": "1",
    "contract-start-time": 1535330427000,
    "contract-end-time": 1535334026000
}

link3 = {
    "description": "Test link #3",
    "latency": "1",
    "linkid": MockLink3ID,
    "contracts": [link3_contract1],
    "tag": "production",
    "interfacetypes": [],
    "connections": [MockEndpoint1UUID, MockEndpoint2UUID],
    "type": "0",
    "linkStatus": 1,
    "cp_uuid": None,
    "billing-id": "6dc48db4-ea9a-485b-a1f8-21dabd33f002",
    "is_protected": False,
    "primary_flow_id": None,
    "protected_latency": None,
    "protected_path_linkid": None,
    "creationDate": None,
    "latency_value": 0,
    "protected_latency_value": None,
    "delete_connections": [
    ]
}

link3_contract_delete = deepcopy(link3)
link3_contract_delete['contracts'] = []

mock_p2plinks_responses = {
    f"/1.0.0/inventory/links/customer/{MockAuthCustomerUUID}": {
        ('default', 'GET'): {
            'json': [link1, link2]
        },
        ('3links', 'GET'): {
            'json': [link1, link2, link3]
        },
        ('contract_delete', 'GET'): {
            'json': [link1, link2, link3_contract_delete]
        },
        ('link_delete', 'GET'): {
            'json': [link2]
        },
        ('nolinks', 'GET'): {
            'json': {
                "error-message":
                    "Provided Customer ID is not associated with any Link Id",
                "error-auxiliary-message": "Error",
                "error-code": 1080018
            },
            "status_code": 400
        }
    },
    f'/1.0.0/inventory/links/{MockLink2ID}': {
        ('default', 'GET'): {
            'json': link2
        }
    },
    f'/1.0.0/inventory/links/{MockLink3ID}': {
        ('default', 'GET'): {
            'json': link3
        }
    },
    f"/1.0.0/inventory/links/{MockLink1ID}": {
        ('default', 'GET'): {
            'json': link1
        }
    },
    f'/1.0.0/inventory/links/{MockLink2ID}/contract/{MockLink2ID}.1': {
        ('default', 'GET'): {
            'json': {**link2_contract1, **link2_contract1_extra}
        }
    },
    '/1.0.0/inventory/link': {
        ('default', 'POST'): {
            'json': {
                **link3,
                'success-auxiliary': 'Success',
                'success-code': 20000,
                'success-message': 'Link Created Successfully'
            }
        }
    },
    f'/lis/1.0.0/link/{MockLink1ID}': {
        ('default', 'DELETE'): {
            'json': {
                'success-auxiliary': 'Success',
                'success-code': 20000,
                'success-message': 'Link Deleted Successfully'
            }
        }
    },
    f'/1.0.0/inventory/links-stats/flow/{MockLink2ID}/'
    '2021-01-01-12:30:00/2021-01-01-12:40:00': {
        ('default', 'GET'): {
            'json': [
                {
                    'aggregateTags': [],
                    'tags': {
                        'flowid': MockLink2ID,
                        'direction': 'forward'
                    },
                    'dps': {
                        '1609504200': 0.1,
                        '1609504500': 0.2,
                        '1609504800': 0.3
                    },
                    'metric': 'flow.packets'
                },
                {
                    'aggregateTags': [],
                    'tags': {
                        'flowid': MockLink2ID,
                        'direction': 'reverse'
                    },
                    'dps': {
                        '1609504200': 0.4,
                        '1609504500': 0.5,
                        '1609504800': 0.6
                    },
                    'metric': 'flow.packets'
                },
                {
                    'aggregateTags': [],
                    'tags': {
                        'flowid': MockLink2ID,
                        'direction': 'forward'
                    },
                    'dps': {
                        '1609504200': 0.7,
                        '1609504500': 0.8,
                        '1609504800': 0.9
                    },
                    'metric': 'flow.bytes'
                },
                {
                    'aggregateTags': [],
                    'tags': {
                        'flowid': MockLink2ID,
                        'direction': 'reverse'
                    },
                    'dps': {
                        '1609504200': 1.0,
                        '1609504500': 1.1,
                        '1609504800': 1.2
                    },
                    'metric': 'flow.bytes'
                }
            ]
        }
    }
}
