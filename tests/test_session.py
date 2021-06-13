import unittest
from requests_mock.contrib import fixture
import testtools

import telstra_pn
import telstra_pn.exceptions
import tests.mocks

username = tests.mocks.MockAuthUsername
password = tests.mocks.MockAuthPassword
accountid = tests.mocks.MockAuthAccountid


class TestSessionLoginFailures(unittest.TestCase):
    def setUp(self):
        telstra_pn.__flags__['debug'] = True

    def test_login_missing_accountid(self):
        with self.assertRaises(ValueError):
            telstra_pn.Session(username=username, password=password)

    def test_login_missing_username(self):
        with self.assertRaises(ValueError):
            telstra_pn.Session(accountid=accountid, password=password)

    def test_login_missing_password(self):
        with self.assertRaises(ValueError):
            telstra_pn.Session(username=username, accountid=accountid)


class TestSession(testtools.TestCase):
    def setUp(self):
        super(TestSession, self).setUp()
        telstra_pn.__flags__['debug'] = True

        self.api_mock = self.useFixture(fixture.Fixture())

        tests.mocks.setup_mocks(
            self.api_mock,
            ['generatetoken'])

        self.tpns = telstra_pn.Session(
            accountid=accountid, username=username, password=password)

    def test_login(self):
        self.assertTrue(self.tpns)
        self.assertEqual(self.tpns.sessionkey, tests.mocks.MockAuthSessionKey)
        self.assertEqual(self.tpns.token_type, 'bearer')
        self.assertTrue(self.tpns.expires_in)
        self.assertTrue(self.tpns.refresh_token)
        self.assertEqual(self.api_mock.call_count, 1)

    def test_validate(self):
        tests.mocks.setup_mocks(
            self.api_mock,
            ['validatetoken'])

        self.tpns.validate()
        print(self.tpns.data)
        self.assertTrue(self.tpns.useruuid, f'{accountid}/{username}')
        self.assertTrue(self.tpns.customeruuid,
                        tests.mocks.MockAuthCustomerUUID)
        self.assertTrue(self.tpns.useruuid, tests.mocks.MockAuthUserUUID)
        self.assertEqual(self.api_mock.call_count, 2)
