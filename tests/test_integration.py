from time import sleep
import pyotp
import unittest
import pytest
import telstra_pn
from telstra_pn import latency, renewal, status
try:
    from tests.integration_test_credentials import (
        ITAccountID, ITUserName, ITPassword, ITOTPSecret)
except ModuleNotFoundError:
    print('please create tests/integration_test_credentials.py to run integration testing')

# from telstra_pn.codes import latency, renewal


class TestIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        otp = None
        if ITOTPSecret is not None:
            otp = pyotp.TOTP(ITOTPSecret).now()
        cls.tpns = telstra_pn.Session(
            accountid=ITAccountID,
            username=ITUserName,
            password=ITPassword,
            otp=otp)

    def test_validate(self):
        TestIntegration.tpns.validate()
        print(f'useruuid: {TestIntegration.tpns.useruuid}')
        print(f'username: {TestIntegration.tpns.username}')
        self.assertEqual(TestIntegration.tpns.username,
                         f'{ITAccountID}/{ITUserName}')

    def test_datacentres(self):
        dcs = TestIntegration.tpns.datacentres
        self.assertGreater(len(dcs), 5)
        for dc in dcs:
            print(f'name: {dc.datacentername}')

    def test_p2plinks(self):
        links = TestIntegration.tpns.p2plinks
        self.assertGreater(len(links), 5)
        for link in links:
            print(f'{link.id} -> {link.description}')

    def test_topologies(self):
        topos = TestIntegration.tpns.topologies
        self.assertGreater(len(topos), 5)
        for topo in topos:
            print(f'topology name: {topo.topologyname}')

    @pytest.mark.xfail(reason='Link creation not yet implemented')
    def test_create_link(self):
        e1 = TestIntegration.tpns.endpoints[
            '6ae5c55f-1ca5-4aae-b788-b1a774a97157'].vlan(39)
        e2 = TestIntegration.tpns.endpoints[
            '6ae5c55f-1ca5-4aae-b788-b1a774a97157'].vlan(49)

        link = TestIntegration.tpns.p2plinks.create(
           endpoints=[e1, e2],
           latency=latency.low,
           duration_hours=1,
           bandwidth_mbps=1000,
           renewal_option=renewal.auto_renew,
           topology=TestIntegration.tpns.topologies['rik-ipvpn']
        )

        self.assertEqual(link.status, status.deploying, link.status)

        while link.status == status.deploying:
            print(f'status: {status}')
            sleep(5)

        self.assertEqual(link.status, status.deployed, link.status)

        sleep(5)

        link.delete()

        self.assertEqual(link.status, status.deleting, link.status)

        while link.status == status.deleting:
            print(f'status: {status}')
            sleep(5)

        self.assertEqual(link.status, status.deleted, link.status)
