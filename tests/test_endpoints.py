from requests_mock.contrib import fixture
import testtools

import telstra_pn
import telstra_pn.exceptions
import tests.mocks

username = tests.mocks.MockAuthUsername
password = tests.mocks.MockAuthPassword
accountid = tests.mocks.MockAuthAccountid


class TestDatacentres(testtools.TestCase):
    def setUp(self):
        super(TestDatacentres, self).setUp()
        telstra_pn.__flags__['debug'] = True

        self.api_mock = self.useFixture(fixture.Fixture())

        tests.mocks.setup_mocks(
            self.api_mock,
            [('generatetoken', 'POST'), ('validatetoken',)]
        )

        self.tpns = telstra_pn.Session(
            accountid=accountid, username=username, password=password)

    def test_datacentres(self):
        tests.mocks.setup_mocks(
            self.api_mock, [('datacenters',)]
        )

        dcs = self.tpns.datacentres
        self.assertTrue(dcs)
        self.assertTrue(len(dcs), 2)
        self.assertTrue('AMLS' in dcs)
        self.assertTrue('AMEQ' in dcs)
        self.assertTrue(tests.mocks.MockDatacentresDC1UUID in dcs)
        self.assertTrue(tests.mocks.MockDatacentresDC2UUID in dcs)
        self.assertEqual(dcs['AMLS'].cityname, 'Melbourne')
        self.assertEqual(self.api_mock.call_count, 2)
        for dc in dcs:
            self.assertEqual(dc.countryname, 'Australia')

        dcs.refresh()
        self.assertEqual(self.api_mock.call_count, 3)
