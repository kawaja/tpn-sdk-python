import unittest
import requests_mock
from requests.exceptions import HTTPError, ConnectTimeout

import telstra_pn
import telstra_pn.rest
import telstra_pn.exceptions
import tests.mocks


class TestRest(unittest.TestCase):
    def setUp(self):
        telstra_pn.__flags__['debug'] = True
        self.mr = tests.mocks.mock_responses

    @requests_mock.Mocker()
    def test_get_success(self, get_mock):
        get_mock.get(
            '/',
            status_code=self.mr['nopath']['GET'].get('status_code', 200),
            json=self.mr['nopath']['GET']['response'])

        tpns = telstra_pn.rest.ApiSession()
        r = tpns.call_api(
            path='nopath',
            body=''
        )

        self.assertEqual(r, self.mr['nopath']['GET']['response'])

    @requests_mock.Mocker()
    def test_get_500(self, get_mock):
        get_mock.get(
            '/',
            status_code=self.mr['nopath']['GET'].get('status_code', 500),
            json=self.mr['nopath']['GET']['response'])

        tpns = telstra_pn.rest.ApiSession()
        with self.assertRaisesRegex(HTTPError, 'Server Error:.*'):
            tpns.call_api(
                path='nopath',
                body=''
            )

    @requests_mock.Mocker()
    def test_post_success(self, post_mock):
        post_mock.post(
            '/',
            status_code=self.mr['nopath']['POST'].get('status_code', 201),
            json=self.mr['nopath']['POST']['response'])

        tpns = telstra_pn.rest.ApiSession()
        r = tpns.call_api(
            method='POST',
            path='nopath',
            body=''
        )

        self.assertEqual(r, self.mr['nopath']['POST']['response'])

    @requests_mock.Mocker()
    def test_post_500(self, post_mock):
        post_mock.post(
            '/',
            status_code=self.mr['nopath']['POST'].get('status_code', 500),
            json=self.mr['nopath']['POST']['response'])

        tpns = telstra_pn.rest.ApiSession()
        with self.assertRaisesRegex(HTTPError, 'Server Error:.*'):
            tpns.call_api(
                method='POST',
                path='nopath',
                body=''
            )

    @requests_mock.Mocker()
    def test_post_timeout(self, post_mock):
        post_mock.post(
            '/',
            exc=ConnectTimeout
        )

        tpns = telstra_pn.rest.ApiSession()
        with self.assertRaises(telstra_pn.exceptions.TPNAPIUnavailable):
            tpns.call_api(
                method='POST',
                path='nopath',
                body=''
            )

    @requests_mock.Mocker()
    def test_get_timeout(self, get_mock):
        get_mock.get(
            '/',
            exc=ConnectTimeout
        )

        tpns = telstra_pn.rest.ApiSession()
        with self.assertRaises(telstra_pn.exceptions.TPNAPIUnavailable):
            tpns.call_api(
                method='GET',
                path='nopath',
                body=''
            )
