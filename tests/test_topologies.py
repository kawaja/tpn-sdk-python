from requests_mock.contrib import fixture
import testtools

import telstra_pn
import telstra_pn.exceptions
import tests.mocks
from tests.mocks import setup_mocks, mock_history
from telstra_pn.codes import topologystatus

username = tests.mocks.MockAuthUsername
password = tests.mocks.MockAuthPassword
accountid = tests.mocks.MockAuthAccountid


class TestTopologies(testtools.TestCase):
    def setUp(self):
        super(TestTopologies, self).setUp()
        telstra_pn.__flags__['debug'] = True
        telstra_pn.__flags__['debug_getattr'] = True

        self.api_mock = self.useFixture(fixture.Fixture())

        setup_mocks(
            self.api_mock,
            [('generatetoken', 'POST'), ('validatetoken',)]
        )

        self.tpns = telstra_pn.Session(
            accountid=accountid, username=username, password=password)

    def test_topologies(self):
        setup_mocks(
            self.api_mock,
            [('topology_tag$',)]
        )

        topos = self.tpns.topologies
        self.assertIsNotNone(topos)
        self.assertEqual(len(topos), 2)
        self.assertEqual(str(topos), '2 TPN topologies')
        self.assertTrue('Test Topo #1' in topos)
        self.assertTrue('Test Topo #2' in topos)
        self.assertTrue(tests.mocks.MockTopo1UUID in topos)
        self.assertTrue(tests.mocks.MockTopo2UUID in topos)
        self.assertFalse('5aaf9a16-1ecb-4ea9-96d1-adbaefa14e7e' in topos)
        self.assertEqual(topos['Test Topo #1'].description,
                         'Test Topo Description #1')
        self.assertFalse(topos['Test Topo #2'].description == 'Sydney')
        self.assertEqual(self.api_mock.call_count, 2,
                         mock_history(self.api_mock))
        for topo in topos:
            self.assertEqual(topo.status, topologystatus.active)

        topos.refresh()
        self.assertEqual(self.api_mock.call_count, 3,
                         mock_history(self.api_mock))
