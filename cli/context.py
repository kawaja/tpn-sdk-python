import os
from nubia import context
from nubia import exceptions
from nubia import eventbus
import telstra_pn


class CLIContext(context.Context):
    def __init__(self):
        self.tpns = None
        super().__init__()

    def on_connected(self, *args, **kwargs):
        if self.debug:
            telstra_pn.__flags__['debug'] = True
            telstra_pn.__flags__['debug_api'] = True
        self.tpns = telstra_pn.Session(token=os.environ['TPNTOKEN'])

    def on_cli(self, cmd, args):
        # dispatch the on connected message
        self.set_options(args)
        self.registry.dispatch_message(eventbus.Message.CONNECTED)

    def on_interactive(self, args):
        self.set_options(args)
        ret = self._registry.find_command("connect").run_cli(args)
        if ret:
            raise exceptions.CommandError("Failed starting interactive mode")
        # dispatch the on connected message
        self.registry.dispatch_message(eventbus.Message.CONNECTED)

    def set_options(self, args):
        self.text = args.output == 'text'
        self.output = args.output
        self.headers = args.headers
        self.verbose = args.verbose
        self.debug = args.debug

    @property
    def headers(self):
        with self._lock:
            return self._headers

    @headers.setter
    def headers(self, headers):
        with self._lock:
            self._headers = headers

    @property
    def json(self):
        with self._lock:
            return self._json

    @json.setter
    def json(self, json):
        with self._lock:
            self.output = 'json'
            self._json = json
            self._text = not json

    @property
    def text(self):
        with self._lock:
            return self._text

    @text.setter
    def text(self, text):
        with self._lock:
            self.output = 'text'
            self._text = text
            self._json = not text
