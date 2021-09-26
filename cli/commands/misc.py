from nubia import command, context
from termcolor import cprint
from cli.cli import CLI


@command('output-style', help='set output style')
class CLIOutput:
    def __init__(self):
        self.ctx = context.get_context()

    @command(help='set output to json')
    def json(self):
        self.ctx.json = True

    @command(help='set output to text')
    def text(self):
        self.ctx.text = True

    @command(help='show current output mode')
    def show(self):
        cprint(f'output is set to \'{self.ctx.output}\'')


@command('unimplemented-types', help='display list of unimplemented subtypes')
class CLIUnimplemented(CLI):
    def __init__(self):
        self.ctx = context.get_context()

    @command(help='unimplemented endpoints')
    def endpoints(self):
        self.obj = self.ctx.tpns.endpoints
        self.output_list_text(filter=lambda i: i.type == 'Endpoint',
                              table_names_overrides=[('Name', 'name'),
                                                     ('UUID', 'endpointuuid'),
                                                     ('Type', 'type'),
                                                     ('endpointtypeuuid',
                                                      'endpointTypeuuid')])
