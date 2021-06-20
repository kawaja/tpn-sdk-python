from telstra_pn.models.tpn_model import TPNModel, TPNListModel
from telstra_pn.exceptions import TPNLogicalError, TPNRefreshInconsistency
from telstra_pn.codes import vportstatus
from telstra_pn import __flags__

# Datacentres is a low change rate resource


class Endpoints(TPNListModel):
    def __init__(self, session):
        super().__init__(session)
        self._refkeys = ['endpointuuid']

        self.get_data()

    def get_data(self):
        cust = self.session.customeruuid
        response = self.session.api_session.call_api(
            path=f'/1.0.0/inventory/endpoints/customeruuid/{cust}'
        )

        if self.debug:
            print(f'Endpoints.get_data.response: {response}')

        self._update_data(response.get('endpointlist', []))

    def _update_data(self, data):
        self.data = {**self.data, 'list': data}

        for port in data:
            self.all.append(Endpoint(self, **port))


class Endpoint(TPNModel):
    def __new__(self, parent, **data):
        super().__init__(parent.session)
        self.data = data

        self.get_data(self)

        return self.detect_type()

    def _update_data(self, data: dict):
        self.data = {**data}

    def detect_type(self):
        if 'datacenter' in self.data:
            return SwitchPort(self.data['datacenter'][0])

    def get_data(self):
        response = self.session.api_session.call_api(
            path=f'/eis/1.0.0/endpoint/endpointuuid/{self.id}'
        )

        if self.debug:
            print(f'Endpoint.get_data.response: {response}')

        self._update_data(response)

    def display(self):
        if self.name:
            return self.name
        if self.switchname and self.portno:
            return f'{self.switchname}.{self.portno[0]}'


class SwitchPort(Endpoint):
    def _update_data(self, data: dict):
        port = data.get('port')
        if not port:
            raise TPNRefreshInconsistency(
                'SwitchPort detail does not contain "port" field'
            )
        if len(port) != 1:
            raise TPNRefreshInconsistency(
                f'SwitchPort detail contains {len(port)} ports'
            )
        port = port[0]
        newid: str = port.get('endpointuuid')
        if getattr(self, 'id', None) is None:
            self.id = newid
        else:
            if self.id != newid:
                raise TPNRefreshInconsistency(
                    'SwitchPort endpointuuid changed from '
                    f'{self.id} to {newid}'
                )

        dc = self.session.datacenters[self.data.get('datacenteruuid')]
        if dc:
            self.parent = dc

        self.vlans = []

        for vlan in port[0].get('vport', []):
            self.vlans.append(VLAN(self, **vlan))


class VPortEncapsulation(TPNModel):
    def __new__(self, parent, **data):
        self.session = parent.session
        self.debug = __flags__.get('debug')
        self.data = data

        self.get_data(self)

        return self.detect_type()

    def detect_type(self):
        if self.data.get('vporttype') == 'vlan':
            return VLAN(self.data)
        if self.data.get('vporttype') == 'vxlan':
            return VXLAN(self.data)
        if self.data.get('vporttype') == 'qinq':
            return QinQ(self.data)


class VLAN(VPortEncapsulation):
    def __init__(self, parent, **kwargs):
        super().__init__(parent.session)
        self.data = {**kwargs}

        self._update_date(kwargs)

    def _update_data(self, data: dict) -> None:
        self.vlanid = self.data.get('vportvalue', {}).get('vlan', {}).get('id')
        self.id = self.data.get('vportuuid')
        if self.data.get('vporttype') != 'vlan':
            raise TPNLogicalError(
                f'unkown vporttype {self.data.get("vporttype")}'
            )
        self.status = vportstatus(self.data.get('status'))


class VXLAN(VPortEncapsulation):
    pass


class QinQ(VPortEncapsulation):
    pass
