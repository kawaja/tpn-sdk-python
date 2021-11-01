from requests_mock.contrib import fixture
import testtools

import telstra_pn
import telstra_pn.exceptions
import tests.mocks
from tests.mocks import setup_mocks, mock_history

username = tests.mocks.MockAuthUsername
password = tests.mocks.MockAuthPassword
accountid = tests.mocks.MockAuthAccountid


class TestDatacentres(testtools.TestCase):
    def setUp(self):
        super(TestDatacentres, self).setUp()
        telstra_pn.__flags__['debug'] = True

        self.api_mock = self.useFixture(fixture.Fixture())

        setup_mocks(
            self.api_mock, [
                ('generatetoken', 'POST'),
                ('validatetoken',),
                ('datacenters',)
            ]
        )

        self.tpns = telstra_pn.Session(
            accountid=accountid, username=username, password=password)

        self.dcs = self.tpns.datacentres

    def test_datacentres(self):
        self.assertIsNotNone(self.dcs)
        self.assertEqual(len(self.dcs), 2)

    def test_datacentres_get(self):
        self.assertEqual(self.dcs['AMLS'].datacentercode, 'AMLS')
        self.assertEqual(self.dcs['AMEQ'].datacentercode, 'AMEQ')

    def test_datacentres_contains(self):
        self.assertTrue('AMLS' in self.dcs)
        self.assertTrue('AMEQ' in self.dcs)
        self.assertTrue(tests.mocks.MockDatacentresDC1UUID in self.dcs)
        self.assertTrue(tests.mocks.MockDatacentresDC2UUID in self.dcs)

    def test_datacentres_contains_missing(self):
        self.assertFalse('SYEQ' in self.dcs)
        self.assertFalse('676c24ef-0f62-4f11-b405-37a091d57251' in self.dcs)

    def test_datacentres_get_cityname(self):
        self.assertEqual(self.dcs['AMLS'].cityname, 'Melbourne')
        self.assertFalse(self.dcs['AMLS'].cityname == 'Sydney')

    def test_datacentres_iteration(self):
        for dc in self.dcs:
            self.assertEqual(dc.countryname, 'Australia')

    def test_datacentres_refresh(self):
        # calls: generatetoken, inventory/datacenters, switchtypename/vnf
        self.assertEqual(self.api_mock.call_count, 3,
                         mock_history(self.api_mock))
        self.dcs.refresh()
        # calls: + inventory/datacenters
        self.assertEqual(self.api_mock.call_count, 4,
                         mock_history(self.api_mock))

    def test_datacentres_display(self):
        self.assertEqual(str(self.dcs), '2 datacentres')

    def test_datacentres_single_display(self):
        self.assertEqual(str(self.dcs['AMLS']), 'AMLS')
