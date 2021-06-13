__version__ = "0.1"
__flags__ = {'debug': False}

# import models
from telstra_pn.models.datacentres import Datacentres  # noqa

# session needs to be at the end, as it uses definitions of the other models
from telstra_pn.models.session import Session  # noqa
