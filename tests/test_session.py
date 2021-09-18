import unittest
from unittest.mock import patch
from requests_mock.contrib import fixture
import testtools

import telstra_pn
from telstra_pn.exceptions import TPNInvalidLogin
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


class TestSessionGenerateToken(testtools.TestCase):
    def test_login_incorrect(self):
        telstra_pn.__flags__['debug'] = True

        self.api_mock = self.useFixture(fixture.Fixture())
        tests.mocks.setup_mocks(
            self.api_mock,
            [('generatetoken', 'POST', 'login_incorrect')]
        )

        with self.assertRaisesRegex(TPNInvalidLogin, ''):
            telstra_pn.Session(accountid=accountid,
                               username=username,
                               password=password)

        # with self.assertRaises(TPNDataError):
        #     tpns = telstra_pn.Session(
        #         accountid=accountid, username=username, password=password)


class TestSession(testtools.TestCase):
    def setUp(self):
        super(TestSession, self).setUp()
        telstra_pn.__flags__['debug'] = True
        telstra_pn.__flags__['debug_getattr'] = True

        self.api_mock = self.useFixture(fixture.Fixture())

        tests.mocks.setup_mocks(
            self.api_mock,
            [('generatetoken', 'POST'), ('validatetoken',)]
        )

        self.tpns = telstra_pn.Session(accountid=accountid,
                                       username=username,
                                       password=password,
                                       otp=123456)

    def test_login(self):
        self.assertIsNotNone(self.tpns)
        self.assertEqual(self.tpns.sessionkey, tests.mocks.MockAuthSessionKey)
        # calls: generatetoken
        self.assertEqual(self.api_mock.call_count, 1)
        self.assertEqual(self.tpns.data['token_type'], 'bearer')
        self.assertTrue(self.tpns.data['expires_in'])
        self.assertTrue(self.tpns.data['refresh_token'])
        # calls: +validatetoken
        self.assertTrue(self.tpns.useruuid, tests.mocks.MockAuthUserUUID)
        self.assertEqual(self.api_mock.call_count, 2)

    def test_validate(self):
        tests.mocks.setup_mocks(
            self.api_mock,
            [('validatetoken',)]
        )

        self.tpns.validate()
        print(self.tpns.data)
        self.assertTrue(self.tpns.useruuid, f'{accountid}/{username}')
        self.assertTrue(self.tpns.customeruuid,
                        tests.mocks.MockAuthCustomerUUID)
        self.assertTrue(self.tpns.useruuid, tests.mocks.MockAuthUserUUID)
        self.assertEqual(self.api_mock.call_count, 2)

    @patch('telstra_pn.Datacentres')
    def test_datacentres(self, mock):
        self.tpns.datacentres
        self.assertEqual(mock.call_count, 1)

    @patch('telstra_pn.P2PLinks')
    def test_p2plinks(self, mock):
        self.tpns.p2plinks
        self.assertEqual(mock.call_count, 1)

    @patch('telstra_pn.Endpoints')
    def test_endpoints(self, mock):
        self.tpns.endpoints
        self.assertEqual(mock.call_count, 1)

    @patch('telstra_pn.Topologies')
    def test_topologies(self, mock):
        self.tpns.topologies
        self.assertEqual(mock.call_count, 1)
