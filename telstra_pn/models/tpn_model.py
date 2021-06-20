from typing import Any
import inspect
from telstra_pn import __flags__
from telstra_pn.exceptions import TPNLogicalError


class TPNModel:
    def __init__(self, session):
        self.session = session
        self.debug = __flags__.get('debug')
        self.data = {}
        self._is_refreshing = False

    def __getattr__(self, name: str) -> Any:
        if __flags__.get('debug_getattr'):
            pframe = inspect.currentframe().f_back
            print(f'__getattr__: {name} '
                  f'{pframe.f_code.co_filename}:{pframe.f_lineno} '
                  f'{pframe.f_code.co_name}')

        if self._is_refreshing is False:
            if self._needs_refresh():
                self._is_refreshing = True
                self.refresh()
                self._is_refreshing = False
            if self._needs_refresh():
                raise TPNLogicalError(
                    'refresh did not retrieve all required attributes')

        d = self.__dict__.get('data', [])
        if __flags__.get('debug_getattr'):
            print(f'd={d}')

        if name in d:
            if __flags__.get('debug_getattr'):
                print(f'{name}={d[name]}')
            return d[name]

        if __flags__.get('debug_getattr'):
            print(f'{name} not found')

        raise AttributeError(
            f'{object.__repr__(self)} has no such attribute "{name}"')

    def _needs_refresh(self) -> bool:
        if 'refresh_if_null' in self.__dict__:
            for key in self.__dict__['refresh_if_null']:
                if key not in self.__dict__.get('data', {}):
                    if __flags__.get('debug'):
                        print(f'{self.__class__.__name__} requires refresh '
                              f'due to missing {key}')
                    return True
        return False

    def refresh(self) -> None:
        self.get_data()

    def __repr__(self):
        display = ""
        if hasattr(self, 'parent'):
            display = self.parent.__repr__()
        if hasattr(self, 'display'):
            me = self.display()
            if display:
                display = f'{display} / {me}'
            else:
                display = me
        return display


class TPNListModel(TPNModel):
    def __init__(self, session):
        super().__init__(session)
        self.all = []

    def __contains__(self, term):
        for item in self.all:
            for key in self._refkeys:
                if term in item.__getattr__(key):
                    return True

    def __getitem__(self, term):
        for item in self.all:
            for key in self._refkeys:
                if term in item.__getattr__(key):
                    return item

    def __len__(self):
        return len(self.all)

    def __iter__(self):
        for i in self.all:
            yield i
