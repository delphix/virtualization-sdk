#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

# -*- coding: utf-8 -*-

"""Plugin for the Virtualization Platform

This module contains a skeleton of a plugin that allows users to extend the Delphix Dynamic Data
Platform's support for external data sources. A plugin is composed of three different parts
that determine how each stage of a data source's virtualization should be performed:
DiscoveryOperations, LinkedOperations and VirtualOperations. These three classes contain all the
methods available during the process of discovery, direct or staged linking, and provisioning
virtual datasets. Let's see an example of how we can start writing a plugin that provides
an implementation for the "virtual.configure" plugin operation, which is executed during
provisioning a virtual dataset.

Before we start looking at implementations of plugin operations, we have to initialize the
plugin object. Let's say we're writing a plugin for a database called "my_db". We can initialize
the plugin object as such:

  from dlpx.virtualization.platform import plugin

  my_db_plugin = plugin.Plugin()

Now, a plugin writer should write an implementation of their "virtual.configure" operation and
decorate the implementation method with a corresponding decorator. The decorator's name must
start with the name of the plugin object as assigned in the statement above:

  @my_db_plugin.virtual.configure()
  def my_configure_implementation(source, repository, snapshot):
    do_something()
    ...
    ## The rest of the implementation.
    return

Let's walk through what happens when invoke "@my_db_plugin.virtual.configure()":

1. my_db_plugin.virtual.configure() function is called. This function allows to pass arguments
   to a decorator. The "self" argument is automatically provided on an object method, hence we
   don't have to pass any arguments.
2. configure_decorator function takes my_configure_implementation function as an input and it saves
   a handle to the implementation on the VirtualOperations object under configure_impl property. Then,
   configure_decorator returns my_configure_implementation to make sure that we preserve the signature
   and metadata of the original implementation function.
3. configure_wrapper(configure_request) is a function that corresponds to the Virtualization
   Platform API  (see platform.proto) and it accepts a protobuf message as input argument,
   and it returns another protobuf message. This function is invoked by the Dynamic Data Platform
   runtime. For the details on the semantics of those protobuf message, see the section below
   entitled "Virtualization Platform API wrappers".
4. configure_wrapper unpacks the received configure_request protobuf message to provide input
   arguments to self.configure_impl method (which points to my_configure_implementation). Then,
   self.configure_impl is invoked with the input arguments.
5. self.configure_impl returns a config object that we pack into a protobuf message response
   and return it. The response will be sent back to the Dynamic Data Platform runtime.

Virtualization Platform API wrappers

The wrappers are the implementation of the Virtualization Platform API. They take
<OperationName>Request protobuf message as input and return <OperationName>Response,
e.g. ConfigureRequest and ConfigureResponse. The wrappers are called by the Dynamic Data Platform
runtime and their role is to unpack input *Request protobuf message, delegate to the user defined
method that has logic for the virtualization operation itself (such as configure), and craft
a response object.
"""

from dlpx.virtualization import common_pb2
from dlpx.virtualization import platform_pb2


## TODO to be implemented
class DiscoveryOperations(object):

    def __init__(self):
        pass

## TODO to be implemented
class LinkedOperations(object):

    def __init__(self):
        pass

## TODO to be implemented
class VirtualOperations(object):

    def __init__(self):
        self.configure_impl = None

    def configure(self):
        def configure_decorator(configure_impl):
            if self.configure_impl is not None:
                raise RuntimeError("An implementation for virtual.configure() operation has"
                                   "already been defined.")
            self.configure_impl = configure_impl
            return configure_impl
        return configure_decorator

    def _internal_configure(self, configure_request):
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
          ConfigureResponse: A response containing the return value of the
          configure operation, as a ConfigureResult.
        """

        config = self.configure_impl(
            source=configure_request.source,
            repository=configure_request.repository,
            snapshot=configure_request.snapshot)
        configure_response = platform_pb2.ConfigureResponse()
        configure_response.return_value.source_config.parameters.json = config.to_json()
        return configure_response

class Plugin(object):

  @property
  def discovery(self):
    return self.__discovery

  @property
  def linked(self):
      return self.__linked

  @property
  def virtual(self):
      return self.__virtual

  def __init__(self):
    self.__discovery = DiscoveryOperations()
    self.__linked = LinkedOperations()
    self.__virtual = VirtualOperations()



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
