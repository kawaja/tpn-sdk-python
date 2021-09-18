from telstra_pn.models.tpn_model import TPNModel, TPNListModel

# Datacentres is a low change rate resource


class Datacentres(TPNListModel):
    def __init__(self, session):
        super().__init__(session)
        self.vnf = []
        self._refkeys = ['datacentercode', 'datacenteruuid']
        self._primary_key = 'datacenteruuid'
        self._url_path = '/1.0.0/inventory/datacenters'
        self._get_deref = 'datacenters'
        self.refresh()

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
        self.refresh()

    def display(self) -> str:
        return self.datacentercode
