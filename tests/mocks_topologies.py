from mocks_auth import MockAuthCustomerUUID, MockAuthUserUUID

MockTopo1UUID = 'fea00e0e-7983-4f60-a973-85c1ca166616'
MockTopo2UUID = 'a692caf4-1298-4247-ba03-cc14aa674b11'

mock_topologies_responses = {
    '/ttms/1.0.0/topology_tag': {
        ('default', 'GET'): {
            'json': [
                {
                    'uuid': MockTopo1UUID,
                    'name': 'Test Topo #1',
                    'description': 'Test Topo Description #1',
                    'status': 'active',
                    'customer_uuid': MockAuthCustomerUUID,
                    'nsd_uuid': None,
                    'gui_topology_id': None,
                    'created_by': MockAuthUserUUID,
                    'creation_date': 1622522804000,
                    'deletion_date': None
                },
                {
                    'uuid': MockTopo2UUID,
                    'name': 'Test Topo #2',
                    'description': 'Test Topo Description #2',
                    'status': 'active',
                    'customer_uuid': MockAuthCustomerUUID,
                    'nsd_uuid': None,
                    'gui_topology_id': None,
                    'created_by': MockAuthUserUUID,
                    'creation_date': 1622522718000,
                    'deletion_date': None
                },
            ]
        }
    }
}
