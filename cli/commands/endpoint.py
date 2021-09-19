from termcolor import cprint
from nubia import argument, command, context
from cli.cli import CLI


@command('endpoints')
class Endpoints(CLI):
    '''Interact with TPN endpoints'''

    def __init__(self):
        self.ctx = context.get_context()
        cprint(f'tpns: {self.ctx.tpns}')
        self.obj = self.ctx.tpns.endpoints
        self.names = [
            ('Name', 'name'),
            ('UUID', 'endpointuuid'),
            ('Type', 'type'),
            ('Creation Date', 'creationdate'),
            ('Datacenter Code', 'datacentercode'),
            ('Last Modified Date', 'lastmodifieddate'),
            ('Enabled', 'enabled'),
            ('Status', 'status'),
        ]

        super().__init__()

    @command
    def list(self):
        '''list TPN endpoints'''
        self.output_list(self.obj)

    @command
    @argument('endpoint',
              description='The name or uuid representing a TPN endpoint',
              positional=True)
    def info(self, endpoint: str):
        '''
        show information about a TPN endpoint

        '''
        dc = self.obj[endpoint]
        if dc:
            self.output_single(dc)
        else:
            if self.ctx.text:
                cprint(f'endpoint {endpoint} not found')
            else:
                cprint('{}')
