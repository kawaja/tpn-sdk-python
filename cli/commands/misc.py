from nubia import command, context
from termcolor import cprint


@command('output-style', help='set output style')
class Output:
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
