from telstra_pn.codes import topologystatus
from telstra_pn.models.tpn_model import TPNModel, TPNListModel

# Topologies is a medium change rate resource


class Topologies(TPNListModel):
    table_names = [
        ('Name', 'name'),
        ('UUID', 'topologyuuid'),
        ('Description', 'description'),
        ('Status', 'status')
    ]
    display_keys = [
        'topologyuuid', 'name', 'description', 'status', 'creation_date'
    ]

    def __init__(self, session):
        super().__init__(session)
        self.vnf = []
        self._refkeys = ['topologyname', 'topologyuuid']
        self._primary_key = 'topologyuuid'
        self._url_path = '/ttms/1.0.0/topology_tag'

        self.refresh()

    def _update_data(self, data: list):
        self.data = {**self.data, 'list': data}
        self._update_keys(data)

        for topo in data:
            self.additem(Topology(self, **topo))

    def display(self):
        return(f'{len(self)} topologies')


class Topology(TPNModel):
    def __init__(self, parent, **data):
        super().__init__(parent.session)
        self.data = data
        self._keyname_mappings = {
            'topologyname': 'name',
            'topologyuuid': 'uuid',
            'id': 'uuid'
        }

        self._update_data(data)

    def _update_data(self, data):
        self._update_keys(data)
        self.status = topologystatus(str(data.get('status')))

    def display(self):
        return self.topologyname
