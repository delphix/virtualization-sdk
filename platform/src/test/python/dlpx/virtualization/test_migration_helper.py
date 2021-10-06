from __future__ import absolute_import
#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import pytest
from . import conftest
from dlpx.virtualization.platform import migration_helper as m
from dlpx.virtualization.platform.exceptions import (
    MigrationIdAlreadyUsedError, MigrationIdIncorrectFormatError,
    MigrationIdIncorrectTypeError)


class TestPlatformUpgradeMigrations:
    @staticmethod
    @pytest.fixture
    def platform_migrations():
        yield m.PlatformUpgradeMigrations()

    @staticmethod
    @pytest.mark.parametrize('object_op', conftest.OBJECT_TYPES)
    @pytest.mark.parametrize('migration_id,expected_std_id',
                             [('5.3.2.1', '5.3.2.1'), ('1000', '1000'),
                              ('50.0.0', '50'), ('50.0.0000.1', '50.0.0.1'),
                              ('2019.10.04', '2019.10.4')])
    def test_basic_add(platform_migrations, method_name, migration_id,
                       expected_std_id):
        def function():
            pass

        # Add the migration id using the specific method passed in.
        getattr(platform_migrations, method_name)(migration_id, function)
        assert len(platform_migrations.get_sorted_ids()) == 1
        assert expected_std_id in platform_migrations.get_sorted_ids()

    @staticmethod
    @pytest.mark.parametrize('object_op', conftest.OBJECT_TYPES)
    @pytest.mark.parametrize('id_one,id_two',
                             [('5.3.2.1', '5.3.2.1'), ('1000', '1000.0.0'),
                              ('50.0.0', '50'),
                              ('50.0.0000.1', '50.0.0.1.0000'),
                              ('2019.0010.0004', '2019.10.4')])
    def test_same_migration_id_used(platform_migrations, method_name, id_one,
                                    id_two):
        def function():
            pass

        def function_two():
            pass

        # Add the id into the correct dict/set first.
        getattr(platform_migrations, method_name)(id_one, function)

        assert len(platform_migrations.get_sorted_ids()) == 1
        std_id = platform_migrations.get_sorted_ids()[0]

        with pytest.raises(MigrationIdAlreadyUsedError) as err_info:
            getattr(platform_migrations, method_name)(id_two, function_two)

        message = err_info.value.message
        assert message == (
            "The migration id '{}' used in the function 'function_two' has the"
            " same canonical form '{}' as another migration.".format(
                id_two, std_id))

    @staticmethod
    @pytest.mark.parametrize('object_op', conftest.OBJECT_TYPES)
    @pytest.mark.parametrize('migration_id',
                             [True, 1000, {'random set'}, ['random', 'list']])
    def test_migration_incorrect_type(platform_migrations, method_name,
                                      migration_id):
        def upgrade():
            pass

        with pytest.raises(MigrationIdIncorrectTypeError) as err_info:
            getattr(platform_migrations, method_name)(migration_id, upgrade)

        message = err_info.value.message
        assert message == (
            "The migration id '{}' used in the function 'upgrade' should"
            " be a string.".format(migration_id))

    @staticmethod
    @pytest.mark.parametrize('method_name', [
        'add_repository', 'add_source_config', 'add_linked_source',
        'add_virtual_source', 'add_snapshot'
    ])
    @pytest.mark.parametrize('migration_id',
                             ['Not integers', '1000.', '2019 10 20'])
    def test_migration_incorrect_format(platform_migrations, method_name,
                                        migration_id):
        def upgrade():
            pass

        with pytest.raises(MigrationIdIncorrectFormatError) as err_info:
            getattr(platform_migrations, method_name)(migration_id, upgrade)

        message = err_info.value.message
        assert message == (
            "The migration id '{}' used in the function 'upgrade' does not"
            " follow the correct format '{}'.".format(
                migration_id,
                m.PlatformUpgradeMigrations.MIGRATION_ID_REGEX.pattern))

    @staticmethod
    @pytest.mark.parametrize('object_op', conftest.OBJECT_TYPES)
    @pytest.mark.parametrize('migration_id', ['0.0', '0', '0.000.000.00.0'])
    def test_migration_id_is_zero(platform_migrations, method_name,
                                  migration_id):
        def upgrade():
            pass

        with pytest.raises(MigrationIdIncorrectFormatError) as err_info:
            getattr(platform_migrations, method_name)(migration_id, upgrade)

        message = err_info.value.message
        assert message == (
            "The migration id '{}' used in the function 'upgrade' cannot be"
            " used because a 0 migration id is not allowed.".format(
                migration_id))

    @staticmethod
    def test_get_sorted_ids(platform_migrations):
        def function():
            pass

        platform_migrations.add_repository('2019.04.01', function)
        platform_migrations.add_virtual_source('4.10.04', function)
        platform_migrations.add_linked_source('20190.10.006', function)
        platform_migrations.add_snapshot('1.2.3.4', function)
        platform_migrations.add_source_config('5.4.3.2.1.0', function)
        platform_migrations.add_linked_source('1', function)
        platform_migrations.add_snapshot('10.01.10.00.1.0.0', function)

        assert platform_migrations.get_sorted_ids() == [
            '1', '1.2.3.4', '4.10.4', '5.4.3.2.1', '10.1.10.0.1', '2019.4.1',
            '20190.10.6'
        ]


class TestLuaUpgradeMigrations:
    @staticmethod
    @pytest.fixture
    def lua_migrations():
        yield m.LuaUpgradeMigrations()

    @staticmethod
    @pytest.mark.parametrize('object_op', conftest.OBJECT_TYPES)
    def test_basic_add(lua_migrations, object_op):
        migration_id_list = ['0.0', '00.30', '1.00', '1.04', '2.5', '5.50']
        expected = ['0.0', '0.30', '1.0', '1.4', '2.5', '5.50']

        def function():
            pass

        # Add all the migration ids using the specific method passed in.
        for migration_id in migration_id_list:
            getattr(lua_migrations, 'add_{}'.format(object_op))(migration_id,
                                                                function)

        impl_dict = getattr(lua_migrations, 'get_{}_dict'.format(object_op))()
        assert len(impl_dict) == 6
        assert all(migration_id in impl_dict for migration_id in expected)

    @staticmethod
    @pytest.mark.parametrize('object_op', conftest.OBJECT_TYPES)
    def test_same_migration_id_used(lua_migrations, object_op):
        def function():
            pass

        def function_two():
            pass

        # Add the id into the correct dict/set first.
        getattr(lua_migrations, 'add_{}'.format(object_op))('5.3', function)

        with pytest.raises(MigrationIdAlreadyUsedError) as err_info:
            getattr(lua_migrations, 'add_{}'.format(object_op))('5.3',
                                                                function_two)

        message = err_info.value.message
        assert message == (
            "The lua major minor version '5.3' used in the function "
            "'function_two' decorated by 'upgrade.{}()' has "
            "already been used.".format(object_op))

    @staticmethod
    @pytest.mark.parametrize('method_name', [
        'add_repository', 'add_source_config', 'add_linked_source',
        'add_virtual_source', 'add_snapshot'
    ])
    @pytest.mark.parametrize('migration_id',
                             [True, 1000, {'random set'}, ['random', 'list']])
    def test_migration_incorrect_type(lua_migrations, method_name,
                                      migration_id):
        def upgrade():
            pass

        with pytest.raises(MigrationIdIncorrectTypeError) as err_info:
            getattr(lua_migrations, method_name)(migration_id, upgrade)

        message = err_info.value.message
        assert message == (
            "The migration id '{}' used in the function 'upgrade' should"
            " be a string.".format(migration_id))

    @staticmethod
    @pytest.mark.parametrize('object_op', conftest.OBJECT_TYPES)
    @pytest.mark.parametrize(
        'migration_id', ['Not integers', '1000.', '2019 10 20', '5.4.testver'])
    def test_migration_incorrect_format(lua_migrations, method_name,
                                        migration_id):
        def upgrade():
            pass

        with pytest.raises(MigrationIdIncorrectFormatError) as err_info:
            getattr(lua_migrations, method_name)(migration_id, upgrade)

        message = err_info.value.message
        assert message == (
            "The migration id '{}' used in the function 'upgrade' does not"
            " follow the correct format '{}'.".format(
                migration_id,
                m.LuaUpgradeMigrations.LUA_VERSION_REGEX.pattern))

    @staticmethod
    @pytest.mark.parametrize('object_op', conftest.OBJECT_TYPES)
    def test_get_correct_impls(lua_migrations, method_name, get_impls_to_exec):
        def f_one():
            pass

        def f_two():
            pass

        def f_three():
            pass

        def f_four():
            pass

        # Add the id/function in a random order
        getattr(lua_migrations, method_name)('3.6', f_three)
        getattr(lua_migrations, method_name)('1.02', f_one)
        getattr(lua_migrations, method_name)('4.0', f_four)
        getattr(lua_migrations, method_name)('2.01', f_two)

        ordered_impl_list = getattr(lua_migrations, get_impls_to_exec)('2.1')

        assert ordered_impl_list == [f_two, f_three, f_four]

    @staticmethod
    @pytest.mark.parametrize('object_op', conftest.OBJECT_TYPES)
    def test_get_correct_impls_low_versions(lua_migrations, method_name,
                                            get_impls_to_exec):
        def f_one():
            pass

        def f_two():
            pass

        def f_three():
            pass

        def f_four():
            pass

        # Add the id/function in a random order
        getattr(lua_migrations, method_name)('3.6', f_three)
        getattr(lua_migrations, method_name)('1.02', f_one)
        getattr(lua_migrations, method_name)('4.0', f_four)
        getattr(lua_migrations, method_name)('2.01', f_two)

        ordered_impl_list = getattr(lua_migrations, get_impls_to_exec)('5.1')

        assert not ordered_impl_list

    @staticmethod
    @pytest.mark.parametrize('object_op', conftest.OBJECT_TYPES)
    def test_get_correct_impls_high_versions(lua_migrations, method_name,
                                             get_impls_to_exec):
        def f_one():
            pass

        def f_two():
            pass

        def f_three():
            pass

        def f_four():
            pass

        # Add the id/function in a random order
        getattr(lua_migrations, method_name)('3.6', f_three)
        getattr(lua_migrations, method_name)('1.02', f_one)
        getattr(lua_migrations, method_name)('4.0', f_four)
        getattr(lua_migrations, method_name)('2.01', f_two)

        ordered_impl_list = getattr(lua_migrations, get_impls_to_exec)('0.0')

        assert ordered_impl_list == [f_one, f_two, f_three, f_four]

    @staticmethod
    @pytest.mark.parametrize('object_op', conftest.OBJECT_TYPES)
    def test_get_correct_impls_version_missing(lua_migrations, method_name,
                                               get_impls_to_exec):
        def f_one():
            pass

        def f_two():
            pass

        def f_three():
            pass

        def f_four():
            pass

        # Add the id/function in a random order
        getattr(lua_migrations, method_name)('3.6', f_three)
        getattr(lua_migrations, method_name)('1.02', f_one)
        getattr(lua_migrations, method_name)('4.0', f_four)
        getattr(lua_migrations, method_name)('2.01', f_two)

        ordered_impl_list = getattr(lua_migrations, get_impls_to_exec)('2.9')

        assert ordered_impl_list == [f_three, f_four]
