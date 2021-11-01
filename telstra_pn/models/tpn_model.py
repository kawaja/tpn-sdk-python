from typing import Any, Union
import inspect
from telstra_pn import __flags__
from telstra_pn.exceptions import (TPNDataError, TPNLogicalError,
                                   TPNLibraryInternalError)


class TPNModel:
    '''
    `TPNModel` represents the generic elements of a TPN object.

    Implementations of `TPNModel` must:
    - include a call to `super().__init__(session)` in `__init__`.

    Implementations of `TPNModel` may:
    - include an implementation of `display()` which returns
      a string with a human-readable representation of the
      object.
    - include an implementation of `_update_data()` which
      sets appropriate instance attributes based on the
      data retrieved from `_get_data()` (and/or passed via
      the initialiser).
    - specify a list of key names in `refresh_if_null` which,
      if any are missing when accessing any attributes, will trigger
      a data refresh via the appropriate TPN API.
    - specify a list of (alias, apiname) tuples in `_keyname_mappings`
      which will be copied as primary attributes when using the built-in
      `_update_data()` function, or if the class provides its own
      `_update_data()`, when it uses the `_update_keys()` function in
      its implementation. Note: if a key alias is specified in the
      `_keyname_mappings` list and the `refresh_if_null`
      list, then it will no longer trigger a refresh if it's null .
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
      `_handle_tpn_data_error()` should either return an alternative
      response payload, or re-raise TPNDataError.

    Public methods:
    - `refresh()` manually triggers a refresh of this object's data
      via the TPN API (if `_get_data()` is implemented).

    Raises:
    - `TPNLogicalError` when accessing attributes if the API refresh
      does not provide data for any keys in `refresh_if_null`.
    - `TPNLibraryInternalError` when accessing attributes if the
      `__init__()` does not call `super().__init__(session)`.
    '''

    data = {}
    _is_refreshing = False
    _url_path = None
    _get_deref = None
    table_names = [('UUID', 'id')]
    display_keys = ['id']
    type_name = 'item'

    def __init__(self, session):
        self._initialised = True
        self.session = session
        self.debug = __flags__.get('debug')

        if self.debug:
            print(f'creating {self.__class__.__name__}')

    def _get_data(self, *args, **kwargs) -> Union[list, dict]:
        if self.__dict__.get('api_session'):
            session = self.api_session
        else:
            session = self.session.api_session
        try:
            response = session.call_api(path=self._url_path)
        except TPNDataError as exc:
            response = self._handle_tpn_data_error(exc)

        if self.debug:
            print(f'{self.__class__.__name__}.'
                  f'get_data.response: {response}')

        if self._get_deref is None:
            return response
        else:
            return self._deref(response)

    def _deref(self, data) -> dict:
        return data.get(self._get_deref, {})

    def _handle_tpn_data_error(self, exc):
        if exc.status_code == 400:
            return {}
        raise(exc) from None

    def _update_data(self, data: dict) -> None:
        self._update_keys(data)

    def _update_keys(self, data) -> None:
        for (key, value) in self.__dict__.get('_keyname_mappings', {}).items():
            self.__dict__[key] = data.get(value)

    def __getitem__(self, name: str) -> Any:
        return getattr(self, name)

    def get(self, name: str, default: str = None) -> Any:
        if hasattr(self, name):
            return getattr(self, name)
        else:
            return default

    # def _check_method_overridden(self, attr) -> bool:
    #     myattr = self.__dict__.get(attr, None)
    #     classattr = TPNModel.__dict__.get(attr, None)
    #     if myattr is not None and classattr is not None:
    #         return myattr.__code__ is not classattr.__code__
    #     return False

    def __getattr__(self, name: str) -> Any:
        if name[0] == '_':
            raise AttributeError(
                f'{self.__class__.__name__} has no such attribute "{name}"'
            ) from None

        if self.__dict__.get('_initialised') is None:
            raise TPNLibraryInternalError(
                f'{self.__class__} does not call "super().__init__(session)" '
                'in "__init__()"'
            ) from None
        if __flags__.get('debug_getattr'):
            pframe = inspect.currentframe().f_back
            print(f'__getattr__ {self.__class__.__name__}: {name} '
                  f'{pframe.f_code.co_filename}:{pframe.f_lineno} '
                  f'{pframe.f_code.co_name}')

        if self._is_refreshing is False:
            if self._needs_refresh():
                self.refresh()
                if self._needs_refresh():
                    raise TPNLogicalError(
                        f'refresh for {self.__class__.__name__} '
                        'did not retrieve all required attributes') from None

        if name in self.__dict__:
            return self.__dict__[name]

        d = self.__dict__.get('data', [])
        if name in d:
            return d[name]

        d = self.__dict__.get('_defaults', {})
        if name in d:
            return d[name]

        raise AttributeError(
            f'{self.__class__.__name__} has no such attribute "{name}"'
        ) from None

    def _needs_refresh(self) -> bool:
        if 'refresh_if_null' in self.__dict__:
            for key in self.__dict__['refresh_if_null']:
                if (key not in self.__dict__
                        and key not in self.__dict__.get('data', [])):
                    if __flags__.get('debug'):
                        print(f'{self.__class__.__name__} requires refresh '
                              f'due to missing {key}')
                    return True
        return False

    def refresh(self) -> None:
        '''
        `refresh()` - force a refresh of the data via appropriate API endpoint
        '''
        if self._url_path is not None:
            self._is_refreshing = True
            response = self._get_data()
            self._update_data(response)
            self._is_refreshing = False
        else:
            self._update_data(self.data)

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
                ) from None
        else:
            raise TPNLibraryInternalError(
                f'{self.__class__} has not implemented '
                'required attribute "_primary_key"'
            ) from None

    def _deref(self, data) -> list:
        return data.get(self._get_deref, [])

    def __contains__(self, term):
        if self._get_contains(term) is None:
            return False
        return True

    def __getitem__(self, term):
        return self._get_contains(term)

    # use __dict__ to avoid hitting the TPNModel __getattr__
    def _get_contains(self, term):
        if '_refkeys' not in self.__dict__:
            return None
        for itemuuid in self.all.keys():
            item = self.all[itemuuid]
            for key in self._refkeys:
                keyfound = False
                if key in item.__dict__:
                    keyfound = True
                    if str(term) == str(item.__dict__[key]):
                        return item
                if key in item.__dict__['data']:
                    keyfound = True
                    if str(term) == str(item.__dict__['data'][key]):
                        return item
                if not keyfound:
                    raise ValueError(
                        f'refkey {key} missing from {object.__repr__(item)}')
        return None

    def __len__(self):
        return len(self.all)

    def __iter__(self):
        for i in self.all:
            yield self.all[i]

    def _extend_data(self, data: list, cls: object) -> list:
        if self.__dict__.get('api_session'):
            session = self.api_session
        else:
            session = self.session.api_session

        urls = [{'path': cls.get_url_path(item)} for item in data]
        return session.call_apis(urls)


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
        # check each subclass to see if one (and only one) claims
        # to be the correct handler for this particular instance
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

        if potential_subclasses == []:
            potential_subclasses.append(cls)
        if len(potential_subclasses) != 1:
            if __flags__.get('debug'):
                print(f'{cls.__class__.__name__}')
            raise TPNLibraryInternalError(
                f'Could not determine unique {cls.__class__.__name__} type '
                f'(found {len(potential_subclasses)} potentials)')

        # Create the instance of the (single) appropriate subclass.
        # Using object.__new__ (the original implementation of __new__
        # is important to avoid creating an infinite recursion on __new__
        newobj = object.__new__(potential_subclasses[0])
        newobj.data = data

        return newobj
