from nubia import argument, command, context
from cli.cli import CLI


@command('topologies')
class CLITopologies(CLI):
    '''Interact with TPN topologies'''
    def __init__(self):
        self.ctx = context.get_context()
        self.obj = self.ctx.tpns.topologies

        super().__init__()

    @command
    def list(self):
        '''List TPN topologies'''
        self.output_list()

    @command
    @argument('topology',
              description='The code or uuid representing a TPN topology',
              positional=True)
    def info(self, topology: str):
        '''Show information about a TPN topology'''
        self.output_single(topology)
