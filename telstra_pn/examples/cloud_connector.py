import telstra_pn
from telstra_pn import renewal, latency

tpns = telstra_pn.Session(accountid='34324',
                          username='a@b.com',
                          password='154jk43l')

alibaba = tpns.cloud.providers('Alibaba Cloud Express Connect')

e1 = tpns.clouds.create(
    cloud_provider=alibaba,
    region=alibaba.regions('cn-hongkong'),
    bandwidth_mbps=50,
    )

e2 = tpns.switchports.create(
    datacentre=tpns.datacentres['SYEQ'],
    interface_type='1000Base-TX'
    )

flow = tpns.p2plinks.create(
    endpoints=[e1, e2],
    latency=latency.low,
    durationHours=3600,
    bandwidthMbps=1000,
    renewalOption=renewal.auto_renew,
    topology=tpns.topologies('testtopo')
)

print(f'number of contracts: {len(flow.active_contracts)}')
print(f'total bandwidth: {flow.total_bandwidth}')
print(f'total price per hour: {flow.total_price}')
print(f'link status: {flow.status}')
