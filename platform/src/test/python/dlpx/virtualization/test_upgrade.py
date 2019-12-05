#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import pytest
import logging
from dlpx.virtualization import platform_pb2
from dlpx.virtualization.platform.exceptions import (
    DecoratorNotFunctionError, MigrationIdAlreadyUsedError)
from dlpx.virtualization.platform.operation import Operation as Op


class TestUpgrade:
    @staticmethod
    @pytest.fixture
    def my_plugin():
        from dlpx.virtualization.platform import Plugin
        yield Plugin()

    @staticmethod
    def basic_upgrade_helper(decorator, id_to_impl, upgrade_operation):
        @decorator('2019.10.01')
        def repo_upgrade_one(input_dict):
            output_dict = {'in': input_dict['in'], 'out': 'first'}
            return output_dict

        @decorator('2019.10.02')
        def repo_upgrade_two(input_dict):
            output_dict = {'in': input_dict['in'], 'out': 'second'}
            return output_dict

        migration_one = id_to_impl['2019.10.1']
        migration_two = id_to_impl['2019.10.2']

        assert migration_one == repo_upgrade_one
        assert migration_two == repo_upgrade_two
        assert migration_one({'in':'in_one'}) == {'in': 'in_one',
                                                  'out': 'first'}
        assert migration_two({'in':'in_two'}) == {'in': 'in_two',
                                                  'out': 'second'}

        assert upgrade_operation.migration_id_list == ['2019.10.1',
                                                       '2019.10.2']

    @staticmethod
    def decorator_not_function_helper(decorator, op):

        with pytest.raises(DecoratorNotFunctionError) as err_info:
            @decorator('2019.10.03')
            class RandomClass(object):
                pass

        message = err_info.value.message
        assert message == ("The object '{}' decorated by '{}' is"
                           " not a function.".format('RandomClass',
                                                     op.value))

    @staticmethod
    def test_upgrade_repository(my_plugin):
        TestUpgrade.basic_upgrade_helper(
            my_plugin.upgrade.repository,
            my_plugin.upgrade.repository_id_to_impl,
            my_plugin.upgrade)

        TestUpgrade.decorator_not_function_helper(
            my_plugin.upgrade.repository, Op.UPGRADE_REPOSITORY)

    @staticmethod
    def test_upgrade_source_config(my_plugin):
        TestUpgrade.basic_upgrade_helper(
            my_plugin.upgrade.source_config,
            my_plugin.upgrade.source_config_id_to_impl,
            my_plugin.upgrade)

        TestUpgrade.decorator_not_function_helper(
            my_plugin.upgrade.source_config, Op.UPGRADE_SOURCE_CONFIG)

    @staticmethod
    def test_upgrade_linked_source(my_plugin):
        TestUpgrade.basic_upgrade_helper(
            my_plugin.upgrade.linked_source,
            my_plugin.upgrade.linked_source_id_to_impl,
            my_plugin.upgrade)

        TestUpgrade.decorator_not_function_helper(
            my_plugin.upgrade.linked_source, Op.UPGRADE_LINKED_SOURCE)

    @staticmethod
    def test_upgrade_virtual_source(my_plugin):
        TestUpgrade.basic_upgrade_helper(
            my_plugin.upgrade.virtual_source,
            my_plugin.upgrade.virtual_source_id_to_impl,
            my_plugin.upgrade)

        TestUpgrade.decorator_not_function_helper(
            my_plugin.upgrade.virtual_source, Op.UPGRADE_VIRTUAL_SOURCE)

    @staticmethod
    def test_upgrade_snapshot(my_plugin):
        TestUpgrade.basic_upgrade_helper(
            my_plugin.upgrade.snapshot,
            my_plugin.upgrade.snapshot_id_to_impl,
            my_plugin.upgrade)

        TestUpgrade.decorator_not_function_helper(
            my_plugin.upgrade.snapshot, Op.UPGRADE_SNAPSHOT)

    @staticmethod
    def test_upgrade_same_migration_id_used(my_plugin):
        @my_plugin.upgrade.repository('2019.10.01')
        def repo_upgrade_one():
            return 'repo_one'

        @my_plugin.upgrade.repository('2019.10.04')
        def repo_upgrade_two():
            return 'repo_two'

        @my_plugin.upgrade.repository('2019.10.006')
        def repo_upgrade_three():
            return 'repo_three'

        @my_plugin.upgrade.source_config('2019.10.02')
        def sc_upgrade_one():
            return 'sc_one'

        with pytest.raises(MigrationIdAlreadyUsedError) as err_info_one:
            @my_plugin.upgrade.source_config('2019.10.0004')
            def sc_upgrade_two():
                return 'sc_two'

        @my_plugin.upgrade.linked_source('2019.10.3.000.0')
        def ls_upgrade_one():
            return 'ls_one'

        with pytest.raises(MigrationIdAlreadyUsedError) as err_info_two:
            @my_plugin.upgrade.virtual_source('2019.10.03')
            def vs_upgrade_one():
                return 'vs_one'

        @my_plugin.upgrade.virtual_source('2019.10.05')
        def vs_upgrade_two():
            return 'vs_two'

        with pytest.raises(MigrationIdAlreadyUsedError) as err_info_three:
            @my_plugin.upgrade.snapshot('2019.010.001')
            def snap_upgrade_one():
                return 'snap_one'

        @my_plugin.upgrade.snapshot('2019.10.12')
        def snap_upgrade_two():
            return 'snap_two'

        assert my_plugin.upgrade.migration_id_list == ['2019.10.1',
                                                       '2019.10.2',
                                                       '2019.10.3',
                                                       '2019.10.4',
                                                       '2019.10.5',
                                                       '2019.10.6',
                                                       '2019.10.12']

        repo_one = my_plugin.upgrade.repository_id_to_impl['2019.10.1']
        repo_two = my_plugin.upgrade.repository_id_to_impl['2019.10.4']
        repo_three = my_plugin.upgrade.repository_id_to_impl['2019.10.6']
        assert repo_one == repo_upgrade_one
        assert repo_two == repo_upgrade_two
        assert repo_three == repo_upgrade_three

        sc_one = my_plugin.upgrade.source_config_id_to_impl['2019.10.2']
        assert sc_one == sc_upgrade_one

        ls_one = my_plugin.upgrade.linked_source_id_to_impl['2019.10.3']
        assert ls_one == ls_upgrade_one

        vs_two = my_plugin.upgrade.virtual_source_id_to_impl['2019.10.5']
        assert vs_two == vs_upgrade_two

        snap_two = my_plugin.upgrade.snapshot_id_to_impl['2019.10.12']
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
    @pytest.fixture
    def caplog(caplog):
        caplog.set_level(logging.DEBUG)
        return caplog

    @staticmethod
    @pytest.fixture
    def upgrade_request(fake_map_param, upgrade_type):
        return platform_pb2.UpgradeRequest(
            pre_upgrade_parameters=fake_map_param,
            type=upgrade_type,
            migration_ids=[]
        )

    @staticmethod
    @pytest.mark.parametrize('fake_map_param,upgrade_type',
                             [({
                                  'APPDATA_REPOSITORY-1': '{}',
                                  'APPDATA_REPOSITORY-2': '{}',
                                  'APPDATA_REPOSITORY-3': '{}'
                              }, platform_pb2.UpgradeRequest.REPOSITORY,
                             )])
    def test_repository(my_plugin, upgrade_request, fake_map_param, caplog):
        upgrade_response = my_plugin.upgrade._internal_repository(
            upgrade_request)

        # Check that the response's oneof is set to return_value and not error
        assert upgrade_response.WhichOneof('result') == 'return_value'
        assert (upgrade_response.return_value.post_upgrade_parameters
                == fake_map_param)
        assert (caplog.records[0].message ==
                'Upgrade repositories [APPDATA_REPOSITORY-1,'
                ' APPDATA_REPOSITORY-2, APPDATA_REPOSITORY-3]')

    @staticmethod
    @pytest.mark.parametrize('fake_map_param,upgrade_type',
                             [({
                                   'APPDATA_SOURCE_CONFIG-1': '{}',
                                   'APPDATA_SOURCE_CONFIG-2': '{}',
                                   'APPDATA_SOURCE_CONFIG-3': '{}',
                                   'APPDATA_SOURCE_CONFIG-4': '{}'
                               }, platform_pb2.UpgradeRequest.SOURCECONFIG,
                             )])
    def test_source_config(my_plugin, upgrade_request, fake_map_param, caplog):
        upgrade_response = my_plugin.upgrade._internal_source_config(
            upgrade_request)

        # Check that the response's oneof is set to return_value and not error
        assert upgrade_response.WhichOneof('result') == 'return_value'
        assert (upgrade_response.return_value.post_upgrade_parameters
                == fake_map_param)
        assert (caplog.records[0].message ==
                'Upgrade source configs [APPDATA_SOURCE_CONFIG-1,'
                ' APPDATA_SOURCE_CONFIG-2, APPDATA_SOURCE_CONFIG-3,'
                ' APPDATA_SOURCE_CONFIG-4]')

    @staticmethod
    @pytest.mark.parametrize('fake_map_param,upgrade_type',
                             [({
                                   'APPDATA_STAGED_SOURCE-1': '{}',
                                   'APPDATA_STAGED_SOURCE-2': '{}',
                                   'APPDATA_STAGED_SOURCE-3': '{}'
                               }, platform_pb2.UpgradeRequest.LINKEDSOURCE,
                             )])
    def test_linked_source(my_plugin, upgrade_request, fake_map_param, caplog):
        upgrade_response = my_plugin.upgrade._internal_linked_source(
            upgrade_request)

        # Check that the response's oneof is set to return_value and not error
        assert upgrade_response.WhichOneof('result') == 'return_value'
        assert (upgrade_response.return_value.post_upgrade_parameters
                == fake_map_param)
        assert (caplog.records[0].message ==
                'Upgrade linked sources [APPDATA_STAGED_SOURCE-1,'
                ' APPDATA_STAGED_SOURCE-2, APPDATA_STAGED_SOURCE-3]')

    @staticmethod
    @pytest.mark.parametrize('fake_map_param,upgrade_type',
                             [({
                                   'APPDATA_VIRTUAL_SOURCE-1': '{}',
                                   'APPDATA_VIRTUAL_SOURCE-2': '{}'
                               }, platform_pb2.UpgradeRequest.VIRTUALSOURCE,
                             )])
    def test_virtual_source(
        my_plugin, upgrade_request, fake_map_param, caplog):
        upgrade_response = my_plugin.upgrade._internal_virtual_source(
            upgrade_request)

        # Check that the response's oneof is set to return_value and not error
        assert upgrade_response.WhichOneof('result') == 'return_value'
        assert (upgrade_response.return_value.post_upgrade_parameters
                == fake_map_param)
        assert (caplog.records[0].message ==
                'Upgrade virtual sources [APPDATA_VIRTUAL_SOURCE-1,'
                ' APPDATA_VIRTUAL_SOURCE-2]')

    @staticmethod
    @pytest.mark.parametrize('fake_map_param,upgrade_type',
                             [({
                                   'APPDATA_SNAPSHOT-1': '{}'
                               }, platform_pb2.UpgradeRequest.SNAPSHOT,
                             )])
    def test_snapshot(my_plugin, upgrade_request, fake_map_param, caplog):
        upgrade_response = my_plugin.upgrade._internal_snapshot(
            upgrade_request)

        # Check that the response's oneof is set to return_value and not error
        assert upgrade_response.WhichOneof('result') == 'return_value'
        assert (upgrade_response.return_value.post_upgrade_parameters
                == fake_map_param)
        assert (caplog.records[0].message ==
                'Upgrade snapshots [APPDATA_SNAPSHOT-1]')
