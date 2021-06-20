import telstra_pn
from telstra_pn import latency, renewal

tpns = telstra_pn.Session(accountid='34324',  # nosec
                          username='a@b.com',
                          password='154jk43l')

# allocate a new port in the AMLS data centre and select VLAN 20
e1 = tpns.switchports.create(
    datacentre=tpns.datacentres['AMLS'],
    interface_type='1000Base-TX',
    name='backup_dc_a'
    ).vlan(20)

# use an existing port named "primary_dc_a" and select VLAN 30
e2 = tpns.switchports['primary_dc_a'].vlan(30)

# create a flow (with an initial bandwidth contract) between
# the two switch ports (vlan 20 on one end, vlan 30 on the other)
# and add to the 'testtopo' topology.
flow = tpns.p2plinks.create(
    endpoints=[e1, e2],
    latency=latency.low,
    duration_hours=1,
    bandwidth_mbps=1000,
    renewal_option=renewal.auto_renew,
    topology=tpns.topologies('testtopo')
)

print(f'number of contracts: {len(flow.active_contracts)}')
print(f'total bandwidth: {flow.total_bandwidth}')
print(f'total price per hour: {flow.total_price}')
print(f'link status: {flow.status}')
