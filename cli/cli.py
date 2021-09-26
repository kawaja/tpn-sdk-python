import json
import enum
from types import FunctionType
from termcolor import cprint
from nubia import context, command

tpns = None


def display_format(value):
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, enum.Enum):
        return str(value.value)
    if isinstance(value, bool):
        return 'true' if bool else 'false'


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
                    disp = display_format(item.get(key, '<unknown>'))
                    cprint(f'{key}: {disp}')
            if self.ctx.json:
                outitem = {}
                for key in self.obj.display_keys:
                    if item.get(key):
                        outitem[key] = display_format(item.get(key))

                cprint(json.dumps(outitem))
        else:
            if self.ctx.text:
                cprint(f'{self.obj.type_name} {itemid} not found')
            else:
                cprint('{}')

        return 1

    def output_list(self, **kwargs) -> None:
        if self.ctx.text:
            return self.output_list_text(**kwargs)
        if self.ctx.json:
            return self.output_list_json(**kwargs)
        return 1

    def output_list_text(self,
                         filter: FunctionType = None,
                         table_names_overrides: list = None) -> None:
        if table_names_overrides is None:
            names = self.obj.table_names
        else:
            names = table_names_overrides

        widths = {name[1]: len(name[0]) for name in names}
        found_item = False
        for item in self.obj:
            if filter is not None:
                if filter(item) is False:
                    continue
            found_item = True
            for (name, key) in names:
                disp = display_format(item.get(key, '<unknown>'))
                if widths[key] < len(disp):
                    widths[key] = len(disp)

        if not found_item:
            cprint('no items found')
            return

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
            if filter is not None:
                if filter(item) is False:
                    continue
            output = ''
            for (name, key) in names:
                disp = display_format(item.get(key, '<unknown>'))
                output += '{item:<{width}} '.format(item=disp,
                                                    width=widths[key])
            cprint(output)

    def output_list_json(self) -> None:
        outdata = []
        names = self.obj.table_names
        for item in self.obj:
            outitem = {}
            for (name, key) in names:
                outitem[name] = display_format(item.get(key, '<unknown>'))
            outdata.append(outitem)

        cprint(json.dumps(outdata))
