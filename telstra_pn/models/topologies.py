from telstra_pn.codes import topologystatus
from telstra_pn.models.tpn_model import TPNModel, TPNListModel

# Topologies is a medium change rate resource


class Topologies(TPNListModel):
    def __init__(self, session):
        super().__init__(session)
        self.vnf = []
        self._refkeys = ['topologyname', 'topologyuuid']
        self._primary_key = 'uuid'

        self.refresh()

    def _get_data(self) -> list:
        response = self.session.api_session.call_api(
            path='/ttms/1.0.0/topology_tag'
        )

        if self.debug:
            print(f'Topologies.get_data.response: {response}')

        return response

    def _update_data(self, data: list):
        self.data = {**self.data, 'list': data}

        for topo in data:
            self.additem(Topology(self, **topo))

    def display(self):
        return(f'{len(self)} topologies')


class Topology(TPNModel):
    def __init__(self, parent, **data):
        super().__init__(parent.session)
        self.data = data

        self._update_data(data)

    def _update_data(self, data):
        self.id = data.get('uuid')
        self.topologyname = data.get('name')
        self.topologyuuid = data.get('uuid')
        self.status = topologystatus(str(data.get('status')))

    def display(self):
        return self.topologyname
