from termcolor import cprint
from nubia import argument, command, context
from cli.cli import CLI


@command('datacenters')
class Datacenters(CLI):
    '''Interact with TPN datacenters'''

    def __init__(self):
        self.ctx = context.get_context()
        self.obj = self.ctx.tpns.datacentres
        self.names = [
            ('Code', 'datacentercode'),
            ('Name', 'datacentername'),
            ('UUID', 'datacenteruuid'),
            ('City', 'cityname'),
            ('Country', 'countryname')
        ]

        super().__init__()

    @command
    def list(self):
        '''list TPN datacenters'''
        self.output_list(self.obj)

    @command
    @argument('datacenter',
              description='The code or uuid representing a TPN datacenter',
              positional=True)
    def info(self, datacenter: str):
        '''
        show information about a TPN datacenter

        '''
        dc = self.obj[datacenter]
        if dc:
            self.output_single(dc)
        else:
            if self.ctx.text:
                cprint(f'datacenter {datacenter} not found')
            else:
                cprint('{}')
