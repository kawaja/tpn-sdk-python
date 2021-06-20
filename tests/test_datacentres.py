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
            self.api_mock,
            [('generatetoken', 'POST'), ('validatetoken',)]
        )

        self.tpns = telstra_pn.Session(
            accountid=accountid, username=username, password=password)

    def test_datacentres(self):
        setup_mocks(
            self.api_mock,
            [('datacenters',)]
        )

        dcs = self.tpns.datacentres
        self.assertIsNotNone(dcs)
        self.assertEqual(len(dcs), 2)
        self.assertEqual(dcs['AMLS'].datacentercode, 'AMLS')
        self.assertEqual(dcs['AMEQ'].datacentercode, 'AMEQ')
        self.assertTrue('AMLS' in dcs)
        self.assertTrue('AMEQ' in dcs)
        self.assertFalse('SYEQ' in dcs)
        self.assertTrue(tests.mocks.MockDatacentresDC1UUID in dcs)
        self.assertTrue(tests.mocks.MockDatacentresDC2UUID in dcs)
        self.assertFalse('676c24ef-0f62-4f11-b405-37a091d57251' in dcs)
        self.assertEqual(dcs['AMLS'].cityname, 'Melbourne')
        self.assertFalse(dcs['AMLS'].cityname == 'Sydney')
        self.assertEqual(self.api_mock.call_count, 2,
                         mock_history(self.api_mock))
        for dc in dcs:
            self.assertEqual(dc.countryname, 'Australia')

        dcs.refresh()
        self.assertEqual(self.api_mock.call_count, 3,
                         mock_history(self.api_mock))
