#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

# -*- coding: utf-8 -*-

"""UpgradeOperations for the Virtualization Platform

There are 5 different objects that we can upgrade. All migration ids must be
unique. To upgrade a specific schema, the plugin author would use that specific
decorator specifying the migration id. We save the implementations of each of
the upgrade functions in a dict for the specific schema. For each new upgrade
operation of the same schema, the key will be the migration id, and the value
will be the function that was implemented.
"""
from dlpx.virtualization.platform import MigrationIdSet
from dlpx.virtualization.platform import validation_util as v
from dlpx.virtualization.platform.operation import Operation as Op

__all__ = ['UpgradeOperations']


class UpgradeOperations(object):

    def __init__(self):
        self.__migration_id_set = MigrationIdSet()

        self.repository_id_to_impl = {}
        self.source_config_id_to_impl = {}
        self.linked_source_id_to_impl = {}
        self.virtual_source_id_to_impl = {}
        self.snapshot_id_to_impl = {}

    def repository(self, migration_id):
        def repository_decorator(repository_impl):

            std_mig_id = self.__migration_id_set.add(
                migration_id, repository_impl.__name__)
            self.repository_id_to_impl[std_mig_id] = v.check_function(
                repository_impl, Op.UPGRADE_REPOSITORY)
            return repository_impl
        return repository_decorator

    def source_config(self, migration_id):
        def source_config_decorator(source_config_impl):
            std_mig_id = self.__migration_id_set.add(
                migration_id, source_config_impl.__name__)
            self.source_config_id_to_impl[std_mig_id] = v.check_function(
                source_config_impl, Op.UPGRADE_SOURCE_CONFIG)
            return source_config_impl
        return source_config_decorator

    def linked_source(self, migration_id):
        def linked_source_decorator(linked_source_impl):
            std_mig_id = self.__migration_id_set.add(
                migration_id, linked_source_impl.__name__)
            self.linked_source_id_to_impl[std_mig_id] = v.check_function(
                linked_source_impl, Op.UPGRADE_LINKED_SOURCE)
            return linked_source_impl
        return linked_source_decorator

    def virtual_source(self, migration_id):
        def virtual_source_decorator(virtual_source_impl):
            std_mig_id = self.__migration_id_set.add(
                migration_id, virtual_source_impl.__name__)
            self.virtual_source_id_to_impl[std_mig_id] = v.check_function(
                virtual_source_impl, Op.UPGRADE_VIRTUAL_SOURCE)
            return virtual_source_impl
        return virtual_source_decorator

    def snapshot(self, migration_id):
        def snapshot_decorator(snapshot_impl):
            std_mig_id = self.__migration_id_set.add(
                migration_id, snapshot_impl.__name__)
            self.snapshot_id_to_impl[std_mig_id] = v.check_function(
                snapshot_impl, Op.UPGRADE_SNAPSHOT)
            return snapshot_impl
        return snapshot_decorator

    @property
    def migration_id_list(self):
        return self.__migration_id_set.get_sorted_ids()

    def _internal_upgrade(self, request):
        """Upgrade Wrapper for plugins.
        """
        # TODO
