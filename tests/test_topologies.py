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
            self.api_mock, [
                ('generatetoken', 'POST'),
                ('validatetoken',),
                ('topology_tag$',)
            ]
        )

        self.tpns = telstra_pn.Session(
            accountid=accountid, username=username, password=password)

        self.topos = self.tpns.topologies

    def test_topologies(self):
        self.assertIsNotNone(self.topos)
        self.assertEqual(len(self.topos), 2)

    def test_topologies_contains(self):
        self.assertTrue('Test Topo #1' in self.topos)
        self.assertTrue('Test Topo #2' in self.topos)
        self.assertTrue(tests.mocks.MockTopo1UUID in self.topos)
        self.assertTrue(tests.mocks.MockTopo2UUID in self.topos)

    def test_topologies_contains_missing(self):
        self.assertFalse('5aaf9a16-1ecb-4ea9-96d1-adbaefa14e7e' in self.topos)

    def test_topologies_get_description(self):
        self.assertEqual(self.topos['Test Topo #1'].description,
                         'Test Topo Description #1')
        self.assertFalse(self.topos['Test Topo #2'].description == 'Sydney')

    def test_topologies_iteration(self):
        for topo in self.topos:
            self.assertEqual(topo.status, topologystatus.active)

    def test_topologies_refresh(self):
        self.assertEqual(self.api_mock.call_count, 2,
                         mock_history(self.api_mock))
        self.topos.refresh()
        self.assertEqual(self.api_mock.call_count, 3,
                         mock_history(self.api_mock))

    def test_topologies_display(self):
        self.assertEqual(str(self.topos), '2 topologies')

    def test_topologies_single_display(self):
        self.assertEqual(str(self.topos['Test Topo #1']), 'Test Topo #1')
