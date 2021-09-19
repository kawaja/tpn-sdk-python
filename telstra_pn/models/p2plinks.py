from datetime import datetime
from telstra_pn.models.tpn_model import TPNModel, TPNListModel
from telstra_pn.codes import status, renewal, latency
from telstra_pn.exceptions import TPNRefreshInconsistency

# P2PLink is a medium change rate resource


class P2PLinks(TPNListModel):
    def __init__(self, session):
        super().__init__(session)
        self._refkeys = ['description', 'linkid', 'tag']
        self._primary_key = 'id'
        cust = self.session.customeruuid
        self._url_path = f'/1.0.0/inventory/links/customer/{cust}'

        self.refresh()

    def _handle_tpn_data_error(self, exc: Exception) -> list:
        # 400 == no links returned
        if exc.status_code == 400:
            self.reset()
            return []

    def create(self, endpoints: list, latency: latency, duration_hours: int,
               bandwidth_mbps: int, renewal_option: renewal,
               topology: str) -> str:
        # create
        self.refresh()

    def _update_data(self, data: list) -> None:
        self.data = {**self.data, 'list': data}

        for link in data:
            self.additem(P2PLink(self, **link))


class P2PLink(TPNModel):
    def __init__(self, parent, **kwargs):
        super().__init__(parent.session)
        self.data = {**kwargs}
        self.parent = parent
        self._keyname_mappings = {
            'id': 'linkid',
            'endpoints': 'connections'
        }
        self._update_data(kwargs)
        self._url_path = f'/1.0.0/inventory/links/{self.id}'

    def _update_data(self, data: dict):
        self._update_keys(data)
        self.latency = latency(int(data.get('latency')))
        self.status = status(int(data.get('linkStatus')))
        if self.debug:
            print(f'contracts: {data.get("contracts", [])}')
        # When refreshing, a completely new P2PContracts (and n x P2PContract)
        # objects are created
        self.contracts = P2PContracts(self, data.get('contracts', []))
        # for contract in data.get('contracts', []):
        #     self.contracts.append(P2PContract(self, **contract))
        if self.debug:
            print(f' . added {len(self.contracts)} contracts')

    def delete(self) -> None:
        response = self.session.api_session.call_api(
            method='DELETE',
            path=f'/lis/1.0.0/link/{self.id}'
        )

        if self.debug:
            print(f'P2PLink.delete.response: {response}')

        self.parent.refresh()

    def get_statistics(self, from_date: datetime, to_date: datetime):
        from_iso = from_date.strftime('%Y-%m-%d-%H:%M:%S')
        to_iso = to_date.strftime('%Y-%m-%d-%H:%M:%S')
        response = self.session.api_session.call_api(
            path=f'/1.0.0/inventory/links-stats/flow/{self.id}/'
                 f'{from_iso}/{to_iso}'
        )

        if self.debug:
            print(f'P2PLink.get_stats.response: {response}')

        return response


class P2PContracts(TPNListModel):
    def __init__(self, parent, contracts):
        super().__init__(parent.session)
        self.parent = parent
        self._refkeys = ['contractid', 'seqno']
        self._primary_key = 'contractid'

        self.data = {'list': contracts}

        self.refresh()

    def display(self) -> None:
        return(f'{len(self)} contract(s)')

    def _update_data(self, data):
        self.data = {**self.data, 'list': data}
        self.reset()

        for contract in data['list']:
            self.additem(P2PContract(self.parent, **contract))


class P2PContract(TPNModel):
    def __init__(self, parent, **kwargs):
        super().__init__(parent.session)
        self.data = {**kwargs}
        self._url_path = (f'/1.0.0/inventory/links/{parent.id}'
                          f'/contract/{self.data["contractid"]}')
        self._update_data(kwargs, linkid=parent.id)
        self._keyname_mappings = {
            'duration_hours': 'duration',
            'hourly_price': 'price',
            'currency': 'currencyID'
        }
        # these extra fields are actually copied from the parent
        # P2PLink when the contract detail API is called
        self.refresh_if_null = [
            'description', 'latency', 'linkid', 'connection', 'tag', 'type',
            'protected_latency', 'latency_value', 'protected_latency_value',
            'billing-id'
        ]

    def _update_data(self, data: dict, linkid: str = None) -> None:
        if linkid is None:
            linkid = data.get('linkid')

        self.contractid: str = data.get('contractid')
        if self.__dict__.get('id', None) is None:
            self.id = self.contractid
        else:
            if self.id != self.contractid:
                raise TPNRefreshInconsistency(
                    'P2PContract contractid changed from '
                    f'{self.id} to {self.contractid}'
                )

        # linkid is from parent
        if self.__dict__.get('linkid', None) is None:
            self.linkid = linkid
        else:
            if self.linkid != linkid:
                raise TPNRefreshInconsistency(
                    'P2PContract linkid changed from '
                    f'{self.linkid} to {linkid}'
                )

        self._update_keys(data)
        self.seqno = self.id[self.id.find('.')+1:]
        # self.duration_hours = data.get('duration')  # convert?
        # self.hourly_price = data.get('price')
        self.status = status(data.get('contractStatus'))
        # self.version = data.get('version')
        # self.currency = data.get('currencyID')
        self.renewal = renewal(int(data.get('renewal-option')))

    def delete(self) -> None:
        # delete
        self.refresh()
