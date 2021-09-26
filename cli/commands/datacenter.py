from nubia import argument, command, context
from cli.cli import CLI


@command('datacenters')
class CLIDatacenters(CLI):
    '''Interact with TPN datacenters'''
    def __init__(self):
        self.ctx = context.get_context()
        self.obj = self.ctx.tpns.datacentres

        super().__init__()

    @command
    def list(self):
        '''List TPN datacenters'''
        self.output_list()

    @command
    @argument('datacenter',
              description='The code or uuid representing a TPN datacenter',
              positional=True)
    def info(self, datacenter: str):
        '''Show information about a TPN datacenter'''
        self.output_single(datacenter)
