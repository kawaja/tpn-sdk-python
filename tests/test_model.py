from unittest.mock import MagicMock
import unittest

from telstra_pn.models import tpn_model
import telstra_pn
import telstra_pn.exceptions


class TestModelBasics(unittest.TestCase):
    def setUp(self):
        telstra_pn.__flags__['debug'] = True
        telstra_pn.__flags__['debug_getattr'] = True

    # No longer a fatal error to omit _get_data()
    # def test_model_refresh_with_no_get_data(self):
    #     class Model(tpn_model.TPNModel):
    #         def _update_data(self, data):
    #             pass

    #     m = Model(MagicMock())
    #     m.refresh()
    #     self.assertFalse(m._check_method_overridden('_get_data'))

    # No longer a fatal error to omit _update_data()
    # def test_model_missing_update_data(self):
    #     class Model(tpn_model.TPNModel):
    #         def _get_data(self):
    #             pass

    #     m = Model(MagicMock())
    #     with self.assertRaisesRegex(NotImplementedError, ''):
    #         m._update_data(MagicMock())
    #     self.assertTrue(m._check_method_overridden('_get_data'))

    def test_model_create(self):
        class Model(tpn_model.TPNModel):
            def _get_data(self):
                pass

            def _update_data(self, data):
                pass

        session_mock = MagicMock()
        m = Model(session_mock)
        self.assertEqual(m.session, session_mock)
        self.assertEqual(m.data, {})
        self.assertEqual(m._is_refreshing, False)

    def test_model_create_with_missing_super(self):
        class Model(tpn_model.TPNModel):
            def __init__(self, parent, **data):
                pass

            def _get_data(self):
                pass

            def _update_data(self, data):
                pass

        with self.assertRaises(telstra_pn.exceptions.TPNLibraryInternalError):
            session_mock = MagicMock()
            m = Model(session_mock)
            m.look_at_any_attribute

    def test_model_create_with_data(self):
        session_mock = MagicMock()

        class Model(tpn_model.TPNModel):
            def __init__(self, parent, **data):
                super().__init__(session_mock)
                self._update_data({'key1': 'data1', 'key2': 'data2'})

            def _get_data(self) -> dict:
                pass

            def _update_data(self, data):
                self.data = data

        m = Model(session_mock)
        self.assertEqual(m.session, session_mock)
        self.assertEqual(m.data, {'key1': 'data1', 'key2': 'data2'}, m.data)

    def test_model_create_with_refresh(self):
        session_mock = MagicMock()

        class Model(tpn_model.TPNModel):
            def __init__(self, parent, **data):
                super().__init__(session_mock)
                self._url_path = 'none'
                self.refresh()

            def _get_data(self) -> dict:
                return {'key1': 'data1', 'key2': 'data2'}

            def _update_data(self, data):
                self.data = data

        m = Model(session_mock)
        self.assertEqual(m.session, session_mock)
        self.assertEqual(m.data, {'key1': 'data1', 'key2': 'data2'}, m.data)


class TestListModelBasics(unittest.TestCase):
    def setUp(self):
        telstra_pn.__flags__['debug'] = True
        telstra_pn.__flags__['debug_getattr'] = True

    # No longer a fatal error to omit _update_data()
    # def test_list_model_missing_update_data(self):
    #     with self.assertRaisesRegex(NotImplementedError, ''):
    #         class ListModel(tpn_model.TPNListModel):
    #             def _get_data(self):
    #                 pass

    #         ListModel(MagicMock())._update_data(MagicMock())

    def test_list_model_missing_primary_key(self):
        class ListModel(tpn_model.TPNListModel):
            def _get_data(self):
                pass

            def _update_data(self, data):
                pass

        with self.assertRaisesRegex(
                telstra_pn.exceptions.TPNLibraryInternalError,
                'has not implemented required attribute "_primary_key"'):
            ListModel(MagicMock()).additem(1)

    def test_list_model_create(self):
        class ListModel(tpn_model.TPNListModel):
            def _get_data(self):
                pass

            def _update_data(self, data):
                pass

        session_mock = MagicMock()
        m = ListModel(session_mock)
        self.assertEqual(m.session, session_mock)
        self.assertEqual(m.data, {})
        self.assertEqual(m.all, {})
        self.assertEqual(m._is_refreshing, False)

    def test_list_model_create_with_missing_super(self):
        class ListModel(tpn_model.TPNListModel):
            def __init__(self, parent, **data):
                pass

            def _get_data(self):
                pass

            def _update_data(self, data):
                pass

        with self.assertRaises(telstra_pn.exceptions.TPNLibraryInternalError):
            session_mock = MagicMock()
            m = ListModel(session_mock)
            m.look_at_any_attribute

    def test_list_model_create_with_refresh(self):
        session_mock = MagicMock()

        class Model(tpn_model.TPNModel):
            def __init__(self, session, **data):
                super().__init__(session)
                self._update_data(data)

            def _update_data(self, data):
                self.data = data

            def display(self):
                return 'child'

        class ListModel(tpn_model.TPNListModel):
            def __init__(self, session):
                super().__init__(session)
                self._primary_key = 'key1'
                self._refkeys = ['key1']
                self._url_path = 'none'
                self.refresh()

            def _get_data(self) -> list:
                return [{'key1': 'data1', 'key2': 'data2'}]

            def _update_data(self, data):
                self.data = {**self.data, 'list': data}

                for item in data:
                    self.additem(Model(self, **item))

        ml = ListModel(session_mock)
        self.assertEqual(ml.session, session_mock)
        self.assertEqual(len(ml), 1)
        self.assertEqual(len(ml.all), 1)
        self.assertEqual(ml['data1'].key1, 'data1', ml.all)
        self.assertEqual(ml['data1'].key2, 'data2', ml.all)


class TestModelBehaviour(unittest.TestCase):
    getdata_mock = MagicMock()

    def setUp(self):
        telstra_pn.__flags__['debug'] = True
        telstra_pn.__flags__['debug_getattr'] = True

        session_mock = MagicMock()
        TestModelBehaviour.getdata_mock.reset_mock()
        TestModelBehaviour.getdata_mock.return_value = {
            'key1': 'data1',
            'key2': 'data2'
        }

        class Model(tpn_model.TPNModel):
            def __init__(self, parent, **data):
                super().__init__(session_mock)
                self._url_path = 'none'
                self.refresh()

            def _update_data(self, data: dict):
                self.data = data
                self._update_keys(data)

            def _get_data(self) -> dict:
                return {**TestModelBehaviour.getdata_mock()}

            def display(self):
                return 'child'

        self.m = Model(session_mock)
        return super().setUp()

    def test_model_gettattr_exists(self):
        self.assertEqual(self.m.key1, 'data1')

    def test_model_refresh_changed_attributes(self):
        self.assertEqual(self.m.key1, 'data1')
        self.assertEqual(len(self.m.data), 2)
        self.assertEqual(TestModelBehaviour.getdata_mock.call_count, 1)
        TestModelBehaviour.getdata_mock.return_value = {
            'key1': 'data+1',
            'key2': 'data+2',
            'key3': 'data+3'
        }
        self.m.refresh()
        self.assertEqual(TestModelBehaviour.getdata_mock.call_count, 2)
        self.assertEqual(self.m.key1, 'data+1')
        self.assertEqual(self.m.key2, 'data+2')
        self.assertEqual(self.m.key3, 'data+3')
        self.assertEqual(len(self.m.data), 3)

    def test_model_force_refresh_missing_attribute(self):
        self.m.refresh_if_null = ['key3']
        with self.assertRaises(telstra_pn.exceptions.TPNLogicalError):
            self.m.missing_attribute

    def test_model_force_refresh_changed_attributes(self):
        self.assertEqual(self.m.key1, 'data1')
        self.assertEqual(len(self.m.data), 2)
        self.assertEqual(TestModelBehaviour.getdata_mock.call_count, 1)
        TestModelBehaviour.getdata_mock.return_value = {
            'key1': 'data+1',
            'key2': 'data+2',
            'key3': 'data+3'
        }
        self.m.refresh_if_null = ['key3']
        self.assertEqual(self.m.key3, 'data+3')
        self.assertEqual(TestModelBehaviour.getdata_mock.call_count, 2)
        self.assertEqual(self.m.key1, 'data+1')
        self.assertEqual(self.m.key2, 'data+2')
        self.assertEqual(len(self.m.data), 3)

    def test_repr_single(self):
        self.assertEqual(str(self.m), 'child')

    def test_repr_parent(self):
        session_mock = MagicMock()
        self.assertEqual(str(self.m), 'child')

        class ModelParent(tpn_model.TPNModel):
            def __init__(self, parent, **data):
                super().__init__(session_mock)
                self.refresh()

            def _get_data(self) -> dict:
                return TestModelBehaviour.getdata_mock()

            def _update_data(self, data):
                self.data = data

            def display(self):
                return 'parent'

        n = ModelParent(session_mock)
        self.m.parent = n

        self.assertEqual(str(n), 'parent')
        self.assertEqual(str(self.m), 'parent / child')


class TestListModelBehaviour(unittest.TestCase):
    getdata_mock = MagicMock()

    def setUp(self):
        telstra_pn.__flags__['debug'] = True
        telstra_pn.__flags__['debug_getattr'] = True

        session_mock = MagicMock()
        TestModelBehaviour.getdata_mock.reset_mock()
        TestModelBehaviour.getdata_mock.return_value = [{
            'key1': 'data1',
            'key2': 'data2'
        }]

        class Model(tpn_model.TPNModel):
            def __init__(self, parent, **data):
                super().__init__(session_mock)
                self._update_data(data)

            def _update_data(self, data):
                self.data = data
                self.extradata = 'extra'

            def display(self):
                return 'child'

        class ListModel(tpn_model.TPNListModel):
            def __init__(self, parent, **data):
                super().__init__(session_mock)
                self._primary_key = 'key1'
                self._refkeys = ['key1', 'key2']
                self._url_path = 'none'
                self.refresh()

            def _update_data(self, data):
                self.data = {**self.data, 'list': data}

                for item in data:
                    self.additem(Model(self, **item))

            def _get_data(self) -> dict:
                return TestModelBehaviour.getdata_mock()

            def display(self):
                return f'list of {len(self.all)} item(s)'

        self.ml = ListModel(session_mock)
        return super().setUp()

    def test_list_model_contains_exists(self):
        self.assertIn('data1', self.ml)
        self.assertIn('data2', self.ml)

    def test_list_model_contains_missing(self):
        self.assertNotIn('data3', self.ml)

    def test_list_model_get_exists(self):
        self.assertEqual(self.ml['data1'].key2, 'data2')
        self.assertEqual(self.ml['data2'].key1, 'data1')

    def test_list_model_get_missing(self):
        self.assertIsNone(self.ml['data3'])

    def test_reset(self):
        self.assertEqual(len(self.ml), 1)
        self.ml.reset()
        self.assertEqual(len(self.ml), 0)

    def test_list_model_create_with_missing_primary_key(self):
        TestModelBehaviour.getdata_mock.return_value = [{
            'key1': 'data1',
            'key2': 'data2'
        }, {
            'key2': 'data+2',
            'key3': 'data+3'
        }]
        with self.assertRaisesRegex(
                telstra_pn.exceptions.TPNLogicalError,
                'attempted to add item.*does not contain primary key'):
            self.ml.refresh()

    def test_list_model_lookup_with_missing_refkey_contains(self):
        TestModelBehaviour.getdata_mock.return_value = [{
            'key1': 'data1',
            'key2': 'data2'
        }, {
            'key1': 'data+1',
            'key2': 'data+2',
            'key3': 'data+3'
        }]
        self.ml.refresh()
        self.ml._refkeys = ['key3']
        with self.assertRaisesRegex(ValueError, 'refkey key3 missing'):
            'data+3' in self.ml

    def test_list_model_lookup_with_missing_refkey_get(self):
        TestModelBehaviour.getdata_mock.return_value = [{
            'key1': 'data1',
            'key2': 'data2'
        }, {
            'key1': 'data+1',
            'key2': 'data+2',
            'key3': 'data+3'
        }]
        self.ml.refresh()
        self.ml._refkeys = ['key3']
        with self.assertRaisesRegex(ValueError, 'refkey key3 missing'):
            self.ml['data+3']

    def test_list_model_lookup_attribute_missing_contains(self):
        self.ml._refkeys = ['nothere']
        with self.assertRaisesRegex(ValueError, 'refkey nothere missing'):
            'extra' in self.ml

    def test_list_model_lookup_attribute_missing_get(self):
        self.ml._refkeys = ['nothere']
        with self.assertRaisesRegex(ValueError, 'refkey nothere missing'):
            self.ml['extra']

    def test_list_model_lookup_attribute_exists_contains(self):
        self.ml._refkeys = ['extradata']
        self.assertIn('extra', self.ml)

    def test_list_model_lookup_attribute_exists_get(self):
        self.ml._refkeys = ['extradata']
        self.assertEqual(self.ml['extra'].key1, 'data1')

    def test_list_model_no_refkeys_contains(self):
        self.assertIn('data1', self.ml)
        del self.ml._refkeys
        self.assertNotIn('data1', self.ml)

    def test_list_model_no_refkeys_get(self):
        self.assertEquals(self.ml['data1'].key1, 'data1')
        del self.ml._refkeys
        self.assertIsNone(self.ml['data1'])

    def test_list_model_refresh_changed_attributes(self):
        self.assertIn('data1', self.ml)
        self.assertIn('data1', self.ml)
        self.assertNotIn('data+1', self.ml)
        self.assertNotIn('data+2', self.ml)
        self.assertNotIn('data+3', self.ml)
        self.assertEqual(len(self.ml), 1)
        self.assertEqual(TestModelBehaviour.getdata_mock.call_count, 1)
        TestModelBehaviour.getdata_mock.return_value = [{
            'key1': 'data1',
            'key2': 'data2'
        }, {
            'key1': 'data+1',
            'key2': 'data+2',
            'key3': 'data+3'
        }]
        self.ml.refresh()
        self.assertEqual(TestModelBehaviour.getdata_mock.call_count, 2)
        self.assertIn('data1', self.ml)
        self.assertIn('data1', self.ml)
        self.assertIn('data+1', self.ml)
        self.assertIn('data+2', self.ml)
        self.assertNotIn('data+3', self.ml)
        self.assertEqual(len(self.ml), 2)

    def test_list_iteration(self):
        self.assertEqual(TestModelBehaviour.getdata_mock.call_count, 1)
        TestModelBehaviour.getdata_mock.return_value = [{
            'key1': 'data1',
            'key2': 'data2'
        }, {
            'key1': 'data+1',
            'key2': 'data+2',
            'key3': 'data+3'
        }]
        self.ml.refresh()
        for item in self.ml:
            self.assertEqual(item.extradata, 'extra')

    def test_repr_single(self):
        self.assertEqual(str(self.ml), 'list of 1 item(s)')


class TestModelSubclassMixin(unittest.TestCase):
    def setUp(self):
        telstra_pn.__flags__['debug'] = True
        telstra_pn.__flags__['debug_getattr'] = True

    def test_mixin_create(self):
        class Model(tpn_model.TPNModel, tpn_model.TPNModelSubclassesMixin):
            def __init__(self, parent, **data):
                self.type = data['type']

            def _get_data(self):
                pass

            def _update_data(self, data):
                pass

        class Subclass1(Model):
            @staticmethod
            def _is_a(data, parent):
                return data['type'] == 'subclass1'

        class Subclass2(Model):
            @staticmethod
            def _is_a(data, parent):
                return data['type'] == 'subclass2'

        session_mock = MagicMock()
        m1 = Model(session_mock, type='subclass1')
        m2 = Model(session_mock, type='subclass2')
        self.assertIsInstance(m1, Subclass1, type(m1))
        self.assertIsInstance(m2, Subclass2, type(m2))

    def test_mixin_missing_is_a(self):
        class Model(tpn_model.TPNModel, tpn_model.TPNModelSubclassesMixin):
            def __init__(self, parent, **data):
                self.type = data['type']

            def _get_data(self):
                pass

            def _update_data(self, data):
                pass

        class Subclass1(Model):
            @staticmethod
            def _is_a(data, parent):
                return data['type'] == 'subclass1'

        class Subclass2(Model):
            pass

        session_mock = MagicMock()
        with self.assertRaisesRegex(
                telstra_pn.exceptions.TPNLibraryInternalError,
                'not implemented the required "_is_a.*" static method'):
            Model(session_mock, type='subclass1')

    def test_mixin_no_matching_subclasses(self):
        class Model(tpn_model.TPNModel, tpn_model.TPNModelSubclassesMixin):
            def __init__(self, parent, **data):
                self.type = data['type']

            def _get_data(self):
                pass

            def _update_data(self, data):
                pass

        class Subclass1(Model):
            @staticmethod
            def _is_a(data, parent):
                return data['type'] == parent.look_for_class

        class Subclass2(Model):
            @staticmethod
            def _is_a(data, parent):
                return data['type'] == parent.look_for_class

        session_mock = MagicMock(look_for_class='subclass1')
        m1 = Model(session_mock, type='subclass2')
        self.assertIsInstance(m1, Model, type(m1))

    def test_mixin_two_matching_subclasses(self):
        class Model(tpn_model.TPNModel, tpn_model.TPNModelSubclassesMixin):
            def __init__(self, parent, **data):
                self.type = data['type']

            def _get_data(self):
                pass

            def _update_data(self, data):
                pass

        class Subclass1(Model):
            @staticmethod
            def _is_a(data, parent):
                return data['type'] == parent.look_for_class

        class Subclass2(Model):
            @staticmethod
            def _is_a(data, parent):
                return data['type'] == parent.look_for_class

        session_mock = MagicMock(look_for_class='subclass1')
        with self.assertRaisesRegex(
                telstra_pn.exceptions.TPNLibraryInternalError,
                'Could not determine unique .* type .found 2 potentials.'):
            Model(session_mock, type='subclass1')
