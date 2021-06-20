from datetime import datetime
from telstra_pn.models.tpn_model import TPNModel, TPNListModel
from telstra_pn.codes import status, renewal, latency
from telstra_pn.exceptions import TPNDataError, TPNRefreshInconsistency

# P2PLink is a medium change rate resource


class P2PLinks(TPNListModel):
    def __init__(self, session):
        super().__init__(session)
        self._refkeys = ['description', 'linkid', 'tag']

        self.get_data()

    def get_data(self):
        cust = self.session.customeruuid
        try:
            response = self.session.api_session.call_api(
                path=f'/1.0.0/inventory/links/customer/{cust}'
            )
        except TPNDataError as exc:
            # 400 == no links returned
            if exc.status_code == 400:
                self.all = []
                return

        if self.debug:
            print(f'P2PLinks.get_data.response: {response}')

        self._update_data(response)

    def create(self, endpoints: list, latency: latency, duration_hours: int,
               bandwidth_mbps: int, renewal_option: renewal,
               topology: str) -> str:
        # create
        self.get_data()

    def _update_data(self, data):
        self.data = {**self.data, 'list': data}
        self.all = []

        for link in data:
            print(f'adding link: {link["linkid"]}')
            self.all.append(P2PLink(self, **link))


class P2PLink(TPNModel):
    def __init__(self, parent, **kwargs):
        super().__init__(parent.session)
        self.data = {**kwargs}
        self.parent = parent

        self._update_data(kwargs)

    def _update_data(self, data):
        self.description = data.get('description')
        self.id = data.get('linkid')
        self.latency = latency(int(data.get('latency')))
        self.tag = data.get('tag')
        self.endpoints = data.get('connections')
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

    def get_data(self):
        response = self.session.api_session.call_api(
            path=f'/1.0.0/inventory/links/{self.id}'
        )

        if self.debug:
            print(f'P2PLink.get_data.response: {response}')

        self._update_data(response)

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

        self._update_data(contracts)

    def display(self) -> None:
        return(f'{len(self.all)} Contracts')

    def _update_data(self, data):
        self.data = {**self.data, 'list': data}
        self.all = []

        for contract in data:
            self.all.append(P2PContract(self.parent, **contract))


class P2PContract(TPNModel):
    def __init__(self, parent, **kwargs):
        super().__init__(parent.session)
        self.data = {**kwargs}
        # these extra fields are actually copied from the parent
        # P2PLink when the contract detail API is called
        self.refresh_if_null = [
            'description', 'latency', 'linkid', 'connection', 'tag', 'type',
            'protected_latency', 'latency_value', 'protected_latency_value',
            'billing-id'
        ]

        self._update_data(kwargs, linkid=parent.id)

    def _update_data(self, data: dict, linkid: str) -> None:
        newid: str = data.get('contractid')
        if getattr(self, 'id', None) is None:
            self.id = newid
        else:
            if self.id != newid:
                raise TPNRefreshInconsistency(
                    'P2PContract contractid changed from '
                    f'{self.id} to {newid}'
                )

        if getattr(self, 'linkid', None) is None:
            self.linkid = linkid
        else:
            if self.linkid != linkid:
                raise TPNRefreshInconsistency(
                    'P2PContract linkid changed from '
                    f'{self.linkid} to {linkid}'
                )

        self.seqno = self.id[self.id.find('.')+1:]
        self.duration_hours = data.get('duration')  # convert?
        self.hourly_price = data.get('price')
        self.status = status(data.get('contractStatus'))
        self.version = data.get('version')
        self.currency = data.get('currencyID')
        self.renewal = renewal(int(data.get('renewal-option')))

    def get_data(self):
        response = self.session.api_session.call_api(
            path=f'/1.0.0/inventory/links/{self.linkid}/contract/{self.id}'
        )

        if self.debug:
            print(f'P2PContract.get_data.response: {response}')

        self._update_data(response, response.get('linkid'))

    def delete(self) -> None:
        # delete
        self.get_data()
