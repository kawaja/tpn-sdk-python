from typing import Any, Union
import inspect
from telstra_pn import __flags__
from telstra_pn.exceptions import (TPNDataError, TPNLogicalError,
                                   TPNLibraryInternalError)


class TPNDataHandler:
    def __init__(self,
                 owner,
                 url_path,
                 get_deref,
                 tpn_data_error_handler=None):
        self.tpn_data_error_handler = (tpn_data_error_handler
                                       or self._handle_tpn_data_error)
        self.url_path = url_path
        self.owner = owner
        self.get_deref = get_deref

    def get_data(self) -> Union[list, dict]:
        if self.owner.__dict__.get('api_session'):
            session = self.owner.api_session
        else:
            session = self.owner.session.api_session
        try:
            response = session.call_api(path=self.url_path)
        except TPNDataError as exc:
            response = self.tpn_data_error_handler(exc)

        if self.owner.debug:
            print(f'{self.owner.__class__.__name__}.'
                  f'get_data.response: {response}')

        if self.get_deref is None:
            return response
        else:
            return self.owner._deref(response)


class TPNModel:
    '''
    `TPNModel` represents the generic elements of a TPN object.

    Implementations of `TPNModel` must:
    - include a call to `super().__init__(session)` in `__init__`.
    - include an implementation of `_update_data()` which
      sets appropriate instance attributes based on the
      data retrieved from `_get_data()` (and/oror passed via
      the initialiser).

    Implementations of `TPNModel` may:
    - include an implementation of `display()` which returns
      a string with a human-readable representation of the
      object.
    - specify a list of key names in `refresh_if_null` which,
      if any are missing when accessing any attributes, will trigger
      a data refresh via the appropriate TPN API.
    - specify a `_url_path` string via which content for this model
      should be retrieved. If no `_url_path` is provided, a
      `_get_data()` function may be provided instead.
    - include an implementation of `_get_data()` which calls
      the appropriate TPN API to retrieve data for this
      object. If no `_get_data()` method is provided, the data
      for this model can only be specified at creation time and the
      `refresh()` method will silently do nothing.
    - include an implementation of `_handle_tpn_data_error(self, exc)`
      which will be called if a TPNDataError exception is raised
      while retrieving data from the TPN API via `_get_data()`.

    Public methods:
    - `refresh()` manually triggers a refresh of this object's data
      via the TPN API (if `_get_data()` is implemented).

    Raises:
    - `TPNLogicalError` when accessing attributes if the API refresh
      does not provide data for any keys in `refresh_if_null`.
    - `TPNLibraryInternalError` when accessing attributes if the
      `__init__()` does not call `super().__init__(session)`.
    '''
    def __init__(self, session, data_handler=None):
        self._initialised = True
        self.session = session
        self.debug = __flags__.get('debug')
        self.data = {}
        self._is_refreshing = False
        self._url_path = None
        self._get_deref = None
        self.data_handler = data_handler

        if self.debug:
            print(f'creating {self.__class__.__name__}')

    def _get_data(self, *args, **kwargs) -> Union[list, dict]:
        # late binding of data_handler to ensure subclass has had
        # a chance to populate _url_path, etc.
        if self.data_handler is None:
            self.data_handler = TPNDataHandler(self, self._url_path,
                                               self._get_deref,
                                               self._handle_tpn_data_error)
        return self.data_handler.get_data(*args, **kwargs)

    def _deref(self, data) -> dict:
        return data.get(self._get_deref, {})

    def _handle_tpn_data_error(self, exc):
        raise(exc)

    def _update_data(self, data: dict) -> None:
        raise NotImplementedError

    # def _check_method_overridden(self, attr) -> bool:
    #     myattr = self.__dict__.get(attr, None)
    #     classattr = TPNModel.__dict__.get(attr, None)
    #     if myattr is not None and classattr is not None:
    #         return myattr.__code__ is not classattr.__code__
    #     return False

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
        # if self._check_method_overridden('_get_data'):
        if self._url_path is not None:
            response = self._get_data()
            self._update_data(response)

    def __repr__(self):
        display = ""
        if hasattr(self, 'parent'):
            display = self.parent.__repr__()
        if hasattr(self, 'display'):
            me = self.display()
        else:
            me = self.__dict__.get('id', self.__class__.__name__)
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
    - specify a `_url_path` string via which content for this model
      should be retrieved. If no `_url_path` is provided, a
      `_get_data()` function may be provided instead.
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
    - include an implementation of `_get_data()` which calls
      the appropriate TPN API to retrieve data for this
      object. If no `_get_data()` method is provided, the data
      for this model can only be specified at creation time and the
      `refresh()` method will silently do nothing.
    - include an implementation of `_handle_tpn_data_error(self, exc)`
      which will be called if a TPNDataError exception is raised
      while retrieving data from the TPN API via `_get_data()`.

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
        if self.__dict__.get('_primary_key', False):
            key = getattr(item, self._primary_key, False)
            if key is not False:
                self.all[key] = item
            else:
                raise TPNLogicalError(
                    f'attempted to add item {item.__dict__} (to '
                    f'{self.__class__}) which does not contain '
                    f'primary key {self._primary_key}'
                )
        else:
            raise TPNLibraryInternalError(
                f'{self.__class__} has not implemented '
                'required attribute "_primary_key"'
            )

    def _deref(self, data) -> list:
        return data.get(self._get_deref, [])

    def __contains__(self, term):
        return self._get_contains(term, 'contains')

    def __getitem__(self, term):
        return self._get_contains(term, 'get')

    # use __dict__ to avoid hitting the TPNModel __getattr__
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
            if subclass.__dict__.get('_is_a', False):
                if subclass._is_a(data, parent):
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
