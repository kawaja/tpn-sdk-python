import json
from termcolor import cprint
from nubia import context, command

tpns = None


class CLI:
    def __init__(self):
        self.ctx = context.get_context()

    @command
    def refresh(self):
        '''refresh information from the TPN platform'''
        self.obj.refresh()

    def output_single(self, data: dict) -> None:
        if self.ctx.text:
            return self.output_single_text(data)

        if self.ctx.json:
            return self.output_single_json(data)

        return 1

    def output_single_text(self, data: dict) -> None:
        if not data:
            cprint('not found')

        names = self.names

        if names is None:
            names = [(x, x) for x in data.keys()]
        for (name, key) in names:
            disp = data.get(key, '<unknown>')
            cprint(f'{name}: {disp}')

    def output_single_json(self, data: dict) -> None:
        outitem = {}
        for (name, key) in self.names:
            outitem[name] = data.get(key, '<unknown>')

        cprint(json.dumps(outitem))

    def output_list(self, data: dict) -> None:
        if self.ctx.text:
            return self.output_list_text(data)

        if self.ctx.json:
            return self.output_list_json(data)

        return 1

    def output_list_text(self, data: dict) -> None:
        widths = {name[1]: len(name[0]) for name in self.names}
        for item in data:
            for (name, key) in self.names:
                disp = str(item.get(key, '<unknown>'))
                if widths[key] < len(disp):
                    widths[key] = len(disp)

        if self.ctx.headers:
            output = ''
            for (name, key) in self.names:
                output += '{item:<{width}} '.format(item=name,
                                                    width=widths[key])
            cprint(output)
            output = ''
            for (name, key) in self.names:
                output += '-'*widths[key] + ' '
            cprint(output)

        for item in data:
            output = ''
            for (name, key) in self.names:
                disp = str(item.get(key, '<unknown>'))
                output += '{item:<{width}} '.format(item=disp,
                                                    width=widths[key])
            cprint(output)

    def output_list_json(self, data: dict) -> None:
        outdata = []
        for item in data:
            outitem = {}
            for (name, key) in self.names:
                outitem[name] = str(item.get(key, '<unknown>'))
            outdata.append(outitem)

        cprint(json.dumps(outdata))
