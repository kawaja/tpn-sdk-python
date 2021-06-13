from telstra_pn.models.tpn_model import TPNModel

# Datacentres is a low change rate resource


class Datacentres(TPNModel):
    def __init__(self, session):
        self.session = session
        self.data = {}
        self.all = []
        self.vnf = []

        self.get_data()

    def get_data(self):
        response = self.session.api_session.call_api(
            path='/1.0.0/inventory/datacenters'
        )

        print(f'Datacentres.get_data.response: {response}')

        self.data = {**self.data, **response}

    def refresh(self) -> None:
        self.get_data()


class Datacentre(TPNModel):
    def __init__(self, data):
        self.data = data
