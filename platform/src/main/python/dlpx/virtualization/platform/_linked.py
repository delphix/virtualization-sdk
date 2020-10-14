#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

# -*- coding: utf-8 -*-
"""LinkedOperations for the Virtualization Platform

"""
import json

from dlpx.virtualization.api import common_pb2, platform_pb2
from dlpx.virtualization.common import RemoteConnection, RemoteEnvironment
from dlpx.virtualization.common.exceptions import PluginRuntimeError
from dlpx.virtualization.platform import (DirectSource, Mount,
                                          MountSpecification, StagedSource,
                                          Status)
from dlpx.virtualization.platform import validation_util as v
from dlpx.virtualization.platform.exceptions import (
    IncorrectReturnTypeError, OperationAlreadyDefinedError,
    OperationNotDefinedError)
from dlpx.virtualization.platform.operation import Operation as Op

__all__ = ['LinkedOperations']


class LinkedOperations(object):
    def __init__(self):
        self.pre_snapshot_impl = None
        self.post_snapshot_impl = None
        self.start_staging_impl = None
        self.stop_staging_impl = None
        self.status_impl = None
        self.worker_impl = None
        self.mount_specification_impl = None

    def pre_snapshot(self):
        def pre_snapshot_decorator(pre_snapshot_impl):
            if self.pre_snapshot_impl:
                raise OperationAlreadyDefinedError(Op.LINKED_PRE_SNAPSHOT)
            self.pre_snapshot_impl = v.check_function(pre_snapshot_impl,
                                                      Op.LINKED_PRE_SNAPSHOT)
            return pre_snapshot_impl

        return pre_snapshot_decorator

    def post_snapshot(self):
        def post_snapshot_decorator(post_snapshot_impl):
            if self.post_snapshot_impl:
                raise OperationAlreadyDefinedError(Op.LINKED_POST_SNAPSHOT)
            self.post_snapshot_impl = v.check_function(post_snapshot_impl,
                                                       Op.LINKED_POST_SNAPSHOT)
            return post_snapshot_impl

        return post_snapshot_decorator

    def start_staging(self):
        def start_staging_decorator(start_staging_impl):
            if self.start_staging_impl:
                raise OperationAlreadyDefinedError(Op.LINKED_START_STAGING)
            self.start_staging_impl = v.check_function(start_staging_impl,
                                                       Op.LINKED_START_STAGING)
            return start_staging_impl

        return start_staging_decorator

    def stop_staging(self):
        def stop_staging_decorator(stop_staging_impl):
            if self.stop_staging_impl:
                raise OperationAlreadyDefinedError(Op.LINKED_STOP_STAGING)
            self.stop_staging_impl = v.check_function(stop_staging_impl,
                                                      Op.LINKED_STOP_STAGING)
            return stop_staging_impl

        return stop_staging_decorator

    def status(self):
        def status_decorator(status_impl):
            if self.status_impl:
                raise OperationAlreadyDefinedError(Op.LINKED_STATUS)
            self.status_impl = v.check_function(status_impl, Op.LINKED_STATUS)
            return status_impl

        return status_decorator

    def worker(self):
        def worker_decorator(worker_impl):
            if self.worker_impl:
                raise OperationAlreadyDefinedError(Op.LINKED_WORKER)
            self.worker_impl = v.check_function(worker_impl, Op.LINKED_WORKER)
            return worker_impl

        return worker_decorator

    def mount_specification(self):
        def mount_specification_decorator(mount_specification_impl):
            if self.mount_specification_impl:
                raise OperationAlreadyDefinedError(Op.LINKED_MOUNT_SPEC)
            self.mount_specification_impl = v.check_function(
                mount_specification_impl, Op.LINKED_MOUNT_SPEC)
            return mount_specification_impl

        return mount_specification_decorator

    def _internal_direct_pre_snapshot(self, request):
        """Pre Snapshot Wrapper for direct plugins.

        Executed before creating a snapshot. This plugin
        operation is run prior to creating a snapshot for a direct source.

        Run pre-snapshot operation for a direct source.

        Args:
           request (DirectPreSnapshotRequest): Pre Snapshot arguments.

        Returns:
           DirectPreSnapshotResponse: A response containing
           DirectPreSnapshotResult if successful or PluginErrorResult in case
           of an error.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import RepositoryDefinition
        from generated.definitions import LinkedSourceDefinition
        from generated.definitions import SourceConfigDefinition
        from generated.definitions import SnapshotParametersDefinition

        #
        # While linked.pre_snapshot() is not a required operation, this should
        # not be called if it wasn't implemented.
        #
        if not self.pre_snapshot_impl:
            raise OperationNotDefinedError(Op.LINKED_PRE_SNAPSHOT)

        direct_source_definition = LinkedSourceDefinition.from_dict(
            json.loads(request.direct_source.linked_source.parameters.json))
        direct_source = DirectSource(
            guid=request.direct_source.linked_source.guid,
            connection=RemoteConnection.from_proto(
                request.direct_source.connection),
            parameters=direct_source_definition)

        repository = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))
        source_config = SourceConfigDefinition.from_dict(
            json.loads(request.source_config.parameters.json))
        snap_params = json.loads(request.snapshot_parameters.parameters.json)
        #
        # The snapshot_parameters object should be set to None if the json from
        # the protobuf is None to differentiate no snapshot parameters vs empty
        # snapshot parameters.
        #
        snapshot_parameters = (
            None if snap_params is None else
            SnapshotParametersDefinition.from_dict(snap_params))

        self.pre_snapshot_impl(
            direct_source=direct_source,
            repository=repository,
            source_config=source_config,
            optional_snapshot_parameters=snapshot_parameters)

        direct_pre_snapshot_response = platform_pb2.DirectPreSnapshotResponse()
        direct_pre_snapshot_response.return_value.CopyFrom(
            platform_pb2.DirectPreSnapshotResult())

        return direct_pre_snapshot_response

    def _internal_direct_post_snapshot(self, request):
        """Post Snapshot Wrapper for direct plugins.

        Executed after creating a snapshot. This plugin
        operation is run after creating a snapshot for a direct source.

        Run post-snapshot operation for a direct source.

        Args:
           request (DirectPostSnapshotRequest): Post Snapshot arguments.

        Returns:
           DirectPostSnapshotResponse: A response containing the return value -
           DirectPostSnapshotResult which has the snapshot metadata on success.
           In case of errors, response object will contain PluginErrorResult.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import RepositoryDefinition
        from generated.definitions import LinkedSourceDefinition
        from generated.definitions import SourceConfigDefinition
        from generated.definitions import SnapshotDefinition
        from generated.definitions import SnapshotParametersDefinition

        def to_protobuf(snapshot):
            parameters = common_pb2.PluginDefinedObject()
            parameters.json = json.dumps(snapshot.to_dict())
            snapshot_protobuf = common_pb2.Snapshot()
            snapshot_protobuf.parameters.CopyFrom(parameters)
            return snapshot_protobuf

        if not self.post_snapshot_impl:
            raise OperationNotDefinedError(Op.LINKED_POST_SNAPSHOT)

        direct_source_definition = LinkedSourceDefinition.from_dict(
            json.loads(request.direct_source.linked_source.parameters.json))
        direct_source = DirectSource(
            guid=request.direct_source.linked_source.guid,
            connection=RemoteConnection.from_proto(
                request.direct_source.connection),
            parameters=direct_source_definition)

        repository = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))
        source_config = SourceConfigDefinition.from_dict(
            json.loads(request.source_config.parameters.json))
        snap_params = json.loads(request.snapshot_parameters.parameters.json)
        #
        # The snapshot_parameters object should be set to None if the json from
        # the protobuf is None to differentiate no snapshot parameters vs empty
        # snapshot parameters.
        #
        snapshot_parameters = (
            None if snap_params is None else
            SnapshotParametersDefinition.from_dict(snap_params))

        snapshot = self.post_snapshot_impl(
            direct_source=direct_source,
            repository=repository,
            source_config=source_config,
            optional_snapshot_parameters=snapshot_parameters)

        # Validate that this is a SnapshotDefinition object
        if not isinstance(snapshot, SnapshotDefinition):
            raise IncorrectReturnTypeError(Op.LINKED_POST_SNAPSHOT,
                                           type(snapshot), SnapshotDefinition)

        direct_post_snapshot_response = (
            platform_pb2.DirectPostSnapshotResponse())
        direct_post_snapshot_response.return_value.snapshot.CopyFrom(
            to_protobuf(snapshot))

        return direct_post_snapshot_response

    def _internal_staged_pre_snapshot(self, request):
        """Pre Snapshot Wrapper for staged plugins.

        Executed before creating a snapshot. This plugin
        operation is run prior to creating a snapshot for a staged source.

        Run pre-snapshot operation for a staged source.

        Args:
            request (StagedPreSnapshotRequest): Pre Snapshot arguments.

        Returns:
            StagedPreSnapshotResponse: A response containing
                StagedPreSnapshotResult if successful or PluginErrorResult
                in case of an error.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import RepositoryDefinition
        from generated.definitions import LinkedSourceDefinition
        from generated.definitions import SourceConfigDefinition
        from generated.definitions import SnapshotParametersDefinition

        #
        # While linked.pre_snapshot() is not a required operation, this should
        # not be called if it wasn't implemented.
        #
        if not self.pre_snapshot_impl:
            raise OperationNotDefinedError(Op.LINKED_PRE_SNAPSHOT)

        linked_source = request.staged_source.linked_source
        staged_source_definition = (LinkedSourceDefinition.from_dict(
            json.loads(linked_source.parameters.json)))
        staged_mount = request.staged_source.staged_mount
        mount = Mount(remote_environment=RemoteEnvironment.from_proto(
            staged_mount.remote_environment),
                      mount_path=staged_mount.mount_path,
                      shared_path=staged_mount.shared_path)
        staged_source = StagedSource(
            guid=linked_source.guid,
            source_connection=RemoteConnection.from_proto(
                request.staged_source.source_connection),
            parameters=staged_source_definition,
            mount=mount,
            staged_connection=RemoteConnection.from_proto(
                request.staged_source.staged_connection))

        repository = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))
        source_config = SourceConfigDefinition.from_dict(
            json.loads(request.source_config.parameters.json))
        snap_params = json.loads(request.snapshot_parameters.parameters.json)
        #
        # The snapshot_parameters object should be set to None if the json from
        # the protobuf is None to differentiate no snapshot parameters vs empty
        # snapshot parameters.
        #
        snapshot_parameters = (
            None if snap_params is None else
            SnapshotParametersDefinition.from_dict(snap_params))

        self.pre_snapshot_impl(
            staged_source=staged_source,
            repository=repository,
            source_config=source_config,
            optional_snapshot_parameters=snapshot_parameters)

        response = platform_pb2.StagedPreSnapshotResponse()
        response.return_value.CopyFrom(platform_pb2.StagedPreSnapshotResult())

        return response

    def _internal_staged_post_snapshot(self, request):
        """Post Snapshot Wrapper for staged plugins.

        Executed after creating a snapshot. This plugin
        operation is run after creating a snapshot for a staged source.

        Run post-snapshot operation for a staged source.

        Args:
           request (StagedPostSnapshotRequest): Post Snapshot arguments.

        Returns:
            StagedPostSnapshotResponse: A response containing the return value
                StagedPostSnapshotResult which has the snapshot metadata on
                success. In case of errors, response object will contain
                PluginErrorResult.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import RepositoryDefinition
        from generated.definitions import LinkedSourceDefinition
        from generated.definitions import SourceConfigDefinition
        from generated.definitions import SnapshotDefinition
        from generated.definitions import SnapshotParametersDefinition

        def to_protobuf(snapshot):
            parameters = common_pb2.PluginDefinedObject()
            parameters.json = json.dumps(snapshot.to_dict())
            snapshot_protobuf = common_pb2.Snapshot()
            snapshot_protobuf.parameters.CopyFrom(parameters)
            return snapshot_protobuf

        if not self.post_snapshot_impl:
            raise OperationNotDefinedError(Op.LINKED_POST_SNAPSHOT)

        staged_source_definition = LinkedSourceDefinition.from_dict(
            json.loads(request.staged_source.linked_source.parameters.json))
        mount = Mount(
            remote_environment=RemoteEnvironment.from_proto(
                request.staged_source.staged_mount.remote_environment),
            mount_path=request.staged_source.staged_mount.mount_path,
            shared_path=request.staged_source.staged_mount.shared_path)
        staged_source = StagedSource(
            guid=request.staged_source.linked_source.guid,
            source_connection=RemoteConnection.from_proto(
                request.staged_source.source_connection),
            parameters=staged_source_definition,
            mount=mount,
            staged_connection=RemoteConnection.from_proto(
                request.staged_source.staged_connection))

        repository = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))
        source_config = SourceConfigDefinition.from_dict(
            json.loads(request.source_config.parameters.json))
        snap_params = json.loads(request.snapshot_parameters.parameters.json)
        #
        # The snapshot_parameters object should be set to None if the json from
        # the protobuf is None to differentiate no snapshot parameters vs empty
        # snapshot parameters.
        #
        snapshot_parameters = (
            None if snap_params is None else
            SnapshotParametersDefinition.from_dict(snap_params))

        snapshot = self.post_snapshot_impl(
            staged_source=staged_source,
            repository=repository,
            source_config=source_config,
            optional_snapshot_parameters=snapshot_parameters)

        # Validate that this is a SnapshotDefinition object
        if not isinstance(snapshot, SnapshotDefinition):
            raise IncorrectReturnTypeError(Op.LINKED_POST_SNAPSHOT,
                                           type(snapshot), SnapshotDefinition)

        response = platform_pb2.StagedPostSnapshotResponse()
        response.return_value.snapshot.CopyFrom(to_protobuf(snapshot))

        return response

    def _internal_start_staging(self, request):
        """Start staging Wrapper for staged plugins.

        Executed when enabling the staging source. This plugin
        operation is run to start the staging source as part
        of the enable operation.

        Run start operation for a staged source.

        Args:
           request (StartStagingRequest): Start arguments.

        Returns:
           StartStagingResponse: A response containing StartStagingResult
           if successful or PluginErrorResult in case of an error.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import RepositoryDefinition
        from generated.definitions import LinkedSourceDefinition
        from generated.definitions import SourceConfigDefinition

        #
        # While linked.start_staging() is not a required operation, this should
        # not be called if it wasn't implemented.
        #
        if not self.start_staging_impl:
            raise OperationNotDefinedError(Op.LINKED_START_STAGING)

        staged_source_definition = LinkedSourceDefinition.from_dict(
            json.loads(request.staged_source.linked_source.parameters.json))
        mount = Mount(
            remote_environment=(RemoteEnvironment.from_proto(
                request.staged_source.staged_mount.remote_environment)),
            mount_path=request.staged_source.staged_mount.mount_path,
            shared_path=request.staged_source.staged_mount.shared_path)
        staged_source = StagedSource(
            guid=request.staged_source.linked_source.guid,
            source_connection=RemoteConnection.from_proto(
                request.staged_source.source_connection),
            parameters=staged_source_definition,
            mount=mount,
            staged_connection=RemoteConnection.from_proto(
                request.staged_source.staged_connection))

        repository = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))
        source_config = SourceConfigDefinition.from_dict(
            json.loads(request.source_config.parameters.json))

        self.start_staging_impl(staged_source=staged_source,
                                repository=repository,
                                source_config=source_config)

        start_staging_response = platform_pb2.StartStagingResponse()
        start_staging_response.return_value.CopyFrom(
            platform_pb2.StartStagingResult())

        return start_staging_response

    def _internal_stop_staging(self, request):
        """Stop staging Wrapper for staged plugins.

        Executed when disabling the staging source. This plugin
        operation is run to stop the staging source as part
        of the disable operation.

        Run stop operation for a staged source.

        Args:
           request (StopStagingRequest): Stop arguments.

        Returns:
           StopStagingResponse: A response containing StopStagingResult
           if successful or PluginErrorResult in case of an error.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import RepositoryDefinition
        from generated.definitions import LinkedSourceDefinition
        from generated.definitions import SourceConfigDefinition

        #
        # While linked.stop_staging() is not a required operation, this should
        # not be called if it wasn't implemented.
        #
        if not self.stop_staging_impl:
            raise OperationNotDefinedError(Op.LINKED_STOP_STAGING)

        staged_source_definition = LinkedSourceDefinition.from_dict(
            json.loads(request.staged_source.linked_source.parameters.json))
        mount = Mount(
            remote_environment=(RemoteEnvironment.from_proto(
                request.staged_source.staged_mount.remote_environment)),
            mount_path=request.staged_source.staged_mount.mount_path,
            shared_path=request.staged_source.staged_mount.shared_path)
        staged_source = StagedSource(
            guid=request.staged_source.linked_source.guid,
            source_connection=RemoteConnection.from_proto(
                request.staged_source.source_connection),
            parameters=staged_source_definition,
            mount=mount,
            staged_connection=RemoteConnection.from_proto(
                request.staged_source.staged_connection))

        repository = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))
        source_config = SourceConfigDefinition.from_dict(
            json.loads(request.source_config.parameters.json))

        self.stop_staging_impl(staged_source=staged_source,
                               repository=repository,
                               source_config=source_config)

        stop_staging_response = platform_pb2.StopStagingResponse()
        stop_staging_response.return_value.CopyFrom(
            platform_pb2.StopStagingResult())

        return stop_staging_response

    def _internal_status(self, request):
        """Staged Status Wrapper for staged plugins.

        Executed as part of several operations to get the status
        of a staged source - active or inactive.

        Run status operation for a staged source.

        Args:
           request (StagedStatusRequest): Post Snapshot arguments.

        Returns:
           StagedStatusResponse: A response containing the return value -
           StagedStatusResult which has active or inactive status. In
           case of errors, response object will contain PluginErrorResult.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import RepositoryDefinition
        from generated.definitions import LinkedSourceDefinition
        from generated.definitions import SourceConfigDefinition

        #
        # While linked.status() is not a required operation, this should
        # not be called if it wasn't implemented.
        #
        if not self.status_impl:
            raise OperationNotDefinedError(Op.LINKED_STATUS)

        staged_source_definition = LinkedSourceDefinition.from_dict(
            json.loads(request.staged_source.linked_source.parameters.json))
        mount = Mount(
            remote_environment=(RemoteEnvironment.from_proto(
                request.staged_source.staged_mount.remote_environment)),
            mount_path=request.staged_source.staged_mount.mount_path,
            shared_path=request.staged_source.staged_mount.shared_path)
        staged_source = StagedSource(
            guid=request.staged_source.linked_source.guid,
            source_connection=RemoteConnection.from_proto(
                request.staged_source.source_connection),
            parameters=staged_source_definition,
            mount=mount,
            staged_connection=RemoteConnection.from_proto(
                request.staged_source.staged_connection))

        repository = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))
        source_config = SourceConfigDefinition.from_dict(
            json.loads(request.source_config.parameters.json))

        status = self.status_impl(staged_source=staged_source,
                                  repository=repository,
                                  source_config=source_config)

        # Validate that this is a Status object.
        if not isinstance(status, Status):
            raise IncorrectReturnTypeError(Op.LINKED_STATUS, type(status),
                                           Status)

        staged_status_response = platform_pb2.StagedStatusResponse()
        staged_status_response.return_value.status = status.value

        return staged_status_response

    def _internal_worker(self, request):
        """Staged Worker Wrapper for staged plugins.

        Executed as part of validated sync. This plugin
        operation is run to sync staging source as part
        of the validated sync operation.

        Run worker operation for a staged source.

        Args:
           request (StagedWorkerRequest): Worker arguments.

        Returns:
           StagedWorkerResponse: A response containing StagedWorkerResult
           if successful or PluginErrorResult in case of an error.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import RepositoryDefinition
        from generated.definitions import LinkedSourceDefinition
        from generated.definitions import SourceConfigDefinition

        #
        # While linked.worker() is not a required operation, this should
        # not be called if it wasn't implemented.
        #
        if not self.worker_impl:
            raise OperationNotDefinedError(Op.LINKED_WORKER)

        staged_source_definition = LinkedSourceDefinition.from_dict(
            json.loads(request.staged_source.linked_source.parameters.json))
        mount = Mount(
            remote_environment=(RemoteEnvironment.from_proto(
                request.staged_source.staged_mount.remote_environment)),
            mount_path=request.staged_source.staged_mount.mount_path,
            shared_path=request.staged_source.staged_mount.shared_path)
        staged_source = StagedSource(
            guid=request.staged_source.linked_source.guid,
            source_connection=RemoteConnection.from_proto(
                request.staged_source.source_connection),
            parameters=staged_source_definition,
            mount=mount,
            staged_connection=RemoteConnection.from_proto(
                request.staged_source.staged_connection))

        repository = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))
        source_config = SourceConfigDefinition.from_dict(
            json.loads(request.source_config.parameters.json))

        self.worker_impl(staged_source=staged_source,
                         repository=repository,
                         source_config=source_config)

        staged_worker_response = platform_pb2.StagedWorkerResponse()
        staged_worker_response.return_value.CopyFrom(
            platform_pb2.StagedWorkerResult())

        return staged_worker_response

    def _internal_mount_specification(self, request):
        """Staged Mount/Ownership Spec Wrapper for staged plugins.

        Executed before creating a snapshot during sync or before
        enable/disable. This plugin operation is run before mounting datasets
        on staging to set the mount path and/or ownership.

        Run mount/ownership spec operation for a staged source.

        Args:
           request (StagedMountSpecRequest): Mount Spec arguments.

        Returns:
           StagedMountSpecResponse: A response containing the return value -
           StagedMountSpecResult which has the mount/ownership metadata on
           success. In case of errors, response object will contain
           PluginErrorResult.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import RepositoryDefinition
        from generated.definitions import LinkedSourceDefinition

        def to_protobuf_single_mount(single_mount):
            if single_mount.shared_path:
                raise PluginRuntimeError(
                    'Shared path is not supported for linked sources.')

            single_mount_protobuf = common_pb2.SingleEntireMount()
            single_mount_protobuf.mount_path = single_mount.mount_path
            single_mount_protobuf.remote_environment.CopyFrom(
                single_mount.remote_environment.to_proto())
            return single_mount_protobuf

        def to_protobuf_ownership_spec(ownership_spec):
            ownership_spec_protobuf = common_pb2.OwnershipSpec()
            ownership_spec_protobuf.uid = ownership_spec.uid
            ownership_spec_protobuf.gid = ownership_spec.gid
            return ownership_spec_protobuf

        if not self.mount_specification_impl:
            raise OperationNotDefinedError(Op.LINKED_MOUNT_SPEC)

        staged_source_definition = LinkedSourceDefinition.from_dict(
            json.loads(request.staged_source.linked_source.parameters.json))
        mount = Mount(
            remote_environment=(RemoteEnvironment.from_proto(
                request.staged_source.staged_mount.remote_environment)),
            mount_path=request.staged_source.staged_mount.mount_path,
            shared_path=request.staged_source.staged_mount.shared_path)
        staged_source = StagedSource(
            guid=request.staged_source.linked_source.guid,
            source_connection=RemoteConnection.from_proto(
                request.staged_source.source_connection),
            parameters=staged_source_definition,
            mount=mount,
            staged_connection=RemoteConnection.from_proto(
                request.staged_source.staged_connection))

        repository = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))

        mount_spec = self.mount_specification_impl(staged_source=staged_source,
                                                   repository=repository)

        # Validate that this is a MountSpecification object.
        if not isinstance(mount_spec, MountSpecification):
            raise IncorrectReturnTypeError(Op.LINKED_MOUNT_SPEC,
                                           type(mount_spec),
                                           MountSpecification)

        # Only one mount is supported for linked sources.
        mount_len = len(mount_spec.mounts)
        if mount_len != 1:
            raise PluginRuntimeError(
                'Exactly one mount must be provided for staging sources.'
                ' Found {}'.format(mount_len))

        staged_mount = to_protobuf_single_mount(mount_spec.mounts[0])

        staged_mount_spec_response = platform_pb2.StagedMountSpecResponse()
        staged_mount_spec_response.return_value.staged_mount.CopyFrom(
            staged_mount)

        # Ownership spec is optional for linked sources.
        if mount_spec.ownership_specification:
            ownership_spec = to_protobuf_ownership_spec(
                mount_spec.ownership_specification)
            staged_mount_spec_response.return_value.ownership_spec.CopyFrom(
                ownership_spec)

        return staged_mount_spec_response
