#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

# -*- coding: utf-8 -*-
"""Virtualization Platform API wrappers.

This module contains all Virtualization Platform API wrappers (for details on
the API definition, see platform/src/proto/platform.proto).

The wrappers are the implementation of the Virtualization Platform API. They
take <OperationName>Request protobuf message as input and return
<OperationName>Response, e.g. ConfigureRequest and ConfigureResponse. The
wrappers are called by the Delphix Engine and their role is to unpack input
*Request protobuf message, delegate to the user defined method that has logic
for the virtualization operation itself (such as configure), and craft a
response object. The wrappers assume that the Python runtime will have
virtulization operation method definitions imported prior, i.e. user defined
configure() method is defined in the runtime and hence we can just
call configure().

Todo:
    * Write wrappers for all remaining virtualization operations.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

from dlpx.virtualization import common_pb2
from dlpx.virtualization import platform_pb2


def configure_wrapper(configure_request):
    """Configure operation wrapper.

    Executed just after cloning the captured data and mounting it to a target
    environment. Specifically, this plugin operation is run during provision and
    refresh, prior to taking the initial snapshot of the clone. This plugin
    operation is run before the user-customizable Configure Clone and Before
    Refresh operations are run. It must return a sourceConfig object that
    represents the new dataset.

    Configure the data to be usable on the target environment. For database data
    files, this may mean recovering from a crash consistent format or backup.
    For application files, this may mean reconfiguring XML files or rewriting
    hostnames and symlinks.

    Args:
      configure_request (ConfigureRequest): Configure operation arguments.

    Returns:
      ConfigureResponse: A response contiaining the return value of the
      configure operation, as a ConfigureResult.
    """

    config = configure(
        source=configure_request.source,
        repository=configure_request.repository,
        snapshot=configure_request.snapshot)
    configure_response = platform_pb2.ConfigureResponse()
    configure_response.return_value.source_config.parameters.json = config.to_json()
    return configure_response

def repository_discovery_wrapper(repository_discovery_request):
    """Repository discovery wrapper.

  Executed just after adding or refreshing an environment. This plugin
  operation is run prior to discovering source configs. This plugin operation
  returns a list of repositories installed on a environment.

  Discover the repositories on an environment given a source connection.

  Args:
      repository_discovery_request (RepositoryDiscoveryRequest): Repository
      Discovery operation arguments.

  Returns:
      RepositoryDiscoveryResponse: The return value of repository discovery
      operation.
  """
    def to_protobuf(repository):
        parameters = common_pb2.PluginDefinedObject()
        parameters.json = repository.to_json()
        repository_protobuf = common_pb2.Repository()
        repository_protobuf.parameters.CopyFrom(parameters)
        return repository_protobuf

    repositories = repository_discovery(
        source_connection=repository_discovery_request.source_connection)
    repository_discovery_response = platform_pb2.RepositoryDiscoveryResponse()
    repository_protobuf_list = map(to_protobuf, repositories)
    repository_discovery_response.return_value.repositories.extend(repository_protobuf_list)
    return repository_discovery_response


def source_config_discovery_wrapper(source_config_discovery_request):
    """Source config discovery wrapper.

    Executed when adding or refreshing an environment. This plugin operation is
    run after discovering repositories and before persisting/updating repository
    and source config data in MDS. This plugin operation returns a list of source
    configs from a discovered repository.

    Discover the source configs on an environment given a discovered repository.

    Args:
        source_config_discovery_request (SourceConfigDiscoveryRequest): Source
        Config Discovery arguments.

    Returns:
        SourceConfigDiscoveryResponse: The return value of source config
        discovery operation.
    """
    def to_protobuf(source_config):
        parameters = common_pb2.PluginDefinedObject()
        parameters.json = source_config.to_json()
        source_config_protobuf = common_pb2.SourceConfig()
        source_config_protobuf.parameters.CopyFrom(parameters)
        return source_config_protobuf

    source_configs = source_config_discovery(
        source_connection=source_config_discovery_request.source_connection,
        repository=source_config_discovery_request.repository)
    source_config_discovery_response = platform_pb2.SourceConfigDiscoveryResponse()
    source_config_protobuf_list = map(to_protobuf, source_configs)
    source_config_discovery_response.return_value.source_configs.extend(source_config_protobuf_list)
    return source_config_discovery_response


def direct_pre_snapshot_wrapper(direct_pre_snapshot_request):
    """Pre Snapshot Wrapper for direct plugins.

    Executed before creating a snapshot. This plugin
    operation is run prior to creating a snapshot for a direct source.

    Run pre-snapshot operation for a direct source.

    Args:
       direct_pre_snapshot_request (DirectPreSnapshotRequest):
       Pre Snapshot arguments.

    Returns:
       DirectPreSnapshotResponse: A response containing DirectPreSnapshotResult
       if successful or PluginErrorResult in case of an error.
    """
    direct_pre_snapshot(
        source=direct_pre_snapshot_request.direct_source,
        repository=direct_pre_snapshot_request.repository,
        config=direct_pre_snapshot_request.source_config)

    direct_pre_snapshot_response = platform_pb2.DirectPreSnapshotResponse()
    direct_pre_snapshot_response.return_value.CopyFrom(platform_pb2.DirectPreSnapshotResult())

    return direct_pre_snapshot_response


def direct_post_snapshot_wrapper(direct_post_snapshot_request):
    """Post Snapshot Wrapper for direct plugins.

    Executed after creating a snapshot. This plugin
    operation is run after creating a snapshot for a direct source.

    Run post-snapshot operation for a direct source.

    Args:
       direct_post_snapshot_request (DirectPreSnapshotRequest):
       Post Snapshot arguments.

    Returns:
       DirectPostSnapshotResponse: A response containing the return value -
       DirectPostSnapshotResult which has the snapshot metadata on success. In
       case of errors, response object will contain PluginErrorResult.
    """
    def to_protobuf(snapshot):
        parameters = common_pb2.PluginDefinedObject()
        parameters.json = snapshot.to_json()
        snapshot_protobuf = common_pb2.Snapshot()
        snapshot_protobuf.parameters.CopyFrom(parameters)
        return snapshot_protobuf

    snapshot = direct_post_snapshot(
        source=direct_post_snapshot_request.direct_source,
        repository=direct_post_snapshot_request.repository,
        config=direct_post_snapshot_request.source_config)

    direct_post_snapshot_response = platform_pb2.DirectPostSnapshotResponse()
    direct_post_snapshot_response.return_value.snapshot.CopyFrom(to_protobuf(snapshot))

    return direct_post_snapshot_response
