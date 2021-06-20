__version__ = "0.1"
__flags__ = {'debug': False}

# import codes
from telstra_pn.codes import *  # noqa

# import models
from telstra_pn.models.datacentres import Datacentres  # noqa
from telstra_pn.models.p2plinks import P2PLinks  # noqa
from telstra_pn.models.endpoints import Endpoints  # noqa

# session needs to be at the end, as it uses definitions of the other models
from telstra_pn.models.session import Session  # noqa
