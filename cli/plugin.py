import argparse
from cli.context import CLIContext
from nubia import PluginInterface


class CLIPlugin(PluginInterface):
    def create_context(self):
        '''
        Must create an object that inherits from `Context` parent class.
        The plugin can return a custom context but it has to inherit from the
        correct parent class.
        '''
        return CLIContext()

    def validate_args(self, args):
        '''
        This will be executed when starting nubia, the args passed is a
        dict-like object that contains the argparse result after parsing the
        command line arguments. The plugin can choose to update the context
        with the values, and/or decide to raise `ArgsValidationError` with
        the error message.
        '''
        print(f'validate_args: {args}')
        pass

    def get_opts_parser(self, add_help=True):
        '''
        Builds the ArgumentParser that will be passed to , use this to
        build your list of arguments that you want for your shell.
        '''
        print('get_opts_parser')
        opts_parser = argparse.ArgumentParser(
            description='TPN CLI Utility',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=add_help,
        )
        opts_parser.add_argument(
            '--debug',
            '-d',
            action='store_true',
            help='Display debugging information from TPN library'
        )
        opts_parser.add_argument(
            '--headers',
            default=True,
            help='Display headers in list outputs'
        )
        opts_parser.add_argument(
            '--output',
            default='text',
            choices=['text', 'json'],
            help='Display headers in list outputs'
        )
        opts_parser.add_argument(
            '--verbose',
            '-v',
            action='count',
            default=0,
            help='Increase verbosity, can be specified ' 'multiple times',
        )
        opts_parser.add_argument(
            '--stderr',
            '-s',
            action='store_true',
            help='By default the logging output goes to a '
            'temporary file. This disables this feature '
            'by sending the logging output to stderr',
        )
        return opts_parser
