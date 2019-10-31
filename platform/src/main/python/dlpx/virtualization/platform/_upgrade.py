#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

# -*- coding: utf-8 -*-

"""UpgradeOperations for the Virtualization Platform

There are 5 different objects that we can upgrade. All migration ids must be
unique.
"""
from dlpx.virtualization.platform.exceptions import MigrationIdAlreadyUsedError


__all__ = ['UpgradeOperations']

class UpgradeOperations(object):

    def __init__(self):
        self.__migration_ids = set()

        self.repository_id_to_impl = {}
        self.source_config_id_to_impl = {}
        self.linked_source_id_to_impl = {}
        self.virtual_source_id_to_impl = {}
        self.snapshot_id_to_impl = {}

    def repository(self, migration_id):
        def repository_decorator(repository_impl):
            self._migration_id_check_helper(migration_id, repository_impl)
            self.repository_id_to_impl[migration_id] = repository_impl
            self.__migration_ids.add(migration_id)
            return repository_impl
        return repository_decorator

    def source_config(self, migration_id):
        def source_config_decorator(source_config_impl):
            self._migration_id_check_helper(migration_id, source_config_impl)
            self.source_config_id_to_impl[migration_id] = source_config_impl
            self.__migration_ids.add(migration_id)
            return source_config_impl
        return source_config_decorator

    def linked_source(self, migration_id):
        def linked_source_decorator(linked_source_impl):
            self._migration_id_check_helper(migration_id, linked_source_impl)
            self.linked_source_id_to_impl[migration_id] = linked_source_impl
            self.__migration_ids.add(migration_id)
            return linked_source_impl
        return linked_source_decorator

    def virtual_source(self, migration_id):
        def virtual_source_decorator(virtual_source_impl):
            self._migration_id_check_helper(migration_id, virtual_source_impl)
            self.virtual_source_id_to_impl[migration_id] = virtual_source_impl
            self.__migration_ids.add(migration_id)
            return virtual_source_impl
        return virtual_source_decorator

    def snapshot(self, migration_id):
        def snapshot_decorator(snapshot_impl):
            self._migration_id_check_helper(migration_id, snapshot_impl)
            self.snapshot_id_to_impl[migration_id] = snapshot_impl
            self.__migration_ids.add(migration_id)
            return snapshot_impl
        return snapshot_decorator

    @property
    def migration_id_list(self):
        return sorted(self.__migration_ids)

    def _migration_id_check_helper(self, migration_id, migration_impl):
        if migration_id in self.__migration_ids:
            raise MigrationIdAlreadyUsedError(migration_id,
                                              migration_impl.__name__)


    def _internal_upgrade(self, request):
        """Upgrade Wrapper for plugins.
        """
        # TODO
