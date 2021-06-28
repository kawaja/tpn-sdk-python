import testtools
from requests_mock.contrib import fixture

import telstra_pn
import telstra_pn.rest
from telstra_pn.exceptions import TPNDataError, TPNAPIUnavailable
import tests.mocks


class TestRest(testtools.TestCase):
    def setUp(self):
        super(TestRest, self).setUp()
        telstra_pn.__flags__['debug_api'] = True
        self.mr = tests.mocks.mock_responses

        self.api_mock = self.useFixture(fixture.Fixture())

    def test_get_success(self):
        tests.mocks.setup_mocks(
            self.api_mock,
            [('testpath',)]
        )

        tpns = telstra_pn.rest.ApiSession()
        r = tpns.call_api(
            path='/testpath',
            body=''
        )

        self.assertEqual(r, self.mr['/testpath'][('default', 'GET')]['json'])

    def test_get_500(self):
        tests.mocks.setup_mocks(
            self.api_mock,
            [('testpath', 'GET', '500')]
        )

        tpns = telstra_pn.rest.ApiSession()
        with self.assertRaisesRegex(TPNDataError, 'Server Error:.*'):
            tpns.call_api(
                path='/testpath',
                body=''
            )

    def test_post_success(self):
        tests.mocks.setup_mocks(
            self.api_mock,
            [('/testpath', 'POST')]
        )

        tpns = telstra_pn.rest.ApiSession()
        r = tpns.call_api(
            method='POST',
            path='/testpath',
            body=''
        )

        self.assertEqual(r, self.mr['/testpath'][('default', 'POST')]['json'])

    def test_put_success(self):
        tests.mocks.setup_mocks(
            self.api_mock,
            [('/testpath', 'PUT')]
        )

        tpns = telstra_pn.rest.ApiSession()
        r = tpns.call_api(
            method='PUT',
            path='/testpath',
            body=''
        )

        self.assertEqual(r, self.mr['/testpath'][('default', 'PUT')]['json'])

    def test_put_500(self):
        tests.mocks.setup_mocks(
            self.api_mock,
            [('testpath', 'PUT', '500')]
        )

        tpns = telstra_pn.rest.ApiSession()
        with self.assertRaisesRegex(TPNDataError, 'Server Error:.*'):
            tpns.call_api(
                method='PUT',
                path='/testpath',
                body=''
            )

    def test_delete_success(self):
        tests.mocks.setup_mocks(
            self.api_mock,
            [('/testpath', 'DELETE')]
        )

        tpns = telstra_pn.rest.ApiSession()
        r = tpns.call_api(
            method='DELETE',
            path='/testpath',
            body=''
        )

        self.assertEqual(r,
                         self.mr['/testpath'][('default', 'DELETE')]['json'])

    def test_delete_500(self):
        tests.mocks.setup_mocks(
            self.api_mock,
            [('testpath', 'DELETE', '500')]
        )

        tpns = telstra_pn.rest.ApiSession()
        with self.assertRaisesRegex(TPNDataError, 'Server Error:.*'):
            tpns.call_api(
                method='DELETE',
                path='/testpath',
                body=''
            )

    def test_lowercase_method(self):
        tests.mocks.setup_mocks(
            self.api_mock,
            [('/testpath', 'POST')]
        )

        tpns = telstra_pn.rest.ApiSession()
        r = tpns.call_api(
            method='post',
            path='/testpath',
            body=''
        )

        self.assertEqual(r, self.mr['/testpath'][('default', 'POST')]['json'])

    def test_post_500(self):
        tests.mocks.setup_mocks(
            self.api_mock,
            [('testpath', 'POST', '500')]
        )

        tpns = telstra_pn.rest.ApiSession()
        with self.assertRaisesRegex(TPNDataError, 'Server Error:.*'):
            tpns.call_api(
                method='POST',
                path='/testpath',
                body=''
            )

    def test_post_timeout(self):
        tests.mocks.setup_mocks(
            self.api_mock,
            [('testpath', 'POST', 'timeout')]
        )

        tpns = telstra_pn.rest.ApiSession()
        with self.assertRaisesRegex(TPNAPIUnavailable, ''):
            tpns.call_api(
                method='POST',
                path='/testpath',
                body=''
            )

    def test_get_timeout(self):
        tests.mocks.setup_mocks(
            self.api_mock,
            [('testpath', 'GET', 'timeout')]
        )

        tpns = telstra_pn.rest.ApiSession()
        with self.assertRaisesRegex(TPNAPIUnavailable, ''):
            tpns.call_api(
                method='GET',
                path='/testpath',
                body=''
            )

    def test_put_timeout(self):
        tests.mocks.setup_mocks(
            self.api_mock,
            [('testpath', 'PUT', 'timeout')]
        )

        tpns = telstra_pn.rest.ApiSession()
        with self.assertRaisesRegex(TPNAPIUnavailable, ''):
            tpns.call_api(
                method='PUT',
                path='/testpath',
                body=''
            )

    def test_delete_timeout(self):
        tests.mocks.setup_mocks(
            self.api_mock,
            [('testpath', 'DELETE', 'timeout')]
        )

        tpns = telstra_pn.rest.ApiSession()
        with self.assertRaisesRegex(TPNAPIUnavailable, ''):
            tpns.call_api(
                method='DELETE',
                path='/testpath',
                body=''
            )

    def test_invalid_method(self):
        tests.mocks.setup_mocks(
            self.api_mock,
            [('testpath', 'PATCH',)]
        )

        tpns = telstra_pn.rest.ApiSession()
        with self.assertRaisesRegex(TPNAPIUnavailable,
                                    'method PATCH not implemented'):
            tpns.call_api(
                method='PATCH',
                path='/testpath',
                body=''
            )
