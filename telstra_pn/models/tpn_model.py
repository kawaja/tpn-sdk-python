from typing import Any
import inspect
from telstra_pn import __flags__
from telstra_pn.exceptions import TPNLogicalError, TPNLibraryInternalError


class TPNModel:
    '''
    `TPNModel` represents the generic elements of a TPN object.

    Implementations of `TPNModel` must:
    - include a call to `super().__init__(session)` in `__init__`.
    - include an implementation of `_update_data()` which
      sets appropriate instance attributes based on the
      data retrieved from `_get_data()`.

    Implementations of `TPNModel` may:
    - include an implementation of `display()` which returns
      a string with a human-readable representation of the
      object.
    - specify a list of key names in `refresh_if_null` which,
      if any are missing when accessing any attributes, will trigger
      a data refresh via the appropriate TPN API.
    - include an implementation of `_get_data()` which calls
      the appropriate TPN API to retrieve data for this
      object. If no `_get_data()` method is provided, the data
      for this model can only be specified at creation time and the
      `refresh()` method will silently do nothing.

    Public methods:
    - `refresh()` manually triggers a refresh of this object's data
      via the TPN API (if `_get_data()` is implemented).

    Raises:
    - `TPNLogicalError` when accessing attributes if the API refresh
      does not provide data for any keys in `refresh_if_null`.
    - `TPNLibraryInternalError` when accessing attributes if the
      `__init__()` does not call `super().__init__(session)`.
    '''
    def __init__(self, session):
        self._initialised = True
        self.session = session
        self.debug = __flags__.get('debug')
        self.data = {}
        self._is_refreshing = False
        if self.debug:
            print(f'creating {self.__class__.__name__}')

    def _get_data(self) -> None:
        raise NotImplementedError

    def _update_data(self, data: dict) -> None:
        raise NotImplementedError

    def _check_method_overridden(self, attr) -> bool:
        return getattr(self, attr).__code__ is not getattr(TPNModel,
                                                           attr).__code__

    def __getattr__(self, name: str) -> Any:
        if self.__dict__.get('_initialised') is None:
            raise TPNLibraryInternalError(
                f'{self.__class__} does not call "super().__init__(session)" '
                'in "__init__()"'
            )
        if __flags__.get('debug_getattr'):
            pframe = inspect.currentframe().f_back
            print(f'__getattr__ {self.__class__}: {name} '
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
        if self._check_method_overridden('_get_data'):
            self._update_data(self._get_data())

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
    '''
    `TPNListModel` represents a list of TPN objects.

    Implementations of `TPNListModel` must:
    - include a call to `super().__init__(session)` in `__init__`.
    - include an implementation of `_update_data()` which sets
      appropriate instance attributes based on the data retrieved
      from `_get_data()`.
    - include an implementation of `_get_data()` which calls
      the appropriate TPN API to retrieve data for this
      object.
    - specify a primary key in `_primary_key`. This key must be
      present in the data returned by `_get_data()`.

    Implementations of `TPNListModel` may:
    - include an implementation of `display()` which returns
      a string with a human-readable representation of the
      object.
    - specify a list of key names in `refresh_if_null` which,
      if any are missing when accessing any attributes, will trigger
      a data refresh via the appropriate TPN API.
    - specify a list of key names in `_refkeys` which will enable
      `in` and `[]` indexing to refer to individual elements in the list.
      If `_refkeys` is specified in a way that might identify more than
      one object, `in` will work correctly, but `[]` indexing will
      return an arbitrary element. Every item in the list must contain
      every key in `_refkeys`. If the API does not always provide this,
      then the additional key should be set in `_update_data()`.

    Public methods:
    - `refresh()` manually triggers a refresh of this object's data
      via the TPN API.
    - `additem()` adds an item to the list.

    Behaviour:
    - when referenced by `[]` index lookup, uses all keys specified in
      `_refkeys` to find a single item. Note that if `_refkeys` is specified
      in a way that might identify more than one object, an arbitrary element
      will be returned. An example of this is when a customer-modifiable
      field such as `name` is used and the customer chooses the same name for
      two items.
    - `key in object` uses all keys specified in `_refkeys` to identify whether
      there is any object in the list matching the key.
    - iterating the object will return all items, even if there are duplicates
      according to the keys in `_refkeys`.

    Raises:
    - `TPNLogicalError` when accessing attributes if the API refresh
      does not provide data for any keys in `refresh_if_null`.
    - `TPNLibraryInternalError` in `additem()` if the `_primary_key` is
      not defined.
    - `ValueError` if any item is missing any key in `_refkeys`.
    '''
    def __init__(self, session):
        super().__init__(session)
        self.all = {}

    def reset(self):
        self.all = {}

    def additem(self, item) -> None:
        '''
        `additem()` adds the item (with data formatted appropriately for
        the member object type). `additem()` is intended to be used within
        the `_update_data()` method to populate the primary list of items
        within the list.

        Returns: None

        Raises:
        - `TPNLogicalError` if the `item` is missing the required
          `_primary_key`.
        - `TPNLibraryInternalError` if the class is missing the required
          `_primary_key` attribute.
        '''
        if getattr(self, '_primary_key', False):
            key = getattr(item, self._primary_key, False)
            if key is not False:
                self.all[key] = item
            else:
                raise TPNLogicalError(
                    f'attempted to add item {item} to {self.__class__} which '
                    f'does not contain primary key {self._primary_key}'
                )
        else:
            raise TPNLibraryInternalError(
                f'{self.__class__} has not implemented '
                'required attribute "_primary_key"'
            )

    # avoid hitting the TPNModel __getattr__
    def __contains__(self, term):
        return self._get_contains(term, 'contains')

    # avoid hitting the TPNModel __getattr__
    def __getitem__(self, term):
        return self._get_contains(term, 'get')

    def _get_contains(self, term, action):
        if '_refkeys' not in self.__dict__:
            if action == 'get':
                return None
            else:
                return False
        for itemuuid in self.all.keys():
            item = self.all[itemuuid]
            for key in self._refkeys:
                keyfound = False
                if key in item.__dict__:
                    keyfound = True
                    if str(term) == str(item.__dict__[key]):
                        if action == 'get':
                            return item
                        else:
                            return True
                if key in item.__dict__['data']:
                    keyfound = True
                    if str(term) == str(item.__dict__['data'][key]):
                        if action == 'get':
                            return item
                        else:
                            return True
                if not keyfound:
                    raise ValueError(
                        f'refkey {key} missing from {object.__repr__(item)}')
        if action == 'get':
            return None
        else:
            return False

    def __len__(self):
        return len(self.all)

    def __iter__(self):
        for i in self.all:
            yield self.all[i]


class TPNModelSubclassesMixin:
    '''
    `TPNModelSubclassesMixin` can be added as a parent class
    to generic classes inheriting from `TPNModel`. It enables returning
    a more specific subclass when creating the generic class, based
    on the results of calling the `_is_a()` static method on each subclass.

    Specific subclasses adding the `TPNModelSubclassesMixin` must:
    - implement a static method `_is_a()` which is provided
      data from the TPN API relating to the generic class and
      should return `True` when the specific subclass believes
      it is the appropriate subclass to represent the object.

    Raises:
    - `TPNLibraryInternalError` if more than one specific subclass
      accepts responsibility to represent the object, as there should
      only be a single specific subclass claiming the object.
    - `TPNLibraryInternalError` if the `_is_a()` static method is not
      implmented.
    '''
    def __new__(cls, parent, **data):
        potential_subclasses = []
        for subclass in cls.__subclasses__():
            if getattr(subclass, '_is_a', False):
                if subclass._is_a(parent, data):
                    potential_subclasses.append(subclass)
            else:
                raise TPNLibraryInternalError(
                    f'{subclass} has not implemented the required '
                    '"_is_a()" static method'
                )
        if len(potential_subclasses) != 1:
            raise TPNLibraryInternalError(
                f'Could not determine unique {cls} type '
                f'(found {len(potential_subclasses)} potentials)')
        # using object.__new__ is important to avoid creating an
        # infinite recursion on __new__
        return object.__new__(potential_subclasses[0])
