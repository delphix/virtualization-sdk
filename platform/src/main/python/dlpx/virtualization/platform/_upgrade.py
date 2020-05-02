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
import json
import logging

from dlpx.virtualization.api import platform_pb2
from dlpx.virtualization.platform import (LuaUpgradeMigrations, MigrationType,
                                          PlatformUpgradeMigrations)
from dlpx.virtualization.platform.exceptions import (
    IncorrectUpgradeObjectTypeError, UnknownMigrationTypeError)

logger = logging.getLogger(__name__)

__all__ = ['UpgradeOperations']


class UpgradeOperations(object):
    def __init__(self):
        self.platform_migrations = PlatformUpgradeMigrations()
        self.lua_migrations = LuaUpgradeMigrations()

    def repository(self, migration_id, migration_type=MigrationType.PLATFORM):
        def repository_decorator(repository_impl):
            if migration_type == MigrationType.PLATFORM:
                self.platform_migrations.add_repository(
                    migration_id, repository_impl)
            elif migration_type == MigrationType.LUA:
                self.lua_migrations.add_repository(migration_id,
                                                   repository_impl)
            else:
                raise UnknownMigrationTypeError(migration_type)
            return repository_impl

        return repository_decorator

    def source_config(self,
                      migration_id,
                      migration_type=MigrationType.PLATFORM):
        def source_config_decorator(source_config_impl):
            if migration_type == MigrationType.PLATFORM:
                self.platform_migrations.add_source_config(
                    migration_id, source_config_impl)
            elif migration_type == MigrationType.LUA:
                self.lua_migrations.add_source_config(migration_id,
                                                      source_config_impl)
            else:
                raise UnknownMigrationTypeError(migration_type)
            return source_config_impl

        return source_config_decorator

    def linked_source(self,
                      migration_id,
                      migration_type=MigrationType.PLATFORM):
        def linked_source_decorator(linked_source_impl):
            if migration_type == MigrationType.PLATFORM:
                self.platform_migrations.add_linked_source(
                    migration_id, linked_source_impl)
            elif migration_type == MigrationType.LUA:
                self.lua_migrations.add_linked_source(migration_id,
                                                      linked_source_impl)
            else:
                raise UnknownMigrationTypeError(migration_type)
            return linked_source_impl

        return linked_source_decorator

    def virtual_source(self,
                       migration_id,
                       migration_type=MigrationType.PLATFORM):
        def virtual_source_decorator(virtual_source_impl):
            if migration_type == MigrationType.PLATFORM:
                self.platform_migrations.add_virtual_source(
                    migration_id, virtual_source_impl)
            elif migration_type == MigrationType.LUA:
                self.lua_migrations.add_virtual_source(migration_id,
                                                       virtual_source_impl)
            else:
                raise UnknownMigrationTypeError(migration_type)
            return virtual_source_impl

        return virtual_source_decorator

    def snapshot(self, migration_id, migration_type=MigrationType.PLATFORM):
        def snapshot_decorator(snapshot_impl):
            if migration_type == MigrationType.PLATFORM:
                self.platform_migrations.add_snapshot(migration_id,
                                                      snapshot_impl)
            elif migration_type == MigrationType.LUA:
                self.lua_migrations.add_snapshot(migration_id, snapshot_impl)
            else:
                raise UnknownMigrationTypeError(migration_type)
            return snapshot_impl

        return snapshot_decorator

    @property
    def migration_id_list(self):
        return self.platform_migrations.get_sorted_ids()

    @staticmethod
    def _success_upgrade_response(upgraded_dict):
        upgrade_result = platform_pb2.UpgradeResult(
            post_upgrade_parameters=upgraded_dict)
        upgrade_response = platform_pb2.UpgradeResponse(
            return_value=upgrade_result)
        return upgrade_response

    @staticmethod
    def _run_migration_upgrades(request, lua_impls_getter,
                                platform_impls_getter):
        """
        Given the list of lua and platform migration to run, iterate and
        invoke these migrations on each object and its metadata, and return a
        dict containing the upgraded parameters.
        """
        post_upgrade_parameters = {}
        #
        # For the request.migration_ids list, protobuf will preserve the
        # ordering of repeated elements, so we can rely on the backend to
        # give us the already sorted list of migrations
        #
        impls_list = lua_impls_getter(
            request.lua_upgrade_version) + platform_impls_getter(
                request.migration_ids)
        for (object_ref, metadata) in request.pre_upgrade_parameters.items():
            # Load the object metadata into a dictionary
            current_metadata = json.loads(metadata)
            for migration_function in impls_list:
                current_metadata = migration_function(current_metadata)
            post_upgrade_parameters[object_ref] = json.dumps(current_metadata)

        return post_upgrade_parameters

    def _internal_repository(self, request):
        """Upgrade repositories for plugins.
        """
        if request.type != platform_pb2.UpgradeRequest.REPOSITORY:
            raise IncorrectUpgradeObjectTypeError(
                request.type, platform_pb2.UpgradeRequest.REPOSITORY)

        logger.debug('Upgrade repositories [{}]'.format(', '.join(
            sorted(request.pre_upgrade_parameters.keys()))))

        post_upgrade_parameters = self._run_migration_upgrades(
            request, self.lua_migrations.get_repository_impls_to_exec,
            self.platform_migrations.get_repository_impls_to_exec)
        return self._success_upgrade_response(post_upgrade_parameters)

    def _internal_source_config(self, request):
        """Upgrade source configs for plugins.
        """
        if request.type != platform_pb2.UpgradeRequest.SOURCECONFIG:
            raise IncorrectUpgradeObjectTypeError(
                request.type, platform_pb2.UpgradeRequest.SOURCECONFIG)

        logger.debug('Upgrade source configs [{}]'.format(', '.join(
            sorted(request.pre_upgrade_parameters.keys()))))

        post_upgrade_parameters = self._run_migration_upgrades(
            request, self.lua_migrations.get_source_config_impls_to_exec,
            self.platform_migrations.get_source_config_impls_to_exec)
        return self._success_upgrade_response(post_upgrade_parameters)

    def _internal_linked_source(self, request):
        """Upgrade linked source for plugins.
        """
        if request.type != platform_pb2.UpgradeRequest.LINKEDSOURCE:
            raise IncorrectUpgradeObjectTypeError(
                request.type, platform_pb2.UpgradeRequest.LINKEDSOURCE)

        logger.debug('Upgrade linked sources [{}]'.format(', '.join(
            sorted(request.pre_upgrade_parameters.keys()))))

        post_upgrade_parameters = self._run_migration_upgrades(
            request, self.lua_migrations.get_linked_source_impls_to_exec,
            self.platform_migrations.get_linked_source_impls_to_exec)
        return self._success_upgrade_response(post_upgrade_parameters)

    def _internal_virtual_source(self, request):
        """Upgrade virtual sources for plugins.
        """
        if request.type != platform_pb2.UpgradeRequest.VIRTUALSOURCE:
            raise IncorrectUpgradeObjectTypeError(
                request.type, platform_pb2.UpgradeRequest.VIRTUALSOURCE)

        logger.debug('Upgrade virtual sources [{}]'.format(', '.join(
            sorted(request.pre_upgrade_parameters.keys()))))

        post_upgrade_parameters = self._run_migration_upgrades(
            request, self.lua_migrations.get_virtual_source_impls_to_exec,
            self.platform_migrations.get_virtual_source_impls_to_exec)
        return self._success_upgrade_response(post_upgrade_parameters)

    def _internal_snapshot(self, request):
        """Upgrade snapshots for plugins.
        """
        if request.type != platform_pb2.UpgradeRequest.SNAPSHOT:
            raise IncorrectUpgradeObjectTypeError(
                request.type, platform_pb2.UpgradeRequest.SNAPSHOT)

        logger.debug('Upgrade snapshots [{}]'.format(', '.join(
            sorted(request.pre_upgrade_parameters.keys()))))

        post_upgrade_parameters = self._run_migration_upgrades(
            request, self.lua_migrations.get_snapshot_impls_to_exec,
            self.platform_migrations.get_snapshot_impls_to_exec)
        return self._success_upgrade_response(post_upgrade_parameters)
