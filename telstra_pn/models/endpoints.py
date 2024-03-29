import enum
from telstra_pn.models.tpn_model import (TPNModel, TPNListModel,
                                         TPNModelSubclassesMixin)
from telstra_pn.exceptions import (TPNRefreshInconsistency)
# from telstra_pn.exceptions import (TPNLogicalError, TPNRefreshInconsistency)
# from telstra_pn.codes import vportstatus
from telstra_pn import __flags__

# Endpoints is a high change rate resource
# Contracts is a high change rate resource


class Endpoints(TPNListModel):
    table_names = [
        ('Name', 'name'),
        ('UUID', 'id'),
        ('Datacenter Code', 'datacentercode'),
        ('Type', 'type'),
        ('Creation Date', 'creationdate'),
        ('Last Modified Date', 'lastmodifieddate'),
        ('Status', 'status')
    ]
    display_keys = [k[1] for k in table_names]
    type_name = 'endpoint'

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
        self.data = {**self.data, 'list': self._extend_data(data, Endpoint)}

        for port in self.data['list']:
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
    type_name = 'switchport'

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
            ) from None
        if len(portarr) != 1:
            raise TPNRefreshInconsistency(
                f'SwitchPort detail contains {len(portarr)} ports'
            ) from None
        self.port = portarr[0]
        newid: str = self.data.get('endpointuuid')
        if self.id != newid:
            raise TPNRefreshInconsistency(
                'SwitchPort endpointuuid changed from '
                f'{self.id} to {newid}'
            ) from None

        dc = self.session.datacentres[self.data.get('datacentercode')]
        if dc:
            self.parent = dc
        else:
            self.parent = 'unknown DC'

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


class IPVPN(Endpoint):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.refresh_if_null = [
            'creationdate', 'enabled',
            'lastmodifieddate', 'status', 'name'
        ]
        self._update_data(kwargs)

    @staticmethod
    def _is_a(data, parent) -> bool:
        return parent.types(data['endpointTypeuuid']) == parent.types.IPVPN

    def _update_data(self, data: dict) -> None:
        self.data = {**self.data, **data}
        return super()._update_data(data)

    def display(self) -> str:
        if self.name:
            return f'IPVPN ({self.name})'
        return 'IPVPN'


class ConstructedProduct(Endpoint):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.refresh_if_null = [
            'creationdate', 'enabled',
            'lastmodifieddate', 'status', 'name'
            'product_definition_uuid', 'price', 'currency'
        ]
        self._update_data(kwargs)
        self._url_path = f'/cpms/1.0.0/endpoint/{self.id}'

    def _handle_tpn_data_error(self, exc: Exception) -> list:
        # 400 == failed CP missing in cpms? set error message
        # to avoid constant refreshing
        if exc.status_code == 400:
            self.data.setdefault('product_definition_uuid', '<error>')
            self.data.setdefault('price', '<error>')
            self.data.setdefault('currency', '<error>')

    @staticmethod
    def _is_a(data, parent) -> bool:
        return parent.types(data['endpointTypeuuid']) == parent.types.CP

    def _update_data(self, data: dict) -> None:
        self.data = {**self.data, **data}
        return super()._update_data(data)

    def display(self) -> str:
        if self.name:
            return f'ConstructedProduct ({self.name})'
        return 'ConstructedProduct'


class Exchange(Endpoint):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.refresh_if_null = [
            'creationdate', 'enabled',
            'lastmodifieddate', 'status', 'name'
        ]
        self._update_data(kwargs)

    @staticmethod
    def _is_a(data, parent) -> bool:
        return parent.types(data['endpointTypeuuid']) == parent.types.Exchange

    def _update_data(self, data: dict) -> None:
        self.data = {**self.data, **data}
        return super()._update_data(data)

    def display(self) -> str:
        if self.name:
            return f'Exchange ({self.name})'
        return 'Exchange'


class DIA(Endpoint):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.refresh_if_null = [
            'creationdate', 'enabled',
            'lastmodifieddate', 'status', 'name'
        ]
        self._update_data(kwargs)

    @staticmethod
    def _is_a(data, parent) -> bool:
        return parent.types(data['endpointTypeuuid']) == parent.types.DIA

    def _update_data(self, data: dict) -> None:
        self.data = {**self.data, **data}
        return super()._update_data(data)

    def display(self) -> str:
        if self.name:
            return f'DIA ({self.name})'
        return 'DIA'


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
        return super()._update_data(data)

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
