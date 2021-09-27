from telstra_pn.models.tpn_model import TPNModel, TPNListModel

# Datacentres is a low change rate resource


class Datacentres(TPNListModel):
    table_names = [
        ('Code', 'datacentercode'),
        ('Name', 'datacentername'),
        ('UUID', 'datacenteruuid'),
        ('City', 'cityname'),
        ('Country', 'countryname'),
        ('VNF Capable', 'vnf_capable')
    ]
    display_keys = [k[1] for k in table_names]
    type_name = 'datacenter'

    def __init__(self, session):
        super().__init__(session)
        self.vnf = []
        self._refkeys = ['datacentercode', 'datacenteruuid']
        self._primary_key = 'datacenteruuid'
        self._url_path = '/1.0.0/inventory/datacenters'
        self._get_deref = 'datacenters'
        self._vnf_capable = self._populate_vnf_capable()
        self.refresh()

    def _populate_vnf_capable(self):
        response = self.session.api_session.call_api(
            path='/eis/1.0.0/datacenters/switchtypename/vnf'
        )
        return [dc['datacenteruuid'] for dc in response['datacenters']]

    def display(self) -> str:
        return f'{len(self.all)} datacentres'

    def _update_data(self, data) -> None:
        self.data = {**self.data, 'list': data}

        for dc in data:
            self.additem(Datacentre(self, **dc))


class Datacentre(TPNModel):
    def __init__(self, parent, **data):
        super().__init__(parent.session)
        self.data = data
        self.data['vnf_capable'] = (self.data['datacenteruuid']
                                    in parent._vnf_capable)
        self._keyname_mappings = {
            'id': 'datacenteruuid'
        }
        self.refresh()

    def _update_data(self, data: dict) -> None:
        self.data = {**self.data, **data}
        return super()._update_data(data)

    def display(self) -> str:
        return self.datacentercode
