#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import pytest
from dlpx.virtualization.platform.exceptions import (
    MigrationIdAlreadyUsedError, MigrationIdIncorrectTypeError,
    MigrationIdIncorrectFormatError)
from dlpx.virtualization.platform import migration_id_set as m


class TestMigrationIdSet:
    @staticmethod
    @pytest.fixture
    def migration_set():
        yield m.MigrationIdSet()

    @staticmethod
    @pytest.mark.parametrize('migration_id,expected_std_id', [
        ('5.3.2.1', '5.3.2.1'),
        ('1000', '1000'),
        ('50.0.0', '50'),
        ('50.0.0000.1', '50.0.0.1'),
        ('2019.10.04', '2019.10.4')])
    def test_basic_add(migration_set, migration_id, expected_std_id):
        actual_std_id = migration_set.add(migration_id, 'function')

        assert actual_std_id == expected_std_id

    @staticmethod
    @pytest.mark.parametrize('id_one,id_two', [
        ('5.3.2.1', '5.3.2.1'),
        ('1000', '1000.0.0'),
        ('50.0.0', '50'),
        ('50.0.0000.1', '50.0.0.1.0000'),
        ('2019.0010.0004', '2019.10.4')])
    def test_same_migration_id_used(migration_set, id_one, id_two):
        std_id = migration_set.add(id_one, 'function')

        with pytest.raises(MigrationIdAlreadyUsedError) as err_info:
            migration_set.add(id_two, 'function2')

        message = err_info.value.message
        assert message == (
            "The migration id '{}' used in the function 'function2' has the"
            " same canonical form '{}' as another migration.".format(id_two,
                                                                     std_id))

    @staticmethod
    @pytest.mark.parametrize('migration_id', [True,
                                              1000,
                                              {'random set'},
                                              ['random', 'list']])
    def test_migration_incorrect_type(migration_set, migration_id):
        with pytest.raises(MigrationIdIncorrectTypeError) as err_info:
            migration_set.add(migration_id, 'upgrade')

        message = err_info.value.message
        assert message == (
            "The migration id '{}' used in the function 'upgrade' should"
            " be a string.".format(migration_id))

    @staticmethod
    @pytest.mark.parametrize('migration_id', ['Not integers',
                                              '1000.',
                                              '2019 10 20'])
    def test_migration_incorrect_format(migration_set, migration_id):
        with pytest.raises(MigrationIdIncorrectFormatError) as err_info:
            migration_set.add(migration_id, 'upgrade')

        message = err_info.value.message
        assert message == (
            "The migration id '{}' used in the function 'upgrade' does not"
            " follow the correct format '{}'.".format(
                migration_id, m.MIGRATION_ID_REGEX.pattern))

    @staticmethod
    @pytest.mark.parametrize('migration_id', ['0.0',
                                              '0',
                                              '0.000.000.00.0'])
    def test_migration_id_is_zero(migration_set, migration_id):
        with pytest.raises(MigrationIdIncorrectFormatError) as err_info:
            migration_set.add(migration_id, 'upgrade')

        message = err_info.value.message
        assert message == (
            "The migration id '{}' used in the function 'upgrade' cannot be"
            " used because a 0 migration id is not allowed.".format(
                migration_id))

    @staticmethod
    def test_get_sorted_ids(migration_set):
        migration_set.add('2019.04.01', 'one')
        migration_set.add('4.10.04', 'two')
        migration_set.add('20190.10.006', 'three')
        migration_set.add('1.2.3.4', 'four')
        migration_set.add('5.4.3.2.1.0', 'five')
        migration_set.add('1', 'six')
        migration_set.add('10.01.10.00.1.0.0', 'seven')

        assert migration_set.get_sorted_ids() == ['1',
                                                  '1.2.3.4',
                                                  '4.10.4',
                                                  '5.4.3.2.1',
                                                  '10.1.10.0.1',
                                                  '2019.4.1',
                                                  '20190.10.6']
