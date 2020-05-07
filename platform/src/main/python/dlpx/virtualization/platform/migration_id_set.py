#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import logging
import re

from dlpx.virtualization.platform.exceptions import (
    MigrationIdAlreadyUsedError, MigrationIdIncorrectTypeError,
    MigrationIdIncorrectFormatError)

MIGRATION_ID_REGEX = re.compile(r'^\d+(\.\d+)*$')
logger = logging.getLogger(__name__)


class MigrationIdSet:
    """
    Keeps track of all migrations and validites/standardizes them as they are
    added / parsed.

    Exceptions can be thrown when trying to add a new migration id. Otherwise
    at the end of reading in all migration functions can be gotten in the
    correct order.
    """
    def __init__(self):
        """
        The list of migration ids will store migrations as an array of ids
        where the id is represented by the standardized array of positive
        integers. For example if there were these ids: 1.0.0, 1.2.03, and
        2.0.1.0, __migration_ids would be [ [1], [1, 2, 3], [2, 0, 1]]
        """
        self.__migration_ids = []

    def add(self, migration_id, impl_name):
        """
        Validates that the migration id is the correct type/format and then
        return the canonical format of the id. Add the id as an array of
        integers into the list of migration ids.
        """
        # First validate that the migration_id is the correct type/format.
        self.validate_migration_id(migration_id, impl_name)

        # Then we must standardize the migration_id.
        std_migration_id = self.standardize_migration_id_to_array(
            migration_id, impl_name)
        std_string = '.'.join(str(i) for i in std_migration_id)

        # Then we should check if this migration_id has already been used
        if std_migration_id in self.__migration_ids:
            raise MigrationIdAlreadyUsedError(migration_id,
                                              std_string,
                                              impl_name)

        # Lastly we should add this new array into the internal migration list.
        self.__migration_ids.append(std_migration_id)

        # Return back the standardized format of the migration id
        return std_string

    @staticmethod
    def validate_migration_id(migration_id, impl_name):
        # First validate that the id is a string
        if not isinstance(migration_id, basestring):
            raise MigrationIdIncorrectTypeError(migration_id, impl_name)

        # Next check if the id is the right format
        if not MIGRATION_ID_REGEX.match(migration_id):
            raise MigrationIdIncorrectFormatError.from_fields(
                migration_id, impl_name, MIGRATION_ID_REGEX.pattern)

    @staticmethod
    def standardize_migration_id_to_array(migration_id, impl_name):
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
        return ['.'.join(str(i) for i in migration_id)
                for migration_id in self.__migration_ids]
