import enum
from telstra_pn.models.tpn_model import (TPNModel, TPNListModel,
                                         TPNModelSubclassesMixin)
from telstra_pn.exceptions import (TPNRefreshInconsistency)
# from telstra_pn.exceptions import (TPNLogicalError, TPNRefreshInconsistency)
# from telstra_pn.codes import vportstatus
from telstra_pn import __flags__

# Endpoints is are high change rate resource
# Contracts is are high change rate resource


class Endpoints(TPNListModel):
    def __init__(self, session):
        super().__init__(session)
        self._refkeys = ['endpointuuid', 'name']
        self._primary_key = 'endpointuuid'
        cust = self.session.customeruuid
        self._url_path = f'/1.0.0/inventory/endpoints/customeruuid/{cust}'
        self._get_deref = 'endpointlist'

        _endpoint_types = self._populate_endpoint_types()
        self.types = enum.Enum('EndpointType', _endpoint_types)

        self.refresh()

    def _populate_endpoint_types(self):
        response = self.session.api_session.call_api(
            path='/eis/1.0.0/switchporttype'
        )
        return {
            eptype['switchporttypename']: eptype['switchporttypeuuid']
            for eptype in response
        }

    def _update_data(self, data: list) -> None:
        self.data = {**self.data, 'list': data}

        for port in data:
            self.additem(Endpoint(self, **port))

    def display(self):
        return f'{len(self)} endpoints'


class Endpoint(TPNModel, TPNModelSubclassesMixin):
    def __init__(self, parent, **data):
        super().__init__(parent.session)

        self.data = {**self.data, **data}
        self.id = data['endpointuuid']
        self.parent = parent
        self.refresh_if_null = [
            'creationdate', 'enabled', 'lastmodifieddate', 'status'
        ]
        self._keyname_mappings = {
            'id': 'endpointuuid'
        }
        self._defaults = {
            'name': '-'
        }
        self._url_path = self.get_url_path(data)
        self.type = self.__class__.__name__

    @staticmethod
    def get_url_path(data: dict) -> str:
        return f'/eis/1.0.0/endpoint/endpointuuid/{data["endpointuuid"]}'


class SwitchPort(Endpoint):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self._update_data(kwargs)

    @staticmethod
    def _is_a(data, parent) -> bool:
        return parent.types(data['endpointTypeuuid']) == parent.types.Port

    def _update_data(self, data: dict):
        self.data = {**self.data, **data}
        portarr = self.data.get('portno')
        if portarr is None:
            raise TPNRefreshInconsistency(
                'SwitchPort detail does not contain "portno" field'
            )
        if len(portarr) != 1:
            raise TPNRefreshInconsistency(
                f'SwitchPort detail contains {len(portarr)} ports'
            )
        self.port = portarr[0]
        newid: str = self.data.get('endpointuuid')
        if self.id != newid:
            raise TPNRefreshInconsistency(
                'SwitchPort endpointuuid changed from '
                f'{self.id} to {newid}'
            )

        dc = self.session.datacentres[self.data.get('datacenteruuid')]
        if dc:
            self.parent = dc

        self.vports = []

#        for vport in data:
#            self.additem(Endpoint(self, **port))
#        for vlan in port.get('vport', []):
#            self.vlans.append(VLAN(self, **vlan))

    def display(self) -> str:
        if self.name:
            return self.name
        if self.switchname and self.portno:
            return f'{self.switchname}.{self.portno[0]}'
        return 'SwitchPort'


class VNF(Endpoint):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.refresh_if_null = [
            'creationdate', 'enabled',
            'lastmodifieddate', 'status', 'name'
        ]
        self._update_data(kwargs)

    @staticmethod
    def _is_a(data, parent) -> bool:
        return parent.types(data['endpointTypeuuid']) == parent.types.VNF

    def _update_data(self, data: dict) -> None:
        self.data = {**self.data, **data}
        self._update_keys(self.data)

    def display(self) -> str:
        if self.name:
            return f'VNF ({self.name})'
        return 'VNF'


class VPortEncapsulation(TPNModel, TPNModelSubclassesMixin):
    def __new__(self, parent, **data):
        self.session = parent.session
        self.debug = __flags__.get('debug')
        self.data = data

        self.get_data(self)

        return self.detect_type()

    def detect_type(self):
        if self.data.get('vporttype') == 'vlan':
            return VLAN(self.data)
        # if self.data.get('vporttype') == 'vxlan':
        #     return VXLAN(self.data)
        if self.data.get('vporttype') == 'qinq':
            return QinQ(self.data)


class VLAN(VPortEncapsulation):
    def __init__(self, parent, **kwargs):
        super().__init__(parent.session)
        self.data = {**kwargs}

        self._update_date(kwargs)

    @staticmethod
    def _is_a(self, data, parent=None) -> bool:
        return data.get('vporttype') == 'vlan'

    # self.vlanid = self.data.get('vportvalue', {}).get('vlan', {}).get('id')
    # self.id = self.data.get('vportuuid')
    # if self.data.get('vporttype') != 'vlan':
    #     raise TPNLogicalError(
    #         f'unkown vporttype {self.data.get("vporttype")}'
    #     )
    # self.status = vportstatus(self.data.get('status'))

# VXLAN endpoints are not currently implemented
# class VXLAN(VPortEncapsulation):
#     pass


class QinQ(VPortEncapsulation):
    pass


# class VNF(Endpoint):
#     pass
