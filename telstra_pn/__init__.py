__version__ = "0.1"
__flags__ = {
    'debug': False,
    'debug_mocks': False,
    'debug_getattr': False,
    'debug_api': False
}

# import codes
from telstra_pn.codes import *  # noqa

# import models
from telstra_pn.models.datacentres import Datacentres  # noqa
from telstra_pn.models.p2plinks import P2PLinks  # noqa
from telstra_pn.models.endpoints import Endpoints  # noqa
from telstra_pn.models.topologies import Topologies  # noqa

# session needs to be at the end, as it uses definitions of the other models
from telstra_pn.models.session import Session  # noqa
