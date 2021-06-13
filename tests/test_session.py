import unittest
import requests_mock

import telstra_pn
import telstra_pn.exceptions
import tests.mocks_auth

username = tests.mocks_auth.MockUsername
password = tests.mocks_auth.MockPassword
accountid = tests.mocks_auth.MockAccountid


class TestSession(unittest.TestCase):
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

    @requests_mock.Mocker()
    def test_login(self, api_mock):
        tests.mocks_auth.setup_mocks(
            api_mock,
            ['generatetoken'])

        tpns = telstra_pn.Session(
            accountid=accountid, username=username, password=password)
        self.assertTrue(tpns)
        self.assertEqual(tpns.sessionkey, tests.mocks_auth.MockSessionKey)
        self.assertEqual(tpns.token_type, 'bearer')
        self.assertTrue(tpns.expires_in)
        self.assertTrue(tpns.refresh_token)
        self.assertEqual(api_mock.call_count, 1)

    @requests_mock.Mocker()
    def test_validate(self, api_mock):
        tests.mocks_auth.setup_mocks(
            api_mock,
            ['generatetoken', 'validatetoken'])
        tpns = telstra_pn.Session(
            accountid=accountid, username=username, password=password)
        tpns.validate()
        print(tpns.data)
        self.assertTrue(tpns.useruuid, f'{accountid}/{username}')
        self.assertTrue(tpns.customeruuid,
                        tests.mocks_auth.MockCustomerUUID)
        self.assertTrue(tpns.useruuid, tests.mocks_auth.MockUserUUID)
        self.assertEqual(api_mock.call_count, 2)
