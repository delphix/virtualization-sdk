#
# Copyright (c) 2019, 2021 by Delphix. All rights reserved.
#

import copy
import json
import logging

import pytest
from dlpx.virtualization.api import platform_pb2
from dlpx.virtualization.platform import MigrationType
from dlpx.virtualization.platform.exceptions import (
    DecoratorNotFunctionError, MigrationIdAlreadyUsedError)
from dlpx.virtualization.platform.operation import Operation as Op


class TestUpgrade:
    @staticmethod
    @pytest.fixture
    def my_upgrade():
        from dlpx.virtualization.platform import Plugin
        yield Plugin().upgrade

    @staticmethod
    @pytest.fixture
    def caplog(caplog):
        caplog.set_level(logging.DEBUG)
        return caplog

    @staticmethod
    @pytest.fixture
    def upgrade_request(fake_map_param, upgrade_type, lua_version,
                        migration_ids):
        return platform_pb2.UpgradeRequest(
            pre_upgrade_parameters=fake_map_param,
            type=upgrade_type,
            lua_upgrade_version=lua_version,
            migration_ids=migration_ids)

    @staticmethod
    @pytest.fixture
    def lua_version():
        return None

    @staticmethod
    @pytest.fixture
    def migration_ids():
        return []

    @staticmethod
    def basic_upgrade_helper(decorator, dict_getter, my_upgrade):
        @decorator('2019.10.01')
        def repo_upgrade_one(input_dict):
            output_dict = {'in': input_dict['in'], 'out': 'first'}
            return output_dict

        @decorator('2019.10.02')
        def repo_upgrade_two(input_dict):
            output_dict = {'in': input_dict['in'], 'out': 'second'}
            return output_dict

        id_to_impl = dict_getter()
        migration_one = id_to_impl['2019.10.1']
        migration_two = id_to_impl['2019.10.2']

        assert migration_one == repo_upgrade_one
        assert migration_two == repo_upgrade_two
        assert migration_one({'in': 'in_one'}) == {
            'in': 'in_one',
            'out': 'first'
        }
        assert migration_two({'in': 'in_two'}) == {
            'in': 'in_two',
            'out': 'second'
        }

        assert my_upgrade.migration_id_list == ['2019.10.1', '2019.10.2']

    @staticmethod
    def decorator_not_function_helper(decorator, op):

        with pytest.raises(DecoratorNotFunctionError) as err_info:

            @decorator('2019.10.03')
            class RandomClass(object):
                pass

        message = err_info.value.message
        assert message == ("The object '{}' decorated by '{}' is"
                           " not a function.".format('RandomClass', op.value))

    @staticmethod
    def test_upgrade_repository(my_upgrade):
        TestUpgrade.basic_upgrade_helper(
            my_upgrade.repository,
            my_upgrade.platform_migrations.get_repository_dict, my_upgrade)

        TestUpgrade.decorator_not_function_helper(my_upgrade.repository,
                                                  Op.UPGRADE_REPOSITORY)

    @staticmethod
    def test_upgrade_source_config(my_upgrade):
        TestUpgrade.basic_upgrade_helper(
            my_upgrade.source_config,
            my_upgrade.platform_migrations.get_source_config_dict, my_upgrade)

        TestUpgrade.decorator_not_function_helper(my_upgrade.source_config,
                                                  Op.UPGRADE_SOURCE_CONFIG)

    @staticmethod
    def test_upgrade_linked_source(my_upgrade):
        TestUpgrade.basic_upgrade_helper(
            my_upgrade.linked_source,
            my_upgrade.platform_migrations.get_linked_source_dict, my_upgrade)

        TestUpgrade.decorator_not_function_helper(my_upgrade.linked_source,
                                                  Op.UPGRADE_LINKED_SOURCE)

    @staticmethod
    def test_upgrade_virtual_source(my_upgrade):
        TestUpgrade.basic_upgrade_helper(
            my_upgrade.virtual_source,
            my_upgrade.platform_migrations.get_virtual_source_dict, my_upgrade)

        TestUpgrade.decorator_not_function_helper(my_upgrade.virtual_source,
                                                  Op.UPGRADE_VIRTUAL_SOURCE)

    @staticmethod
    def test_upgrade_snapshot(my_upgrade):
        TestUpgrade.basic_upgrade_helper(
            my_upgrade.snapshot,
            my_upgrade.platform_migrations.get_snapshot_dict, my_upgrade)

        TestUpgrade.decorator_not_function_helper(my_upgrade.snapshot,
                                                  Op.UPGRADE_SNAPSHOT)

    @staticmethod
    def test_upgrade_same_migration_id_used(my_upgrade):
        @my_upgrade.repository('2019.10.01')
        def repo_upgrade_one():
            return 'repo_one'

        @my_upgrade.repository('2019.10.04')
        def repo_upgrade_two():
            return 'repo_two'

        @my_upgrade.repository('2019.10.006')
        def repo_upgrade_three():
            return 'repo_three'

        @my_upgrade.source_config('2019.10.02')
        def sc_upgrade_one():
            return 'sc_one'

        with pytest.raises(MigrationIdAlreadyUsedError) as err_info_one:

            @my_upgrade.source_config('2019.10.0004')
            def sc_upgrade_two():
                return 'sc_two'

        @my_upgrade.linked_source('2019.10.3.000.0')
        def ls_upgrade_one():
            return 'ls_one'

        with pytest.raises(MigrationIdAlreadyUsedError) as err_info_two:

            @my_upgrade.virtual_source('2019.10.03')
            def vs_upgrade_one():
                return 'vs_one'

        @my_upgrade.virtual_source('2019.10.05')
        def vs_upgrade_two():
            return 'vs_two'

        with pytest.raises(MigrationIdAlreadyUsedError) as err_info_three:

            @my_upgrade.snapshot('2019.010.001')
            def snap_upgrade_one():
                return 'snap_one'

        @my_upgrade.snapshot('2019.10.12')
        def snap_upgrade_two():
            return 'snap_two'

        assert my_upgrade.migration_id_list == [
            '2019.10.1', '2019.10.2', '2019.10.3', '2019.10.4', '2019.10.5',
            '2019.10.6', '2019.10.12'
        ]

        platform_migrations = my_upgrade.platform_migrations
        repo_one = platform_migrations.get_repository_dict()['2019.10.1']
        repo_two = platform_migrations.get_repository_dict()['2019.10.4']
        repo_three = platform_migrations.get_repository_dict()['2019.10.6']
        assert repo_one == repo_upgrade_one
        assert repo_two == repo_upgrade_two
        assert repo_three == repo_upgrade_three

        sc_one = platform_migrations.get_source_config_dict()['2019.10.2']
        assert sc_one == sc_upgrade_one

        ls_one = platform_migrations.get_linked_source_dict()['2019.10.3']
        assert ls_one == ls_upgrade_one

        vs_two = platform_migrations.get_virtual_source_dict()['2019.10.5']
        assert vs_two == vs_upgrade_two

        snap_two = platform_migrations.get_snapshot_dict()['2019.10.12']
        assert snap_two == snap_upgrade_two

        assert err_info_one.value.message == (
            "The migration id '2019.10.0004' used in the function"
            " 'sc_upgrade_two' has the same canonical form '2019.10.4'"
            " as another migration.")

        assert err_info_two.value.message == (
            "The migration id '2019.10.03' used in the function"
            " 'vs_upgrade_one' has the same canonical form '2019.10.3'"
            " as another migration.")

        assert err_info_three.value.message == (
            "The migration id '2019.010.001' used in the function"
            " 'snap_upgrade_one' has the same canonical form '2019.10.1'"
            " as another migration.")

    @staticmethod
    @pytest.mark.parametrize('fake_map_param,upgrade_type,object_op', [
        ({
            'APPDATA_REPOSITORY-1': '{"name": "repo", "migrations": []}'
        }, platform_pb2.UpgradeRequest.REPOSITORY, 'repository'),
        ({
            'APPDATA_SOURCE_CONFIG-1': '{"name": "sc", "migrations": []}'
        }, platform_pb2.UpgradeRequest.SOURCECONFIG, 'source_config'),
        ({
            'APPDATA_STAGED_SOURCE-1': '{"name": "ls", "migrations": []}'
        }, platform_pb2.UpgradeRequest.LINKEDSOURCE, 'linked_source'),
        ({
            'APPDATA_VIRTUAL_SOURCE-1': '{"name": "vs", "migrations": []}'
        }, platform_pb2.UpgradeRequest.VIRTUALSOURCE, 'virtual_source'),
        ({
            'APPDATA_SNAPSHOT-1': '{"name": "snap", "migrations": []}'
        }, platform_pb2.UpgradeRequest.SNAPSHOT, 'snapshot'),
    ])
    @pytest.mark.parametrize('lua_version,migration_ids', [(
        '1.2',
        ['2020.4.2', '2020.4.4'],
    )])
    def test_lua_upgrade(my_upgrade, upgrade_request, object_op,
                         get_impls_to_exec):
        upgrade_type_decorator = getattr(my_upgrade, object_op)

        @upgrade_type_decorator('1.1', MigrationType.LUA)
        def repo_upgrade_one(input_dict):
            output_dict = copy.deepcopy(input_dict)
            output_dict['migrations'].append('lua repo 1.1')
            return output_dict

        @upgrade_type_decorator('1.2', MigrationType.LUA)  # noqa F811
        def repo_upgrade_one(input_dict):  # noqa F811
            output_dict = copy.deepcopy(input_dict)
            output_dict['migrations'].append('lua repo 1.2')
            return output_dict

        @upgrade_type_decorator('2020.4.2')
        def repo_upgrade_two(input_dict):
            output_dict = copy.deepcopy(input_dict)
            output_dict['migrations'].append('platform repo 2020.4.2')
            return output_dict

        @upgrade_type_decorator('2020.4.3')  # noqa F811
        def repo_upgrade_two(input_dict):  # noqa F811
            output_dict = copy.deepcopy(input_dict)
            output_dict['migrations'].append('platform repo 2020.4.3')
            return output_dict

        @upgrade_type_decorator('2020.4.4')  # noqa F811
        def repo_upgrade_two(input_dict):  # noqa F811
            output_dict = copy.deepcopy(input_dict)
            output_dict['migrations'].append('platform repo 2020.4.4')
            return output_dict

        lua_getter = getattr(my_upgrade.lua_migrations, get_impls_to_exec)

        platform_getter = getattr(my_upgrade.platform_migrations,
                                  get_impls_to_exec)

        post_upgrade_parameters = my_upgrade._run_migration_upgrades(
            upgrade_request, lua_getter, platform_getter)

        expected = [
            "lua repo 1.2", "platform repo 2020.4.2", "platform repo 2020.4.4"
        ]
        for metadata in post_upgrade_parameters.values():
            current_metadata = json.loads(metadata)
            assert current_metadata['migrations'] == expected

    @staticmethod
    @pytest.mark.parametrize(
        'func_name,fake_map_param,upgrade_type,expected_logs',
        [('_internal_repository', {
            'APPDATA_REPOSITORY-1': '{}',
            'APPDATA_REPOSITORY-2': '{}',
            'APPDATA_REPOSITORY-3': '{}'
        }, platform_pb2.UpgradeRequest.REPOSITORY,
          'Upgrade repositories [APPDATA_REPOSITORY-1,'
          ' APPDATA_REPOSITORY-2, APPDATA_REPOSITORY-3]'),
         ('_internal_source_config', {
             'APPDATA_SOURCE_CONFIG-1': '{}',
             'APPDATA_SOURCE_CONFIG-2': '{}',
             'APPDATA_SOURCE_CONFIG-3': '{}',
             'APPDATA_SOURCE_CONFIG-4': '{}'
         }, platform_pb2.UpgradeRequest.SOURCECONFIG,
          'Upgrade source configs [APPDATA_SOURCE_CONFIG-1,'
          ' APPDATA_SOURCE_CONFIG-2, APPDATA_SOURCE_CONFIG-3,'
          ' APPDATA_SOURCE_CONFIG-4]'),
         ('_internal_linked_source', {
             'APPDATA_STAGED_SOURCE-1': '{}',
             'APPDATA_STAGED_SOURCE-2': '{}',
             'APPDATA_STAGED_SOURCE-3': '{}'
         }, platform_pb2.UpgradeRequest.LINKEDSOURCE,
          'Upgrade linked sources [APPDATA_STAGED_SOURCE-1,'
          ' APPDATA_STAGED_SOURCE-2, APPDATA_STAGED_SOURCE-3]'),
         ('_internal_virtual_source', {
             'APPDATA_VIRTUAL_SOURCE-1': '{}',
             'APPDATA_VIRTUAL_SOURCE-2': '{}'
         }, platform_pb2.UpgradeRequest.VIRTUALSOURCE,
          'Upgrade virtual sources [APPDATA_VIRTUAL_SOURCE-1,'
          ' APPDATA_VIRTUAL_SOURCE-2]'),
         ('_internal_snapshot', {
             'APPDATA_SNAPSHOT-1': '{}'
         }, platform_pb2.UpgradeRequest.SNAPSHOT,
          'Upgrade snapshots [APPDATA_SNAPSHOT-1]')])
    def test_upgrade_requests(my_upgrade, func_name, fake_map_param,
                              expected_logs, upgrade_request, caplog):
        upgrade_response = getattr(my_upgrade, func_name)(upgrade_request)

        # Check that the response's oneof is set to return_value and not error
        assert upgrade_response.WhichOneof('result') == 'return_value'
        assert (upgrade_response.return_value.post_upgrade_parameters ==
                fake_map_param)
        assert (caplog.records[0].message == expected_logs)
