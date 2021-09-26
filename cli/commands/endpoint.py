from nubia import argument, command, context
from cli.cli import CLI


@command('endpoints')
class CLIEndpoints(CLI):
    '''Interact with TPN endpoints'''
    def __init__(self):
        self.ctx = context.get_context()
        self.obj = self.ctx.tpns.endpoints

        super().__init__()

    @command
    def list(self):
        '''list TPN endpoints'''
        self.output_list()

    @command
    @argument('endpoint',
              description='The name or uuid representing a TPN endpoint',
              positional=True)
    def info(self, endpoint: str):
        '''Show information about a TPN endpoint'''
        self.output_single(endpoint)
