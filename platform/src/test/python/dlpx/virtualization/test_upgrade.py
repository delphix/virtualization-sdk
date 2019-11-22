#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import pytest
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
