import enum
from requests_mock.contrib import fixture
from unittest.mock import MagicMock
import testtools
import unittest

import telstra_pn
from telstra_pn.models import endpoints
import telstra_pn.exceptions
import telstra_pn.models.endpoints
import tests.mocks
import tests.mocks_endpoints
from tests.mocks import setup_mocks, mock_history

username = tests.mocks.MockAuthUsername
password = tests.mocks.MockAuthPassword
accountid = tests.mocks.MockAuthAccountid


class TestEndpointTypes(testtools.TestCase):
    def setUp(self):
        super(TestEndpointTypes, self).setUp()
        telstra_pn.__flags__['debug'] = True
        telstra_pn.__flags__['debug_mocks'] = False
        telstra_pn.__flags__['debug_getattr'] = False
        self.api_mock = self.useFixture(fixture.Fixture())

        setup_mocks(self.api_mock, [
            ('generatetoken', 'POST'),
            ('validatetoken', ),
            ('switchporttype', ),
            ('endpoints', 'GET', 'none')
        ])

        self.tpns = telstra_pn.Session(
            accountid=accountid, username=username, password=password)

    def test_endpoint_types(self):
        et = self.tpns.endpoints.types
        self.assertGreater(len(et), 5)
        self.assertEqual(
            et.Port.value, '32eea883-16cf-11e8-902e-000c293805b1')
        self.assertEqual(
            et('32eea883-16cf-11e8-902e-000c293805b1').name, 'Port')
        self.assertEqual(
            et('32eea883-16cf-11e8-902e-000c293805b1'), et.Port)
        self.assertIsInstance(et, enum.EnumMeta)


class TestEndpointSubtypes(unittest.TestCase):
    def setUp(self):
        super(TestEndpointSubtypes, self).setUp()
        telstra_pn.__flags__['debug'] = True
        telstra_pn.__flags__['debug_mocks'] = False
        telstra_pn.__flags__['debug_getattr'] = False

    def test_endpoint_switchport(self):
        class EndpointTypes(enum.Enum):
            Port = '32eea883-16cf-11e8-902e-000c293805b1'
            NotPort = '48ad9af9-decb-40a2-8c69-db5b36f321bd'

        session = MagicMock(types=EndpointTypes)
        session.api_session.call_api.return_value = (
            tests.mocks_endpoints.endpoint1_switchport)
        ep = endpoints.Endpoint(session, **tests.mocks.endpoint1_switchport)
        self.assertTrue(isinstance(ep, endpoints.SwitchPort), type(ep))


class TestEndpoints(testtools.TestCase):
    def setUp(self):
        super(TestEndpoints, self).setUp()
        telstra_pn.__flags__['debug'] = True
        telstra_pn.__flags__['debug_mocks'] = True
        telstra_pn.__flags__['debug_getattr'] = False

        self.api_mock = self.useFixture(fixture.Fixture())

        setup_mocks(
            self.api_mock,
            [('generatetoken', 'POST'), ('validatetoken',)]
        )

        self.tpns = telstra_pn.Session(
            accountid=accountid, username=username, password=password)

    def test_endpoints(self):
        print(f'mock_responses: {tests.mocks.mock_responses}')
        setup_mocks(self.api_mock, [('endpoints', ),
                                    ('endpoint/endpointuuid', ),
                                    ('switchporttype', ),
                                    ('datacenters', )])

        eps = self.tpns.endpoints
        self.assertTrue(eps)
        self.assertEqual(len(eps.all), 2)
        self.assertEqual(len(eps), 2)
        self.assertTrue(tests.mocks.MockEndpoint1UUID in eps)
        self.assertTrue('ep1' in eps)
        self.assertTrue(tests.mocks.MockEndpoint2UUID in eps)
        self.assertEqual(eps['ep1'].datacentercode, 'AMLS')
        # calls: generatetoken, validatetoken, switchporttype,
        # endpointlist, datacentres, 2 x endpoints
        self.assertEqual(self.api_mock.call_count, 7,
                         mock_history(self.api_mock))

        eps.refresh()
        # calls: + endpointlist, 2 x endpoints
        self.assertEqual(self.api_mock.call_count, 10,
                         mock_history(self.api_mock))
