# Telstra Programmable Network Python SDK
Telstra Programmable Network is a self-provisioning platform that allows its users to create on-demand connectivity services between multiple end-points and add various network functions to those services. Programmable Network enables to connectivity to a global ecosystem of networking services as well as public and private cloud services. Once you are connected to the platform on one or more POPs (points of presence), you can start creating those services based on the use case that you want to accomplish. The Programmable Network API is available to all customers who have registered to use the Programmable Network. To register, please contact your account representative.


- API version: 2.5.3
- Package version: 0.1

For more information, please visit [https://dev.telstra.com/content/programmable-network-api](https://dev.telstra.com/content/programmable-network-api)

## Requirements.

Python 3.7+

## Installation & Usage
### pip install


```sh
pip install git+https://github.com/telstra/tpn-sdk-python.git
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/telstra/tpn-sdk-python.git`)

```python
import telstra_pn 
```

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python
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
```

## Author

pnapi-support@team.telstra.com
