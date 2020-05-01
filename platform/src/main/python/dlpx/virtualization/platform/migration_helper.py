#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import re

from dlpx.virtualization.platform import validation_util as v
from dlpx.virtualization.platform.exceptions import (
    MigrationIdAlreadyUsedError, MigrationIdIncorrectFormatError,
    MigrationIdIncorrectTypeError)
from dlpx.virtualization.platform.operation import Operation as Op


class UpgradeMigrations(object):
    def __init__(self):
        self._repository_id_to_impl = {}
        self._source_config_id_to_impl = {}
        self._linked_source_id_to_impl = {}
        self._virtual_source_id_to_impl = {}
        self._snapshot_id_to_impl = {}

    def add_repository(self, migration_id, repository_impl):
        self._repository_id_to_impl[migration_id] = v.check_function(
            repository_impl, Op.UPGRADE_REPOSITORY)

    def add_source_config(self, migration_id, source_config_impl):
        self._source_config_id_to_impl[migration_id] = v.check_function(
            source_config_impl, Op.UPGRADE_SOURCE_CONFIG)

    def add_linked_source(self, migration_id, linked_source_impl):
        self._linked_source_id_to_impl[migration_id] = v.check_function(
            linked_source_impl, Op.UPGRADE_LINKED_SOURCE)

    def add_virtual_source(self, migration_id, virtual_source_impl):
        self._virtual_source_id_to_impl[migration_id] = v.check_function(
            virtual_source_impl, Op.UPGRADE_VIRTUAL_SOURCE)

    def add_snapshot(self, migration_id, snapshot_impl):
        self._snapshot_id_to_impl[migration_id] = v.check_function(
            snapshot_impl, Op.UPGRADE_SNAPSHOT)

    def get_repository_dict(self):
        """dict: The migration id to implementation for repository migrations.
        """
        return self._repository_id_to_impl

    def get_source_config_dict(self):
        """dict: The migration id to implementation for source config
        migrations.
        """
        return self._source_config_id_to_impl

    def get_linked_source_dict(self):
        """dict: The migration id to implementation for linked source
        migrations.
        """
        return self._linked_source_id_to_impl

    def get_virtual_source_dict(self):
        """dict: The migration id to implementation for virtual source
        migrations.
        """
        return self._virtual_source_id_to_impl

    def get_snapshot_dict(self):
        """dict: The migration id to implementation for snapshot migrations.
        """
        return self._snapshot_id_to_impl


class PlatformUpgradeMigrations(UpgradeMigrations):
    """
    Keeps track of all migrations and validites/standardizes them as they are
    added / parsed.

    Exceptions can be thrown when trying to add a new migration id. Otherwise
    at the end of reading in all migration functions can be gotten in the
    correct order.
    """
    MIGRATION_ID_REGEX = re.compile(r'^\d+(\.\d+)*$')

    def __init__(self):
        """
        The list of migration ids will store migrations as an array of ids
        where the id is represented by the standardized array of positive
        integers. For example if there were these ids: 1.0.0, 1.2.03, and
        2.0.1.0, __migration_ids would be [ [1], [1, 2, 3], [2, 0, 1]]
        """
        self.__migration_ids = []
        super(PlatformUpgradeMigrations, self).__init__()

    def add_repository(self, migration_id, repository_impl):
        std_mig_id = self.__add(migration_id, repository_impl.__name__)
        super(PlatformUpgradeMigrations,
              self).add_repository(std_mig_id, repository_impl)

    def add_source_config(self, migration_id, source_config_impl):
        std_mig_id = self.__add(migration_id, source_config_impl.__name__)
        super(PlatformUpgradeMigrations,
              self).add_source_config(std_mig_id, source_config_impl)

    def add_linked_source(self, migration_id, linked_source_impl):
        std_mig_id = self.__add(migration_id, linked_source_impl.__name__)
        super(PlatformUpgradeMigrations,
              self).add_linked_source(std_mig_id, linked_source_impl)

    def add_virtual_source(self, migration_id, virtual_source_impl):
        std_mig_id = self.__add(migration_id, virtual_source_impl.__name__)
        super(PlatformUpgradeMigrations,
              self).add_virtual_source(std_mig_id, virtual_source_impl)

    def add_snapshot(self, migration_id, snapshot_impl):
        std_mig_id = self.__add(migration_id, snapshot_impl.__name__)
        super(PlatformUpgradeMigrations,
              self).add_snapshot(std_mig_id, snapshot_impl)

    def __add(self, migration_id, impl_name):
        """
        Validates that the migration id is the correct type/format and then
        return the canonical format of the id. Add the id as an array of
        integers into the list of migration ids.
        """
        # First validate that the migration_id is the correct type/format.
        self.__validate_migration_id(migration_id, impl_name)

        # Then we must standardize the migration_id.
        std_migration_id = self.__standardize_migration_id_to_array(
            migration_id, impl_name)
        std_string = '.'.join(str(i) for i in std_migration_id)

        # Then we should check if this migration_id has already been used
        if std_migration_id in self.__migration_ids:
            raise MigrationIdAlreadyUsedError.fromMigrationId(
                migration_id, std_string, impl_name)

        # Lastly we should add this new array into the internal migration list.
        self.__migration_ids.append(std_migration_id)

        # Return back the standardized format of the migration id
        return std_string

    @staticmethod
    def __validate_migration_id(migration_id, impl_name):
        # First validate that the id is a string
        if not isinstance(migration_id, basestring):
            raise MigrationIdIncorrectTypeError(migration_id, impl_name)

        # Next check if the id is the right format
        if not PlatformUpgradeMigrations.MIGRATION_ID_REGEX.match(
                migration_id):
            raise MigrationIdIncorrectFormatError.from_fields(
                migration_id, impl_name,
                PlatformUpgradeMigrations.MIGRATION_ID_REGEX.pattern)

    @staticmethod
    def __standardize_migration_id_to_array(migration_id, impl_name):
        # Split on the period and convert to integer
        array = [int(i) for i in migration_id.split('.')]

        #
        # We cannot allow a migration id of essentially '0' because otherwise
        # there would be no way to add a migration that goes before this.
        #
        if not any(array):
            raise MigrationIdIncorrectFormatError(
                "The migration id '{}' used in the function '{}' cannot be"
                " used because a 0 migration id is not allowed.".format(
                    migration_id, impl_name))

        # Next we want to trim all trailing zeros so ex: 5.3.0.0 == 5.3
        while array:
            if not array[-1]:
                # Remove the last element which is a zero from array
                array.pop()
            else:
                break

        return array

    def get_sorted_ids(self):
        # First sort the migration ids
        self.__migration_ids.sort()

        # Then convert all these arrays to the usual string format.
        return [
            '.'.join(str(i) for i in migration_id)
            for migration_id in self.__migration_ids
        ]

    def get_repository_impls_to_exec(self, migration_id_list):
        return self.__get_impls(migration_id_list, self.get_repository_dict())

    def get_source_config_impls_to_exec(self, migration_id_list):
        return self.__get_impls(migration_id_list,
                                self.get_source_config_dict())

    def get_linked_source_impls_to_exec(self, migration_id_list):
        return self.__get_impls(migration_id_list,
                                self.get_linked_source_dict())

    def get_virtual_source_impls_to_exec(self, migration_id_list):
        return self.__get_impls(migration_id_list,
                                self.get_virtual_source_dict())

    def get_snapshot_impls_to_exec(self, migration_id_list):
        return self.__get_impls(migration_id_list, self.get_snapshot_dict())

    @staticmethod
    def __get_impls(migration_id_list, impl_dict):
        return_list = []
        for migration_id in migration_id_list:
            # Should only add the function if the id exists in the map.
            if migration_id in impl_dict:
                return_list.append(impl_dict[migration_id])
        return return_list


class LuaUpgradeMigrations(UpgradeMigrations):
    LUA_VERSION_REGEX = re.compile(r'^\d+\.\d+$')

    def __init__(self):
        super(LuaUpgradeMigrations, self).__init__()

    def add_repository(self, migration_id, repository_impl):
        std_mig_id = self.__validate_lua_major_minor_version(
            migration_id, repository_impl.__name__,
            Op.UPGRADE_REPOSITORY.value, self.get_repository_dict)
        super(LuaUpgradeMigrations,
              self).add_repository(std_mig_id, repository_impl)

    def add_source_config(self, migration_id, source_config_impl):
        std_mig_id = self.__validate_lua_major_minor_version(
            migration_id, source_config_impl.__name__,
            Op.UPGRADE_SOURCE_CONFIG.value, self.get_source_config_dict)
        super(LuaUpgradeMigrations,
              self).add_source_config(std_mig_id, source_config_impl)

    def add_linked_source(self, migration_id, linked_source_impl):
        std_mig_id = self.__validate_lua_major_minor_version(
            migration_id, linked_source_impl.__name__,
            Op.UPGRADE_LINKED_SOURCE.value, self.get_linked_source_dict)
        super(LuaUpgradeMigrations,
              self).add_linked_source(std_mig_id, linked_source_impl)

    def add_virtual_source(self, migration_id, virtual_source_impl):
        std_mig_id = self.__validate_lua_major_minor_version(
            migration_id, virtual_source_impl.__name__,
            Op.UPGRADE_VIRTUAL_SOURCE.value, self.get_virtual_source_dict)
        super(LuaUpgradeMigrations,
              self).add_virtual_source(std_mig_id, virtual_source_impl)

    def add_snapshot(self, migration_id, snapshot_impl):
        std_mig_id = self.__validate_lua_major_minor_version(
            migration_id, snapshot_impl.__name__, Op.UPGRADE_SNAPSHOT.value,
            self.get_snapshot_dict)
        super(LuaUpgradeMigrations, self).add_snapshot(std_mig_id,
                                                       snapshot_impl)

    @staticmethod
    def __validate_lua_major_minor_version(migration_id, impl_name,
                                           decorator_name, impl_getter):
        # First validate that the major minor version is a string
        if not isinstance(migration_id, basestring):
            raise MigrationIdIncorrectTypeError(migration_id, impl_name)

        # Next check if the id already exists in this particular dictionary
        if migration_id in impl_getter():
            raise MigrationIdAlreadyUsedError.fromLuaVersion(
                migration_id, impl_name, decorator_name)

        # Lastly check if the id is the right format for a lua version
        if not LuaUpgradeMigrations.LUA_VERSION_REGEX.match(migration_id):
            raise MigrationIdIncorrectFormatError.from_fields(
                migration_id, impl_name,
                LuaUpgradeMigrations.LUA_VERSION_REGEX.pattern)

        #
        # Now we want to decompose the version string to get rid of any
        # leading zeros (such as 1.01 -> 1.1)
        #
        return '.'.join(
            str(i) for i in [int(i) for i in migration_id.split('.')])

    def get_repository_impls_to_exec(self, migration_id):
        return self.__get_sorted_impls(migration_id,
                                       self.get_repository_dict())

    def get_source_config_impls_to_exec(self, migration_id):
        return self.__get_sorted_impls(migration_id,
                                       self.get_source_config_dict())

    def get_linked_source_impls_to_exec(self, migration_id):
        return self.__get_sorted_impls(migration_id,
                                       self.get_linked_source_dict())

    def get_virtual_source_impls_to_exec(self, migration_id):
        return self.__get_sorted_impls(migration_id,
                                       self.get_virtual_source_dict())

    def get_snapshot_impls_to_exec(self, migration_id):
        return self.__get_sorted_impls(migration_id, self.get_snapshot_dict())

    @staticmethod
    def __get_sorted_impls(migration_id, impl_dict):
        #
        # If there is no migration id, this means no lua version was provided
        # so just return an empty list.
        #
        if not migration_id:
            return []
        #
        # First filter out all ids less than the migration id. We need to do
        # this because even after sorting, we wouldn't know where in the list
        # to start iterating over.
        #
        def filter_lower(current):
            return (sorted([current, migration_id],
                           key=float)[0] == migration_id)

        # Filter and sort the list.
        id_list = sorted(filter(filter_lower, impl_dict.keys()), key=float)

        #
        # Loop through ids after filtering out lower ids and sorting to add
        # the impl to the resulting list in the correct order.
        #
        return [impl_dict[found_id] for found_id in id_list]
