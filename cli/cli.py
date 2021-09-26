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

    def output_single(self, itemid: str) -> None:
        item = self.obj[itemid]
        if item:
            if self.ctx.text:
                for key in self.obj.display_keys:
                    disp = item.get(key, '<unknown>')
                    cprint(f'{key}: {disp}')
            if self.ctx.json:
                outitem = {}
                for key in self.obj.display_keys:
                    outitem[key] = item.get(key, '<unknown>')

                cprint(json.dumps(outitem))
        else:
            if self.ctx.text:
                cprint(f'{self.obj.type_name} {itemid} not found')
            else:
                cprint('{}')

        return 1

    def output_list(self) -> None:
        if self.ctx.text:
            return self.output_list_text()
        if self.ctx.json:
            return self.output_list_json()
        return 1

    def output_list_text(self) -> None:
        names = self.obj.table_names
        widths = {name[1]: len(name[0]) for name in names}
        print(f'widths: {widths}')
        for item in self.obj:
            for (name, key) in names:
                disp = str(item.get(key, '<unknown>'))
                if widths[key] < len(disp):
                    widths[key] = len(disp)
        print(f'widths: {widths}')

        if self.ctx.headers:
            output = ''
            for (name, key) in names:
                output += '{item:<{width}} '.format(item=name,
                                                    width=widths[key])
            cprint(output)
            output = ''
            for (name, key) in names:
                output += '-'*widths[key] + ' '
            cprint(output)

        for item in self.obj:
            output = ''
            for (name, key) in names:
                disp = str(item.get(key, '<unknown>'))
                output += '{item:<{width}} '.format(item=disp,
                                                    width=widths[key])
            cprint(output)

    def output_list_json(self) -> None:
        outdata = []
        names = self.obj.table_names
        for item in self.obj:
            outitem = {}
            for (name, key) in names:
                outitem[name] = str(item.get(key, '<unknown>'))
            outdata.append(outitem)

        cprint(json.dumps(outdata))
