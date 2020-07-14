#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

# -*- coding: utf-8 -*-
"""DiscoveryOperations for the Virtualization Platform

"""
import json

from dlpx.virtualization.api import common_pb2, platform_pb2
from dlpx.virtualization.common import RemoteConnection
from dlpx.virtualization.platform import validation_util as v
from dlpx.virtualization.platform.exceptions import (
    IncorrectReturnTypeError, OperationAlreadyDefinedError,
    OperationNotDefinedError)
from dlpx.virtualization.platform.operation import Operation as Op

__all__ = ['DiscoveryOperations']


class DiscoveryOperations(object):
    def __init__(self):
        self.repository_impl = None
        self.source_config_impl = None

    def repository(self):
        def repository_decorator(repository_impl):
            if self.repository_impl:
                raise OperationAlreadyDefinedError(Op.DISCOVERY_REPOSITORY)

            self.repository_impl = v.check_function(repository_impl,
                                                    Op.DISCOVERY_REPOSITORY)
            return repository_impl

        return repository_decorator

    def source_config(self):
        def source_config_decorator(source_config_impl):
            if self.source_config_impl:
                raise OperationAlreadyDefinedError(Op.DISCOVERY_SOURCE_CONFIG)
            self.source_config_impl = v.check_function(
                source_config_impl, Op.DISCOVERY_SOURCE_CONFIG)
            return source_config_impl

        return source_config_decorator

    def _internal_repository(self, request):
        """Repository discovery wrapper.

        Executed just after adding or refreshing an environment. This plugin
        operation is run prior to discovering source configs. This plugin
        operation returns a list of repositories installed on a environment.

        Discover the repositories on an environment given a source connection.

        Args:
            request (RepositoryDiscoveryRequest): Repository
            Discovery operation arguments.

        Returns:
            RepositoryDiscoveryResponse: The return value of repository
            discovery operation.
        """
        from generated.definitions import RepositoryDefinition

        def to_protobuf(repository):
            parameters = common_pb2.PluginDefinedObject()
            parameters.json = json.dumps(repository.to_dict())
            repository_protobuf = common_pb2.Repository()
            repository_protobuf.parameters.CopyFrom(parameters)
            return repository_protobuf

        if not self.repository_impl:
            raise OperationNotDefinedError(Op.DISCOVERY_REPOSITORY)

        repositories = self.repository_impl(
            source_connection=RemoteConnection.from_proto(
                request.source_connection))

        # Validate that this is a list of Repository objects
        if not isinstance(repositories, list):
            raise IncorrectReturnTypeError(Op.DISCOVERY_REPOSITORY,
                                           type(repositories),
                                           [RepositoryDefinition])

        if not all(
                isinstance(repo, RepositoryDefinition)
                for repo in repositories):
            raise IncorrectReturnTypeError(
                Op.DISCOVERY_REPOSITORY, [type(repo) for repo in repositories],
                [RepositoryDefinition])

        repository_discovery_response = (
            platform_pb2.RepositoryDiscoveryResponse())
        repository_protobuf_list = [to_protobuf(repo) for repo in repositories]
        repository_discovery_response.return_value.repositories.extend(
            repository_protobuf_list)
        return repository_discovery_response

    def _internal_source_config(self, request):
        """Source config discovery wrapper.

        Executed when adding or refreshing an environment. This plugin
        operation is run after discovering repositories and before
        persisting/updating repository and source config data in MDS. This
        plugin operation returns a list of source configs from a discovered
        repository.

        Discover the source configs on an environment given a discovered
        repository.

        Args:
            request (SourceConfigDiscoveryRequest): Source
            Config Discovery arguments.

        Returns:
            SourceConfigDiscoveryResponse: The return value of source config
            discovery operation.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import RepositoryDefinition
        from generated.definitions import SourceConfigDefinition

        def to_protobuf(source_config):
            parameters = common_pb2.PluginDefinedObject()
            parameters.json = json.dumps(source_config.to_dict())
            source_config_protobuf = common_pb2.SourceConfig()
            source_config_protobuf.parameters.CopyFrom(parameters)
            return source_config_protobuf

        if not self.source_config_impl:
            raise OperationNotDefinedError(Op.DISCOVERY_SOURCE_CONFIG)

        repository_definition = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))

        source_configs = self.source_config_impl(
            source_connection=RemoteConnection.from_proto(
                request.source_connection),
            repository=repository_definition)

        # Validate that this is a list of SourceConfigDefinition objects
        if not isinstance(source_configs, list):
            raise IncorrectReturnTypeError(Op.DISCOVERY_SOURCE_CONFIG,
                                           type(source_configs),
                                           [SourceConfigDefinition])

        if not all(
                isinstance(config, SourceConfigDefinition)
                for config in source_configs):
            raise IncorrectReturnTypeError(
                Op.DISCOVERY_SOURCE_CONFIG,
                [type(config)
                 for config in source_configs], [SourceConfigDefinition])

        source_config_discovery_response = (
            platform_pb2.SourceConfigDiscoveryResponse())
        source_config_protobuf_list = [
            to_protobuf(config) for config in source_configs
        ]
        source_config_discovery_response.return_value.source_configs.extend(
            source_config_protobuf_list)
        return source_config_discovery_response
