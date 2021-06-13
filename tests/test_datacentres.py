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
            ['generatetoken'])

        self.tpns = telstra_pn.Session(
            accountid=accountid, username=username, password=password)

    def test_datacentres(self):
        tests.mocks.setup_mocks(
            self.api_mock,
            ['datacenters'])

        dcs = self.tpns.Datacentres()
        self.assertTrue(dcs)
        self.assertTrue(len(dcs.data['datacenters']), 2)
        self.assertEqual(self.api_mock.call_count, 2)

        dcs.refresh()
        self.assertEqual(self.api_mock.call_count, 3)
