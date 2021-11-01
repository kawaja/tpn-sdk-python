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
import tests.mocks_auth
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
            VNF = '4c240647-16cf-11e8-902e-000c293805b1'
            NotPort = '48ad9af9-decb-40a2-8c69-db5b36f321bd'
            IPVPN = 'd630970e-f33c-11e6-be1f-000c293805b1'
            CP = '3386e885-ebc4-11e7-b8f4-000c293805b1'
            Exchange = '8af8351c-75ef-11e6-a638-02304ce2af1b'
            DIA = 'a03d653c-dc6f-11e5-996f-000c293805b1'

        session = MagicMock()
        session.api_session.call_api.return_value = (
            tests.mocks_endpoints.endpoint1_switchport)
        session.customeruuid = tests.mocks_auth.MockAuthCustomerUUID
        eps = MagicMock(types=EndpointTypes)
        eps.session = session
        ep = endpoints.Endpoint(eps, **tests.mocks.endpoint1_switchport)
        self.assertTrue(isinstance(ep, endpoints.SwitchPort), type(ep))


class TestEndpoints(testtools.TestCase):
    def setUp(self):
        super(TestEndpoints, self).setUp()
        telstra_pn.__flags__['debug'] = True
        telstra_pn.__flags__['debug_mocks'] = True
        telstra_pn.__flags__['debug_getattr'] = True

        self.api_mock = self.useFixture(fixture.Fixture())

        setup_mocks(
            self.api_mock,
            [('generatetoken', 'POST'), ('validatetoken',)]
        )

        self.tpns = telstra_pn.Session(
            accountid=accountid, username=username, password=password)

    def test_endpoints_missing_port(self):
        setup_mocks(self.api_mock,
                    [('endpoints', ),
                     ('endpoint/endpointuuid', 'GET', 'noportno'),
                     ('switchporttype', ), ('datacenters', ),
                     ('switchtypename', )])

        print(f'mock status: {self.api_mock.real_http}')

        with self.assertRaisesRegex(
                telstra_pn.exceptions.TPNRefreshInconsistency,
                'detail does not contain "portno" field'):
            self.eps = self.tpns.endpoints

    def test_endpoints_zero_ports(self):
        setup_mocks(self.api_mock,
                    [('endpoints', ),
                     ('endpoint/endpointuuid', 'GET', 'noports'),
                     ('switchporttype', ), ('datacenters', )])

        with self.assertRaisesRegex(
                telstra_pn.exceptions.TPNRefreshInconsistency,
                'detail contains 0 ports'):
            self.eps = self.tpns.endpoints

    def test_endpoints_two_ports(self):
        setup_mocks(self.api_mock,
                    [('endpoints', ),
                     ('endpoint/endpointuuid', 'GET', 'twoports'),
                     ('switchporttype', ), ('datacenters', )])

        with self.assertRaisesRegex(
                telstra_pn.exceptions.TPNRefreshInconsistency,
                'detail contains 2 ports'):
            self.eps = self.tpns.endpoints


class TestEndpointsBehaviour(testtools.TestCase):
    def setUp(self):
        super(TestEndpointsBehaviour, self).setUp()
        telstra_pn.__flags__['debug'] = True
        telstra_pn.__flags__['debug_mocks'] = False
        telstra_pn.__flags__['debug_getattr'] = False

        self.api_mock = self.useFixture(fixture.Fixture())

        setup_mocks(
            self.api_mock,
            [('generatetoken', 'POST'), ('validatetoken',)]
        )

        self.tpns = telstra_pn.Session(
            accountid=accountid, username=username, password=password)

        setup_mocks(self.api_mock, [('endpoints', ),
                                    ('endpoint/endpointuuid', ),
                                    ('switchporttype', ),
                                    ('datacenters', )])

        self.eps = self.tpns.endpoints

    def test_endpoints(self):
        self.assertTrue(self.eps)
        self.assertEqual(len(self.eps), 3)

    def test_endpoints_contains(self):
        self.assertTrue(tests.mocks.MockEndpoint1UUID in self.eps)
        self.assertTrue('ep1' in self.eps)
        self.assertTrue(tests.mocks.MockEndpoint2UUID in self.eps)

    def test_endpoints_contains_missing(self):
        self.assertFalse('ep5' in self.eps)

    def test_endpoints_get_datcentercode(self):
        self.assertEqual(self.eps['ep1'].datacentercode, 'AMLS')

    def test_endpoints_refresh(self):
        # calls: generatetoken, validatetoken, switchporttype,
        # endpointlist, datacentres, 3 x endpoints, switchtypename
        self.assertEqual(self.api_mock.call_count, 9,
                         mock_history(self.api_mock))
        self.eps.refresh()
        # calls: + endpointlist, 3 x endpoints
        self.assertEqual(self.api_mock.call_count, 13,
                         mock_history(self.api_mock))

    def test_endpoints_display(self):
        self.assertEqual(str(self.eps), '3 endpoints')

    def test_endpoints_single_display_name(self):
        self.assertEqual(str(self.eps['ep1']), 'AMLS / ep1')

    def test_endpoints_single_display_noname(self):
        self.assertEqual(
            str(self.eps[tests.mocks_endpoints.MockEndpoint3UUID]),
            'AMLS / ofsw3.pen.amls.99')

    def test_endpoints_list(self):
        output = ''
        for ep in self.eps:
            output = f'{output}\n{ep.__class__.__name__}'

        print(output)
        self.assertEqual(output, '\nSwitchPort\nSwitchPort\nSwitchPort')
