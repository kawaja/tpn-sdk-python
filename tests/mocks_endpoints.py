import copy
from tests.mocks_datacentres import MockDatacentresDC1UUID
from tests.mocks_auth import MockAuthCustomerUUID
from tests.mocks_topologies import MockTopo1UUID


MockEndpoint1UUID = '8bcca2cf-e166-4638-992d-d6e901c6e93a'
MockEndpoint2UUID = 'ac8348d4-9e48-464e-ac6c-e7a76007e7b3'
MockEndpoint3UUID = 'c54b030a-d733-4f8c-829a-a6f6b881a22e'

endpoint1_switchport = {
    'creationdate': 1500941038,
    'customeruuid': MockAuthCustomerUUID,
    'datacentercode': 'AMLS',
    'enabled': True,
    'endpointTypeuuid': '32eea883-16cf-11e8-902e-000c293805b1',
    'inventoryLocationuuid': '2c02f224-ccbf-11e5-b670-000c293805b1',
    'lastmodifieddate': 1624067308,
    'name': 'ep1',
    'endpointuuid': MockEndpoint1UUID,
    'portno': ['97'],
    'status': 'deployed',
    'switchcode': 'SW000000223D6C0128',
    'switchname': 'ofsw3.pen.amls',
    'switchuuid': '14f93516-3b72-4179-8df0-051ff6b21c46',
    'topologytaguuid': [MockTopo1UUID]
}

endpoint1_switchport_missing_portno = copy.deepcopy(endpoint1_switchport)
del endpoint1_switchport_missing_portno['portno']
endpoint1_switchport_no_ports = copy.deepcopy(endpoint1_switchport)
endpoint1_switchport_no_ports['portno'] = []
endpoint1_switchport_two_ports = copy.deepcopy(endpoint1_switchport)
endpoint1_switchport_two_ports['portno'] = ['96', '95']

endpoint2_switchport = {
    'creationdate': 1500941038,
    'customeruuid': MockAuthCustomerUUID,
    'datacentercode': 'AMLS',
    'enabled': True,
    'endpointTypeuuid': '32eea883-16cf-11e8-902e-000c293805b1',
    'inventoryLocationuuid': '2c02f224-ccbf-11e5-b670-000c293805b1',
    'lastmodifieddate': 1624067308,
    'name': 'ep2',
    'endpointuuid': MockEndpoint2UUID,
    'portno': ['98'],
    'status': 'deployed',
    'switchcode': 'SW000000223D6C0128',
    'switchname': 'ofsw3.pen.amls',
    'switchuuid': '14f93516-3b72-4179-8df0-051ff6b21c46',
    'topologytaguuid': [MockTopo1UUID]
}

endpoint3_switchport = {
    'creationdate': 1500941038,
    'customeruuid': MockAuthCustomerUUID,
    'datacentercode': 'AMLS',
    'enabled': True,
    'endpointTypeuuid': '32eea883-16cf-11e8-902e-000c293805b1',
    'inventoryLocationuuid': '2c02f224-ccbf-11e5-b670-000c293805b1',
    'lastmodifieddate': 1624067308,
    'name': '',
    'endpointuuid': MockEndpoint3UUID,
    'portno': ['99'],
    'status': 'deployed',
    'switchcode': 'SW000000223D6C0128',
    'switchname': 'ofsw3.pen.amls',
    'switchuuid': '14f93516-3b72-4179-8df0-051ff6b21c46',
    'topologytaguuid': [MockTopo1UUID]
}

endpointtypes = [{
    "switchporttypeid": 1,
    "switchporttypename": "Port",
    "switchporttypeuuid": "32eea883-16cf-11e8-902e-000c293805b1"
}, {
    "switchporttypeid": 2,
    "switchporttypename": "VNF",
    "switchporttypeuuid": "4c240647-16cf-11e8-902e-000c293805b1"
}, {
    "switchporttypeid": 3,
    "switchporttypename": "DIA",
    "switchporttypeuuid": "a03d653c-dc6f-11e5-996f-000c293805b1"
}, {
    "switchporttypeid": 4,
    "switchporttypename": "ISL",
    "switchporttypeuuid": "8af81dac-75ef-11e6-a638-02304ce2af1b"
}, {
    "switchporttypeid": 5,
    "switchporttypename": "Exchange",
    "switchporttypeuuid": "8af8351c-75ef-11e6-a638-02304ce2af1b"
}, {
    "switchporttypeid": 7,
    "switchporttypename": "IPVPN",
    "switchporttypeuuid": "d630970e-f33c-11e6-be1f-000c293805b1"
}, {
    "switchporttypeid": 8,
    "switchporttypename": "uCPE",
    "switchporttypeuuid": "3b5f3181-7e70-11e7-993a-0aa9532305d7"
}, {
    "switchporttypeid": 9,
    "switchporttypename": "NFV",
    "switchporttypeuuid": "d469be4e-7e70-11e7-993a-0aa9532305d7"
}, {
    "switchporttypeid": 10,
    "switchporttypename": "LBL",
    "switchporttypeuuid": "e7b4f019-7e70-11e7-993a-0aa9532305d7"
}, {
    "switchporttypeid": 11,
    "switchporttypename": "CP",
    "switchporttypeuuid": "3386e885-ebc4-11e7-b8f4-000c293805b1"
}, {
    "switchporttypeid": 12,
    "switchporttypename": "CE",
    "switchporttypeuuid": "a312feb4-6314-11e8-ad33-000c293805b1"
}]

mock_endpoints_responses = {
    f'/1.0.0/inventory/endpoints/customeruuid/{MockAuthCustomerUUID}': {
        ('default', 'GET'): {
            'json': {
                'endpointlist': [{
                    'datacenteruuid': MockDatacentresDC1UUID,
                    'endpointuuid': MockEndpoint1UUID
                }, {
                    'datacenteruuid': MockDatacentresDC1UUID,
                    'endpointuuid': MockEndpoint2UUID
                }, {
                    'datacenteruuid': MockDatacentresDC1UUID,
                    'endpointuuid': MockEndpoint3UUID
                }]
            }
        },
        ('none', 'GET'): {
            'json': {
                'endpointlist': []
            }
        }
    },
    f'/eis/1.0.0/endpoint/endpointuuid/{MockEndpoint1UUID}': {
        ('default', 'GET'): {'json': endpoint1_switchport},
        ('noportno', 'GET'): {'json': endpoint1_switchport_missing_portno},
        ('noports', 'GET'): {'json': endpoint1_switchport_no_ports},
        ('twoports', 'GET'): {'json': endpoint1_switchport_two_ports}
    },
    f'/eis/1.0.0/endpoint/endpointuuid/{MockEndpoint2UUID}': {
        ('default', 'GET'): {'json': endpoint2_switchport},
        ('noportno', 'GET'): {'json': endpoint2_switchport},
        ('noports', 'GET'): {'json': endpoint2_switchport},
        ('twoports', 'GET'): {'json': endpoint2_switchport}
    },
    f'/eis/1.0.0/endpoint/endpointuuid/{MockEndpoint3UUID}': {
        ('default', 'GET'): {'json': endpoint3_switchport},
        ('noportno', 'GET'): {'json': endpoint3_switchport},
        ('noports', 'GET'): {'json': endpoint3_switchport},
        ('twoports', 'GET'): {'json': endpoint3_switchport}
    },
    '/eis/1.0.0/switchporttype': {
        ('default', 'GET'): {'json': endpointtypes}
    }
}
