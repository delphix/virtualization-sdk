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

import json
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
        configure_response.return_value.source_config.parameters.json = json.dumps(config.to_dict())
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


def unconfigure_wrapper(unconfigure_request):
    """Unconfigure operation wrapper.

    Executed when disabling or deleting an existing virtual source which has already
    been mounted to a target environment. This plugin operation is run before
    unmounting the virtual source from the target environment.

    Args:
      unconfigure_request (UnconfigureRequest): Unconfigure operation arguments.

    Returns:
      UnconfigureResponse: A response containing UnconfigureResult
       if successful or PluginErrorResult in case of an error.
    """
    unconfigure(
        repository=unconfigure_request.repository,
        source_config=unconfigure_request.source_config,
        virtual_source=unconfigure_request.virtual_source)
    unconfigure_response = platform_pb2.UnconfigureResponse()
    unconfigure_response.return_value.CopyFrom(platform_pb2.UnconfigureResult())
    return unconfigure_response


def reconfigure_wrapper(reconfigure_request):
    """Reconfigure operation wrapper.

    Executed while attaching a VDB during a virtual source enable job and returns
    a virtual source config.

    Args:
      reconfigure_request (ReconfigureRequest): Reconfigure operation arguments.

    Returns:
      ReconfigureResponse: A response containing the return value of the
      reconfigure operation, as a ReconfigureResult.
    """
    config = reconfigure(
        snapshot=reconfigure_request.snapshot,
        source_config=reconfigure_request.source_config,
        virtual_source=reconfigure_request.virtual_source)
    reconfigure_response = platform_pb2.ReconfigureResponse()
    reconfigure_response.return_value.source_config.parameters.json = json.dumps(config.to_dict())
    return reconfigure_response


def start_wrapper(start_request):
    """Start operation wrapper.

    Executed after attaching a VDB during a virtual source enable job to start
    the database.

    Args:
      start_request (StartRequest): Start operation arguments.

    Returns:
      StartResponse: A response containing StartResult if successful or
      PluginErrorResult in case of an error.
    """
    start(
        repository=start_request.repository,
        source_config=start_request.source_config,
        virtual_source=start_request.virtual_source)
    start_response = platform_pb2.StartResponse()
    start_response.return_value.CopyFrom(platform_pb2.StartResult())
    return start_response


def stop_wrapper(stop_request):
    """Stop operation wrapper.

    Executed before unmounting a VDB during a virtual source stop job.

    Args:
      stop_request (StopRequest): Stop operation arguments.

    Returns:
      StopResponse: A response containing StopResult if successful or
      PluginErrorResult in case of an error.
    """
    stop(
        repository=stop_request.repository,
        source_config=stop_request.source_config,
        virtual_source=stop_request.virtual_source)
    stop_response = platform_pb2.StopResponse()
    stop_response.return_value.CopyFrom(platform_pb2.StopResult())
    return stop_response


def virtual_pre_snapshot_wrapper(virtual_pre_snapshot_request):
    """Virtual pre snapshot operation wrapper.

    Executed before creating a ZFS snapshot. This plugin operation is run prior to
    creating a snapshot for a virtual source.

    Run pre-snapshot operation for a virtual source.

    Args:
      virtual_pre_snapshot_request (VirtualPreSnapshotRequest):
      Virtual pre snapshot operation arguments.

    Returns:
      VirtualPreSnapshotResponse: A response containing VirtualPreSnapshotResult
      if successful or PluginErrorResult in case of an error.
    """
    pre_snapshot(
        repository=virtual_pre_snapshot_request.repository,
        source_config=virtual_pre_snapshot_request.source_config,
        virtual_source=virtual_pre_snapshot_request.virtual_source)
    virtual_pre_snapshot_response = platform_pb2.VirtualPreSnapshotResponse()
    virtual_pre_snapshot_response.return_value.CopyFrom(platform_pb2.VirtualPreSnapshotResult())
    return virtual_pre_snapshot_response


def virtual_post_snapshot_wrapper(virtual_post_snapshot_request):
    """Virtual post snapshot operation wrapper.

    Executed after creating a ZFS snapshot. This plugin operation is run after
    creating a snapshot for a virtual source.

    Run post-snapshot operation for a virtual source.

    Args:
      virtual_post_snapshot_request (VirtualPostSnapshotRequest):
      Virtual post snapshot operation arguments.

    Returns:
      VirtualPostSnapshotResponse: A response containing the return value of the
      virtual post snapshot operation, as a VirtualPostSnapshotResult.
    """
    def to_protobuf(snapshot):
        parameters = common_pb2.PluginDefinedObject()
        parameters.json = json.dumps(snapshot.to_dict())
        snapshot_protobuf = common_pb2.Snapshot()
        snapshot_protobuf.parameters.CopyFrom(parameters)
        return snapshot_protobuf

    snapshot = post_snapshot(
        repository=virtual_post_snapshot_request.repository,
        source_config=virtual_post_snapshot_request.source_config,
        virtual_source=virtual_post_snapshot_request.virtual_source)
    virtual_post_snapshot_response = platform_pb2.VirtualPostSnapshotResponse()
    virtual_post_snapshot_response.return_value.snapshot.CopyFrom(to_protobuf(snapshot))
    return virtual_post_snapshot_response


def virtual_status_wrapper(virtual_status_request):
    """Virtual status operation wrapper.

    Executed to get the status of a virtual source - active or inactive.

    Run status operation for a virtual source.

    Args:
      virtual_status_request (VirtualStatusRequest):
      Virtual status operation arguments.

    Returns:
      VirtualStatusResponse: A response containing VirtualStatusResult
      if successful or PluginErrorResult in case of an error.
    """
    virtual_status = status(
        repository=virtual_status_request.repository,
        source_config=virtual_status_request.source_config,
        virtual_source=virtual_status_request.virtual_source)
    virtual_status_response = platform_pb2.VirtualStatusResponse()
    virtual_status_response.return_value.status = virtual_status.value
    return virtual_status_response


def initialize_wrapper(initialize_request):
    """Initialize operation wrapper.

    Executed during VDB creation after mounting onto the target environment.

    Run initialize operation for an empty virtual source.

    Args:
      initialize_request (InitializeRequest):
      Initialize operation arguments.

    Returns:
      InitializeResponse: A response containing InitializeResult
      if successful or PluginErrorResult in case of an error.
    """
    initialize(
        repository=initialize_request.repository,
        source_config=initialize_request.source_config,
        virtual_source=initialize_request.virtual_source)
    initialize_response = platform_pb2.InitializeResponse()
    initialize_response.return_value.CopyFrom(platform_pb2.InitializeResult())
    return initialize_response


def virtual_mount_spec_wrapper(virtual_mount_spec_request):
    """Virtual mount spec operation wrapper.

    Executed to fetch the ownership spec before mounting onto a target environment.

    Run mount spec operation for a virtual source.

    Args:
      virtual_mount_spec_request (VirtualMountSpecRequest):
      Virtual mount spec operation arguments.

    Returns:
      VirtualMountSpecResponse: A response containing the return value of the
      virtual mount spec operation, as a VirtualMountSpecResult.
    """
    def to_protobuf_single_mount(single_mount):
        single_mount_protobuf = common_pb2.SingleSubsetMount()

        host_protobuf = common_pb2.RemoteHost()
        host_protobuf.name = single_mount.remote_environment.host.name
        host_protobuf.reference = single_mount.remote_environment.host.reference
        host_protobuf.binary_path = single_mount.remote_environment.host.binary_path
        host_protobuf.scratch_path = single_mount.remote_environment.host.scratch_path

        environment_protobuf = common_pb2.RemoteEnvironment()
        environment_protobuf.name = single_mount.remote_environment.name
        environment_protobuf.reference = single_mount.remote_environment.reference
        environment_protobuf.host.CopyFrom(host_protobuf)

        single_mount_protobuf.remote_environment.CopyFrom(environment_protobuf)
        single_mount_protobuf.mount_path = single_mount.mount_path
        single_mount_protobuf.shared_path = single_mount.shared_path

        return single_mount_protobuf

    def to_protobuf_ownership_spec(ownership_spec):
        ownership_spec_protobuf = common_pb2.OwnershipSpec()
        ownership_spec_protobuf.uid = ownership_spec.uid
        ownership_spec_protobuf.gid = ownership_spec.gid
        return ownership_spec_protobuf

    virtual_mount_spec = mount_spec(
        repository=virtual_mount_spec_request.repository,
        virtual_source=virtual_mount_spec_request.virtual_source)
    virtual_mount_spec_response = platform_pb2.VirtualMountSpecResponse()
    ownership_spec = to_protobuf_ownership_spec(virtual_mount_spec.ownership_spec)
    virtual_mount_spec_response.return_value.ownership_spec.CopyFrom(ownership_spec)
    mounts_list = [to_protobuf_single_mount(m) for m in virtual_mount_spec.mounts]
    virtual_mount_spec_response.return_value.mounts.extend(mounts_list)
    return virtual_mount_spec_response


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
        parameters.json = json.dumps(repository.to_dict())
        repository_protobuf = common_pb2.Repository()
        repository_protobuf.parameters.CopyFrom(parameters)
        return repository_protobuf

    repositories = repository_discovery(
        source_connection=repository_discovery_request.source_connection)
    repository_discovery_response = platform_pb2.RepositoryDiscoveryResponse()
    repository_protobuf_list = [to_protobuf(repo) for repo in repositories]
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
        parameters.json = json.dumps(source_config.to_dict())
        source_config_protobuf = common_pb2.SourceConfig()
        source_config_protobuf.parameters.CopyFrom(parameters)
        return source_config_protobuf

    source_configs = source_config_discovery(
        source_connection=source_config_discovery_request.source_connection,
        repository=source_config_discovery_request.repository)
    source_config_discovery_response = platform_pb2.SourceConfigDiscoveryResponse()
    source_config_protobuf_list = [to_protobuf(source_config) for source_config in source_configs]
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
        direct_source=direct_pre_snapshot_request.direct_source,
        repository=direct_pre_snapshot_request.repository,
        source_config=direct_pre_snapshot_request.source_config)

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
        parameters.json = json.dumps(snapshot.to_dict())
        snapshot_protobuf = common_pb2.Snapshot()
        snapshot_protobuf.parameters.CopyFrom(parameters)
        return snapshot_protobuf

    snapshot = direct_post_snapshot(
        direct_source=direct_post_snapshot_request.direct_source,
        repository=direct_post_snapshot_request.repository,
        source_config=direct_post_snapshot_request.source_config)

    direct_post_snapshot_response = platform_pb2.DirectPostSnapshotResponse()
    direct_post_snapshot_response.return_value.snapshot.CopyFrom(to_protobuf(snapshot))

    return direct_post_snapshot_response

def staged_pre_snapshot_wrapper(staged_pre_snapshot_request):
    """Pre Snapshot Wrapper for staged plugins.

    Executed before creating a snapshot. This plugin
    operation is run prior to creating a snapshot for a staged source.

    Run pre-snapshot operation for a staged source.

    Args:
       staged_pre_snapshot_request (StagedPreSnapshotRequest):
       Pre Snapshot arguments.

    Returns:
       StagedPreSnapshotResponse: A response containing StagedPreSnapshotResult
       if successful or PluginErrorResult in case of an error.
    """

    staged_pre_snapshot(
        staged_source=staged_pre_snapshot_request.staged_source,
        repository=staged_pre_snapshot_request.repository,
        source_config=staged_pre_snapshot_request.source_config)

    staged_pre_snapshot_response = platform_pb2.StagedPreSnapshotResponse()
    staged_pre_snapshot_response.return_value.CopyFrom(platform_pb2.StagedPreSnapshotResult())

    return staged_pre_snapshot_response


def staged_post_snapshot_wrapper(staged_post_snapshot_request):
    """Post Snapshot Wrapper for staged plugins.

    Executed after creating a snapshot. This plugin
    operation is run after creating a snapshot for a staged source.

    Run post-snapshot operation for a staged source.

    Args:
       staged_post_snapshot_request (StagedPostSnapshotRequest):
       Post Snapshot arguments.

    Returns:
       StagedPostSnapshotResponse: A response containing the return value -
       StagedPostSnapshotResult which has the snapshot metadata on success. In
       case of errors, response object will contain PluginErrorResult.
    """

    def to_protobuf(snapshot):
        parameters = common_pb2.PluginDefinedObject()
        parameters.json = json.dumps(snapshot.to_dict())
        snapshot_protobuf = common_pb2.Snapshot()
        snapshot_protobuf.parameters.CopyFrom(parameters)
        return snapshot_protobuf

    snapshot = staged_post_snapshot(
        staged_source=staged_post_snapshot_request.staged_source,
        repository=staged_post_snapshot_request.repository,
        source_config=staged_post_snapshot_request.source_config)

    staged_post_snapshot_response = platform_pb2.StagedPostSnapshotResponse()
    staged_post_snapshot_response.return_value.snapshot.CopyFrom(to_protobuf(snapshot))

    return staged_post_snapshot_response


def start_staging_wrapper(start_staging_request):
    """Start staging Wrapper for staged plugins.

    Executed when enabling the staging source. This plugin
    operation is run to start the staging source as part
    of the enable operation.

    Run start operation for a staged source.

    Args:
       start_staging_request (StartStagingRequest):
       Start arguments.

    Returns:
       StartStagingResponse: A response containing StartStagingResult
       if successful or PluginErrorResult in case of an error.
    """

    start_staging(
        staged_source=start_staging_request.staged_source,
        repository=start_staging_request.repository,
        source_config=start_staging_request.source_config)

    start_staging_response = platform_pb2.StartStagingResponse()
    start_staging_response.return_value.CopyFrom(platform_pb2.StartStagingResult())

    return start_staging_response


def stop_staging_wrapper(stop_staging_request):
    """Stop staging Wrapper for staged plugins.

    Executed when disabling the staging source. This plugin
    operation is run to stop the staging source as part
    of the disable operation.

    Run stop operation for a staged source.

    Args:
       stop_staging_request (StopStagingRequest):
       Stop arguments.

    Returns:
       StopStagingResponse: A response containing StopStagingResult
       if successful or PluginErrorResult in case of an error.
    """

    stop_staging(
        staged_source=stop_staging_request.staged_source,
        repository=stop_staging_request.repository,
        source_config=stop_staging_request.source_config)

    stop_staging_response = platform_pb2.StopStagingResponse()
    stop_staging_response.return_value.CopyFrom(platform_pb2.StopStagingResult())

    return stop_staging_response


def staged_status_wrapper(staged_status_request):
    """Staged Status Wrapper for staged plugins.

    Executed as part of several operations to get the status
    of a staged source - active or inactive.

    Run status operation for a staged source.

    Args:
       staged_status_request (StagedStatusRequest):
       Post Snapshot arguments.

    Returns:
       StagedStatusResponse: A response containing the return value -
       StagedStatusResult which has active or inactive status. In
       case of errors, response object will contain PluginErrorResult.
    """

    status = staged_status(
        staged_source=staged_status_request.staged_source,
        repository=staged_status_request.repository,
        source_config=staged_status_request.source_config)

    staged_status_response = platform_pb2.StagedStatusResponse()
    staged_status_response.return_value.status = status.value

    return staged_status_response


def staged_worker_wrapper(staged_worker_request):
    """Staged Worker Wrapper for staged plugins.

    Executed as part of validated sync. This plugin
    operation is run to sync staging source as part
    of the validated sync operation.

    Run worker operation for a staged source.

    Args:
       staged_worker_request (StagedWorkerRequest):
       Worker arguments.

    Returns:
       StagedWorkerResponse: A response containing StagedWorkerResult
       if successful or PluginErrorResult in case of an error.
    """

    staged_worker(
        staged_source=staged_worker_request.staged_source,
        repository=staged_worker_request.repository,
        source_config=staged_worker_request.source_config)

    staged_worker_response = platform_pb2.StagedWorkerResponse()
    staged_worker_response.return_value.CopyFrom(platform_pb2.StagedWorkerResult())

    return staged_worker_response


def staged_mount_spec_wrapper(staged_mount_spec_request):
    """Staged Mount/Ownership Spec Wrapper for staged plugins.

    Executed before creating a snapshot during sync or before enable/disable.
    This plugin operation is run before mounting datasets on staging to set
    the mount path and/or ownership.

    Run mount/ownership spec operation for a staged source.

    Args:
       staged_mount_spec_request (StagedMountSpecRequest):
       Mount Spec arguments.

    Returns:
       StagedMountSpecResponse: A response containing the return value -
       StagedMountSpecResult which has the mount/ownership metadata on success.
       In case of errors, response object will contain PluginErrorResult.
    """

    def to_protobuf_single_mount(single_mount):
        single_mount_protobuf = common_pb2.SingleEntireMount()

        host_protobuf = common_pb2.RemoteHost()
        host_protobuf.name = single_mount.remote_environment.host.name
        host_protobuf.reference = single_mount.remote_environment.host.reference
        host_protobuf.binary_path = single_mount.remote_environment.host.binary_path
        host_protobuf.scratch_path = single_mount.remote_environment.host.scratch_path

        environment_protobuf = common_pb2.RemoteEnvironment()
        environment_protobuf.name = single_mount.remote_environment.name
        environment_protobuf.reference = single_mount.remote_environment.reference
        environment_protobuf.host.CopyFrom(host_protobuf)

        single_mount_protobuf.remote_environment.CopyFrom(environment_protobuf)
        single_mount_protobuf.mount_path = single_mount.mount_path

        return single_mount_protobuf

    def to_protobuf_ownership_spec(ownership_spec):
        ownership_spec_protobuf = common_pb2.OwnershipSpec()
        ownership_spec_protobuf.uid = ownership_spec.uid
        ownership_spec_protobuf.gid = ownership_spec.gid
        return ownership_spec_protobuf

    mount_spec = staged_mount_spec(
        staged_source=staged_mount_spec_request.staged_source,
        repository=staged_mount_spec_request.repository)

    staged_mount_spec_response = platform_pb2.StagedMountSpecResponse()
    staged_mount = to_protobuf_single_mount(mount_spec.mounts[0])
    staged_mount_spec_response.return_value.staged_mount.CopyFrom(staged_mount)
    ownership_spec = to_protobuf_ownership_spec(mount_spec.ownership_spec)
    staged_mount_spec_response.return_value.ownership_spec.CopyFrom(ownership_spec)

    return staged_mount_spec_response
