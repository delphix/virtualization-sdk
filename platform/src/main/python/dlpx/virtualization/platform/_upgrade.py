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
from dlpx.virtualization.platform import MigrationIdSet
from dlpx.virtualization.platform import validation_util as v
from dlpx.virtualization.platform.operation import Operation as Op
from dlpx.virtualization.platform.exceptions import (
    IncorrectUpgradeObjectTypeError)

logger = logging.getLogger(__name__)

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

    @staticmethod
    def _success_upgrade_response(upgraded_dict):
        upgrade_result = platform_pb2.UpgradeResult(
            post_upgrade_parameters=upgraded_dict)
        upgrade_response = platform_pb2.UpgradeResponse(
            return_value=upgrade_result)
        return upgrade_response

    def __process_upgrade_request(self, request, id_to_impl):
        """Iterate through all objects in the pre_upgrade_parameters map,
        invoke all available migrations on each object and its metadata,
        and return a map containing the updated metadata for each object.
        """
        post_upgrade_parameters = {}
        for (object_ref, metadata) in request.pre_upgrade_parameters.items():
            # Load the object metadata into a dictionary
            current_metadata = json.loads(metadata)
            #
            # Loop through all migrations that were passed into the upgrade
            # request. Protobuf will preserve the ordering of repeated
            # elements, so we can rely on the backend to sort the migration
            # ids before packing them into the request.
            #
            for migration_id in request.migration_ids:
                # Only try to execute the function if the id exists in the map.
                if migration_id in id_to_impl:
                    current_metadata = id_to_impl[migration_id](current_metadata)
            post_upgrade_parameters[object_ref] = json.dumps(current_metadata)

        return self._success_upgrade_response(post_upgrade_parameters)

    def _internal_repository(self, request):
        """Upgrade repositories for plugins.
        """
        if request.type != platform_pb2.UpgradeRequest.REPOSITORY:
            raise IncorrectUpgradeObjectTypeError(
                request.type, platform_pb2.UpgradeRequest.REPOSITORY)

        logger.debug('Upgrade repositories [{}]'.format(
            ', '.join(sorted(request.pre_upgrade_parameters.keys()))))

        return self.__process_upgrade_request(request, self.repository_id_to_impl)

    def _internal_source_config(self, request):
        """Upgrade source configs for plugins.
        """
        if request.type != platform_pb2.UpgradeRequest.SOURCECONFIG:
            raise IncorrectUpgradeObjectTypeError(
                request.type, platform_pb2.UpgradeRequest.SOURCECONFIG)

        logger.debug('Upgrade source configs [{}]'.format(
            ', '.join(sorted(request.pre_upgrade_parameters.keys()))))

        return self.__process_upgrade_request(request, self.source_config_id_to_impl)

    def _internal_linked_source(self, request):
        """Upgrade linked source for plugins.
        """
        if request.type != platform_pb2.UpgradeRequest.LINKEDSOURCE:
            raise IncorrectUpgradeObjectTypeError(
                request.type, platform_pb2.UpgradeRequest.LINKEDSOURCE)

        logger.debug('Upgrade linked sources [{}]'.format(
            ', '.join(sorted(request.pre_upgrade_parameters.keys()))))

        return self.__process_upgrade_request(request, self.linked_source_id_to_impl)

    def _internal_virtual_source(self, request):
        """Upgrade virtual sources for plugins.
        """
        if request.type != platform_pb2.UpgradeRequest.VIRTUALSOURCE:
            raise IncorrectUpgradeObjectTypeError(
                request.type, platform_pb2.UpgradeRequest.VIRTUALSOURCE)

        logger.debug('Upgrade virtual sources [{}]'.format(
            ', '.join(sorted(request.pre_upgrade_parameters.keys()))))

        return self.__process_upgrade_request(request, self.virtual_source_id_to_impl)

    def _internal_snapshot(self, request):
        """Upgrade snapshots for plugins.
        """
        if request.type != platform_pb2.UpgradeRequest.SNAPSHOT:
            raise IncorrectUpgradeObjectTypeError(
                request.type, platform_pb2.UpgradeRequest.SNAPSHOT)

        logger.debug('Upgrade snapshots [{}]'.format(
            ', '.join(sorted(request.pre_upgrade_parameters.keys()))))

        return self.__process_upgrade_request(request, self.snapshot_id_to_impl)
