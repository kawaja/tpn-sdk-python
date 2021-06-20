from requests_mock.contrib import fixture
import testtools
import json

import telstra_pn
import telstra_pn.exceptions
import tests.mocks
from tests.mocks import setup_mocks, mock_history
from telstra_pn.codes import status, latency, renewal
import datetime
from datetime import timezone

username = tests.mocks.MockAuthUsername
password = tests.mocks.MockAuthPassword
accountid = tests.mocks.MockAuthAccountid


class TestP2PLinks(testtools.TestCase):
    def setUp(self):
        super(TestP2PLinks, self).setUp()
        telstra_pn.__flags__['debug'] = True
        telstra_pn.__flags__['debug_getattr'] = True

        self.api_mock = self.useFixture(fixture.Fixture())

        setup_mocks(
            self.api_mock,
            [('generatetoken', 'POST'), ('validatetoken',)]
        )

        self.tpns = telstra_pn.Session(
            accountid=accountid, username=username, password=password)

    def test_p2plinks(self):
        setup_mocks(
            self.api_mock, [('inventory/links/customer',)]
        )

        links = self.tpns.p2plinks
        self.assertIsNotNone(links)
        self.assertEqual(len(links), 2)
        self.assertTrue('Test link #1' in links)
        self.assertTrue('Test link #2' in links)
        self.assertFalse('Test link #3' in links)
        self.assertTrue(tests.mocks.MockLink1ID in links)
        self.assertTrue(tests.mocks.MockLink2ID in links)
        self.assertFalse('cb46ec44-4b5b-4fd9-80c9-dd52c1805ff0' in links)
        self.assertEqual(links['Test link #1'].tag, 'production')
        # calls: generatetoken, validatetoken, inventory/links/customer
        self.assertEqual(self.api_mock.call_count, 3,
                         mock_history(self.api_mock))
        for link in links:
            self.assertEqual(link.linkStatus, 1)

        links.refresh()
        # calls: +inventory/links/customer
        self.assertEqual(self.api_mock.call_count, 4,
                         mock_history(self.api_mock))

    def test_p2plinks_nolinks(self):
        setup_mocks(
            self.api_mock, [('inventory/links/customer', 'GET', 'nolinks')]
        )

        links = self.tpns.p2plinks
        self.assertIsNotNone(links)
        self.assertEqual(len(links), 0)
        # calls: generatetoken, validatetoken, inventory/links/customer
        self.assertEqual(self.api_mock.call_count, 3,
                         mock_history(self.api_mock))

    def test_p2plink_refresh(self):
        setup_mocks(
            self.api_mock, [
                ('inventory/links/customer',),
                (f'inventory/links/{tests.mocks.MockLink1ID}',)
            ]
        )

        links = self.tpns.p2plinks
        self.assertIsNotNone(links)
        self.assertEqual(len(links), 2)
        # calls: generatetoken, validatetoken, inventory/links/customer
        self.assertEqual(self.api_mock.call_count, 3,
                         mock_history(self.api_mock))

        links['Test link #1'].refresh()
        self.assertEqual(len(links), 2)
        self.assertEqual(self.api_mock.call_count, 4,
                         mock_history(self.api_mock))

    def test_contract_refresh(self):
        setup_mocks(
            self.api_mock, [
                ('inventory/links/customer',),
                ('inventory/links.*contract',)
            ]
        )

        links = self.tpns.p2plinks
        self.assertTrue(links)
        self.assertEqual(len(links), 2)
        # calls: generatetoken, validatetoken, inventory/links/customer
        self.assertEqual(self.api_mock.call_count, 3,
                         mock_history(self.api_mock))

        self.assertEqual(len(links['Test link #2'].contracts), 1)
        links['Test link #2'].contracts['1'].refresh()
        self.assertEqual(len(links), 2)
        self.assertEqual(len(links['Test link #2'].contracts), 1)
        self.assertEqual(self.api_mock.call_count, 4,
                         mock_history(self.api_mock))

    def test_contract_delete(self):
        setup_mocks(
            self.api_mock, [
                ('inventory/links/customer', 'GET', '3links'),
                ('inventory/links/customer', 'GET', 'contract_delete'),
                ('inventory/links.*contract',)
            ]
        )

        links = self.tpns.p2plinks
        self.assertTrue(links)
        self.assertEqual(len(links), 3)
        # calls: generatetoken, validatetoken, inventory/links/customer
        self.assertEqual(self.api_mock.call_count, 3,
                         mock_history(self.api_mock))

        self.assertEqual(len(links['Test link #3'].contracts), 1)
        links['Test link #3'].contracts['1'].delete()
        self.assertEqual(len(links['Test link #3'].contracts), 0)
        # calls: + inventory/links/customer - get_data in delete()
        self.assertEqual(self.api_mock.call_count, 4,
                         mock_history(self.api_mock))
        self.assertEqual(len(links), 3)

    def test_p2plinks_create(self):
        setup_mocks(
            self.api_mock, [
                ('inventory/links/customer', 'GET'),
                ('inventory/links/customer', 'GET', '3links'),
                ('inventory/link$',)
            ]
        )

        links = self.tpns.p2plinks
        self.assertEqual(len(links), 2)
        linkid = links.create(
            endpoints=[
                tests.mocks.MockEndpoint1UUID,
                tests.mocks.MockEndpoint2UUID
            ],
            latency=latency.low,
            duration_hours=1,
            bandwidth_mbps=1000,
            renewal_option=renewal.auto_renew,
            topology='abc'
        )
        self.assertEqual(links[linkid].status, status.new)
        self.assertEqual(linkid, tests.mocks.MockLink3ID)
        self.assertEqual(len(links), 3)
        links.refresh()
        self.assertEqual(len(links), 3)

    def test_p2plink_delete(self):
        setup_mocks(
            self.api_mock, [
                ('inventory/links/customer',),
                ('inventory/links/customer', 'GET', 'link_delete'),
                ('inventory/links/[a-f0-9]+$',),
                ('lis/.*link/[a-f0-9]+$', 'DELETE')
            ]
        )

        links = self.tpns.p2plinks
        # calls: generatetoken, validatetoken, inventory/links/customer
        self.assertEqual(self.api_mock.call_count, 3,
                         mock_history(self.api_mock))
        self.assertEqual(len(links), 2)
        links['Test link #1'].delete()
        # calls: + delete, inventory/links/customer
        self.assertEqual(self.api_mock.call_count, 5,
                         mock_history(self.api_mock))
        self.assertEqual(len(links), 1)

    def test_p2plink_get_statistics(self):
        setup_mocks(
            self.api_mock, [
                ('inventory/links/customer', ),
                ('inventory/links-stats/flow', )
            ]
        )

        links = self.tpns.p2plinks
        self.assertEqual(len(links), 2)
        stats = links['Test link #2'].get_statistics(
            from_date=datetime.datetime(2021, 1, 1, 12, 30, 0, 55,
                                        tzinfo=timezone.utc),
            to_date=datetime.datetime(2021, 1, 1, 12, 40, 0,
                                      tzinfo=timezone.utc)
            )

        self.assertEqual(len(stats), 4)
