from telstra_pn.models.tpn_model import TPNModel, TPNListModel

# Datacentres is a low change rate resource


class Datacentres(TPNListModel):
    def __init__(self, session):
        super().__init__(session)
        self.vnf = []
        self._refkeys = ['datacentercode', 'datacenteruuid']
        self._primary_key = 'datacenteruuid'

        self.refresh()

    def _get_data(self):
        response = self.session.api_session.call_api(
            path='/1.0.0/inventory/datacenters'
        )

        if self.debug:
            print(f'Datacentres.get_data.response: {response}')

        return response.get('datacenters', [])

    def display(self):
        return f'{len(self.all)} datacentres'

    def _update_data(self, data):
        self.data = {**self.data, 'list': data}

        for dc in data:
            self.additem(Datacentre(self, **dc))


class Datacentre(TPNModel):
    def __init__(self, parent, **data):
        super().__init__(parent.session)
        self.data = data

    def display(self):
        return self.datacentercode
