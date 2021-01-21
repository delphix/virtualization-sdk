#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

# -*- coding: utf-8 -*-
"""VirtualOperations for the Virtualization Platform

"""
import json

from dlpx.virtualization.api import common_pb2, platform_pb2
from dlpx.virtualization.common import RemoteConnection, RemoteEnvironment
from dlpx.virtualization.platform import (Mount, MountSpecification, Status,
                                          VirtualSource)
from dlpx.virtualization.platform import validation_util as v
from dlpx.virtualization.platform.exceptions import (
    IncorrectReturnTypeError, OperationAlreadyDefinedError,
    OperationNotDefinedError)
from dlpx.virtualization.platform.operation import Operation as Op

__all__ = ['VirtualOperations']


class VirtualOperations(object):
    def __init__(self):
        self.configure_impl = None
        self.unconfigure_impl = None
        self.reconfigure_impl = None
        self.start_impl = None
        self.stop_impl = None
        self.pre_snapshot_impl = None
        self.post_snapshot_impl = None
        self.status_impl = None
        self.initialize_impl = None
        self.mount_specification_impl = None

    def configure(self):
        def configure_decorator(configure_impl):
            if self.configure_impl:
                raise OperationAlreadyDefinedError(Op.VIRTUAL_CONFIGURE)
            self.configure_impl = v.check_function(configure_impl,
                                                   Op.VIRTUAL_CONFIGURE)
            return configure_impl

        return configure_decorator

    def unconfigure(self):
        def unconfigure_decorator(unconfigure_impl):
            if self.unconfigure_impl:
                raise OperationAlreadyDefinedError(Op.VIRTUAL_UNCONFIGURE)
            self.unconfigure_impl = v.check_function(unconfigure_impl,
                                                     Op.VIRTUAL_UNCONFIGURE)
            return unconfigure_impl

        return unconfigure_decorator

    def reconfigure(self):
        def reconfigure_decorator(reconfigure_impl):
            if self.reconfigure_impl:
                raise OperationAlreadyDefinedError(Op.VIRTUAL_RECONFIGURE)
            self.reconfigure_impl = v.check_function(reconfigure_impl,
                                                     Op.VIRTUAL_RECONFIGURE)
            return reconfigure_impl

        return reconfigure_decorator

    def start(self):
        def start_decorator(start_impl):
            if self.start_impl:
                raise OperationAlreadyDefinedError(Op.VIRTUAL_START)
            self.start_impl = v.check_function(start_impl, Op.VIRTUAL_START)
            return start_impl

        return start_decorator

    def stop(self):
        def stop_decorator(stop_impl):
            if self.stop_impl:
                raise OperationAlreadyDefinedError(Op.VIRTUAL_STOP)
            self.stop_impl = v.check_function(stop_impl, Op.VIRTUAL_STOP)
            return stop_impl

        return stop_decorator

    def pre_snapshot(self):
        def pre_snapshot_decorator(pre_snapshot_impl):
            if self.pre_snapshot_impl:
                raise OperationAlreadyDefinedError(Op.VIRTUAL_PRE_SNAPSHOT)
            self.pre_snapshot_impl = v.check_function(pre_snapshot_impl,
                                                      Op.VIRTUAL_PRE_SNAPSHOT)
            return pre_snapshot_impl

        return pre_snapshot_decorator

    def post_snapshot(self):
        def post_snapshot_decorator(post_snapshot_impl):
            if self.post_snapshot_impl:
                raise OperationAlreadyDefinedError(Op.VIRTUAL_POST_SNAPSHOT)
            self.post_snapshot_impl = v.check_function(
                post_snapshot_impl, Op.VIRTUAL_POST_SNAPSHOT)
            return post_snapshot_impl

        return post_snapshot_decorator

    def status(self):
        def status_decorator(status_impl):
            if self.status_impl:
                raise OperationAlreadyDefinedError(Op.VIRTUAL_STATUS)
            self.status_impl = v.check_function(status_impl, Op.VIRTUAL_STATUS)
            return status_impl

        return status_decorator

    def initialize(self):
        def initialize_decorator(initialize_impl):
            if self.initialize_impl:
                raise OperationAlreadyDefinedError(Op.VIRTUAL_INITIALIZE)
            self.initialize_impl = v.check_function(initialize_impl,
                                                    Op.VIRTUAL_INITIALIZE)
            return initialize_impl

        return initialize_decorator

    def mount_specification(self):
        def mount_specification_decorator(mount_specification_impl):
            if self.mount_specification_impl:
                raise OperationAlreadyDefinedError(Op.VIRTUAL_MOUNT_SPEC)
            self.mount_specification_impl = v.check_function(
                mount_specification_impl, Op.VIRTUAL_MOUNT_SPEC)
            return mount_specification_impl

        return mount_specification_decorator

    @staticmethod
    def _from_protobuf_single_subset_mount(single_subset_mount):
        return Mount(remote_environment=RemoteEnvironment.from_proto(
            single_subset_mount.remote_environment),
                     mount_path=single_subset_mount.mount_path,
                     shared_path=single_subset_mount.shared_path)

    def _internal_configure(self, request):
        """Configure operation wrapper.

        Executed just after cloning the captured data and mounting it to a
        target environment. Specifically, this plugin operation is run during
        provision and refresh, prior to taking the initial snapshot of the
        clone. This plugin operation is run before the user-customizable
        Configure Clone and Before Refresh operations are run. It must return
        a sourceConfig object that represents the new dataset.

        Configure the data to be usable on the target environment. For database
        data files, this may mean recovering from a crash consistent format or
        backup. For application files, this may mean reconfiguring XML files or
        rewriting hostnames and symlinks.

        Args:
          request (ConfigureRequest): Configure operation arguments.

        Returns:
          ConfigureResponse: A response containing the return value of the
          configure operation, as a ConfigureResult.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import VirtualSourceDefinition
        from generated.definitions import RepositoryDefinition
        from generated.definitions import SnapshotDefinition
        from generated.definitions import SourceConfigDefinition

        if not self.configure_impl:
            raise OperationNotDefinedError(Op.VIRTUAL_CONFIGURE)

        virtual_source_definition = VirtualSourceDefinition.from_dict(
            json.loads(request.virtual_source.parameters.json))
        mounts = [
            VirtualOperations._from_protobuf_single_subset_mount(m)
            for m in request.virtual_source.mounts
        ]

        virtual_source = VirtualSource(guid=request.virtual_source.guid,
                                       connection=RemoteConnection.from_proto(
                                           request.virtual_source.connection),
                                       parameters=virtual_source_definition,
                                       mounts=mounts)

        repository = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))
        snapshot = SnapshotDefinition.from_dict(
            json.loads(request.snapshot.parameters.json))

        config = self.configure_impl(virtual_source=virtual_source,
                                     repository=repository,
                                     snapshot=snapshot)

        # Validate that this is a SourceConfigDefinition object.
        if not isinstance(config, SourceConfigDefinition):
            raise IncorrectReturnTypeError(Op.VIRTUAL_CONFIGURE, type(config),
                                           SourceConfigDefinition)

        configure_response = platform_pb2.ConfigureResponse()
        configure_response.return_value.source_config.parameters.json = (
            json.dumps(config.to_dict()))
        return configure_response

    def _internal_unconfigure(self, request):
        """Unconfigure operation wrapper.

        Executed when disabling or deleting an existing virtual source which
        has already been mounted to a target environment. This plugin operation
        is run before unmounting the virtual source from the target
        environment.

        Args:
          request (UnconfigureRequest): Unconfigure operation arguments.

        Returns:
          UnconfigureResponse: A response containing UnconfigureResult
           if successful or PluginErrorResult in case of an error.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import VirtualSourceDefinition
        from generated.definitions import RepositoryDefinition
        from generated.definitions import SourceConfigDefinition

        #
        # While virtual.unconfigure() is not a required operation, this should
        # not be called if it wasn't implemented.
        #
        if not self.unconfigure_impl:
            raise OperationNotDefinedError(Op.VIRTUAL_UNCONFIGURE)

        virtual_source_definition = VirtualSourceDefinition.from_dict(
            json.loads(request.virtual_source.parameters.json))
        mounts = [
            VirtualOperations._from_protobuf_single_subset_mount(m)
            for m in request.virtual_source.mounts
        ]

        virtual_source = VirtualSource(guid=request.virtual_source.guid,
                                       connection=RemoteConnection.from_proto(
                                           request.virtual_source.connection),
                                       parameters=virtual_source_definition,
                                       mounts=mounts)

        repository = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))
        source_config = SourceConfigDefinition.from_dict(
            json.loads(request.source_config.parameters.json))

        self.unconfigure_impl(repository=repository,
                              source_config=source_config,
                              virtual_source=virtual_source)

        unconfigure_response = platform_pb2.UnconfigureResponse()
        unconfigure_response.return_value.CopyFrom(
            platform_pb2.UnconfigureResult())
        return unconfigure_response

    def _internal_reconfigure(self, request):
        """Reconfigure operation wrapper.

        Executed while attaching a VDB during a virtual source enable job and
        returns a virtual source config.

        Args:
          request (ReconfigureRequest): Reconfigure operation arguments.

        Returns:
          ReconfigureResponse: A response containing the return value of the
          reconfigure operation, as a ReconfigureResult.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import VirtualSourceDefinition
        from generated.definitions import SnapshotDefinition
        from generated.definitions import SourceConfigDefinition
        from generated.definitions import RepositoryDefinition

        if not self.reconfigure_impl:
            raise OperationNotDefinedError(Op.VIRTUAL_RECONFIGURE)

        virtual_source_definition = VirtualSourceDefinition.from_dict(
            json.loads(request.virtual_source.parameters.json))
        mounts = [
            VirtualOperations._from_protobuf_single_subset_mount(m)
            for m in request.virtual_source.mounts
        ]
        virtual_source = VirtualSource(guid=request.virtual_source.guid,
                                       connection=RemoteConnection.from_proto(
                                           request.virtual_source.connection),
                                       parameters=virtual_source_definition,
                                       mounts=mounts)

        snapshot = SnapshotDefinition.from_dict(
            json.loads(request.snapshot.parameters.json))
        source_config = SourceConfigDefinition.from_dict(
            json.loads(request.source_config.parameters.json))
        repository = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))

        config = self.reconfigure_impl(snapshot=snapshot,
                                       repository=repository,
                                       source_config=source_config,
                                       virtual_source=virtual_source)

        # Validate that this is a SourceConfigDefinition object.
        if not isinstance(config, SourceConfigDefinition):
            raise IncorrectReturnTypeError(Op.VIRTUAL_RECONFIGURE,
                                           type(config),
                                           SourceConfigDefinition)

        reconfigure_response = platform_pb2.ReconfigureResponse()
        reconfigure_response.return_value.source_config.parameters.json = (
            json.dumps(config.to_dict()))
        return reconfigure_response

    def _internal_start(self, request):
        """Start operation wrapper.

        Executed after attaching a VDB during a virtual source enable job to
        start the database.

        Args:
          request (StartRequest): Start operation arguments.

        Returns:
          StartResponse: A response containing StartResult if successful or
          PluginErrorResult in case of an error.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import VirtualSourceDefinition
        from generated.definitions import RepositoryDefinition
        from generated.definitions import SourceConfigDefinition

        #
        # While virtual.start() is not a required operation, this should
        # not be called if it wasn't implemented.
        #
        if not self.start_impl:
            raise OperationNotDefinedError(Op.VIRTUAL_START)

        virtual_source_definition = VirtualSourceDefinition.from_dict(
            json.loads(request.virtual_source.parameters.json))
        mounts = [
            VirtualOperations._from_protobuf_single_subset_mount(m)
            for m in request.virtual_source.mounts
        ]
        virtual_source = VirtualSource(guid=request.virtual_source.guid,
                                       connection=RemoteConnection.from_proto(
                                           request.virtual_source.connection),
                                       parameters=virtual_source_definition,
                                       mounts=mounts)

        repository = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))
        source_config = SourceConfigDefinition.from_dict(
            json.loads(request.source_config.parameters.json))

        self.start_impl(repository=repository,
                        source_config=source_config,
                        virtual_source=virtual_source)

        start_response = platform_pb2.StartResponse()
        start_response.return_value.CopyFrom(platform_pb2.StartResult())
        return start_response

    def _internal_stop(self, request):
        """Stop operation wrapper.

        Executed before unmounting a VDB during a virtual source stop job.

        Args:
          request (StopRequest): Stop operation arguments.

        Returns:
          StopResponse: A response containing StopResult if successful or
          PluginErrorResult in case of an error.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import VirtualSourceDefinition
        from generated.definitions import RepositoryDefinition
        from generated.definitions import SourceConfigDefinition

        #
        # While virtual.stop() is not a required operation, this should
        # not be called if it wasn't implemented.
        #
        if not self.stop_impl:
            raise OperationNotDefinedError(Op.VIRTUAL_STOP)

        virtual_source_definition = VirtualSourceDefinition.from_dict(
            json.loads(request.virtual_source.parameters.json))
        mounts = [
            VirtualOperations._from_protobuf_single_subset_mount(m)
            for m in request.virtual_source.mounts
        ]
        virtual_source = VirtualSource(guid=request.virtual_source.guid,
                                       connection=RemoteConnection.from_proto(
                                           request.virtual_source.connection),
                                       parameters=virtual_source_definition,
                                       mounts=mounts)

        repository = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))
        source_config = SourceConfigDefinition.from_dict(
            json.loads(request.source_config.parameters.json))

        self.stop_impl(repository=repository,
                       source_config=source_config,
                       virtual_source=virtual_source)

        stop_response = platform_pb2.StopResponse()
        stop_response.return_value.CopyFrom(platform_pb2.StopResult())
        return stop_response

    def _internal_pre_snapshot(self, request):
        """Virtual pre snapshot operation wrapper.

        Executed before creating a ZFS snapshot. This plugin operation is run
        prior to creating a snapshot for a virtual source.

        Run pre-snapshot operation for a virtual source.

        Args:
          virtual_pre_snapshot_request (VirtualPreSnapshotRequest):
          Virtual pre snapshot operation arguments.

        Returns:
          VirtualPreSnapshotResponse: A response containing
          VirtualPreSnapshotResult if successful or PluginErrorResult in case
          of an error.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import VirtualSourceDefinition
        from generated.definitions import RepositoryDefinition
        from generated.definitions import SourceConfigDefinition

        #
        # While virtual.pre_snapshot() is not a required operation, this should
        # not be called if it wasn't implemented.
        #
        if not self.pre_snapshot_impl:
            raise OperationNotDefinedError(Op.VIRTUAL_PRE_SNAPSHOT)

        virtual_source_definition = VirtualSourceDefinition.from_dict(
            json.loads(request.virtual_source.parameters.json))
        mounts = [
            VirtualOperations._from_protobuf_single_subset_mount(m)
            for m in request.virtual_source.mounts
        ]
        virtual_source = VirtualSource(guid=request.virtual_source.guid,
                                       connection=RemoteConnection.from_proto(
                                           request.virtual_source.connection),
                                       parameters=virtual_source_definition,
                                       mounts=mounts)

        repository = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))
        source_config = SourceConfigDefinition.from_dict(
            json.loads(request.source_config.parameters.json))

        self.pre_snapshot_impl(repository=repository,
                               source_config=source_config,
                               virtual_source=virtual_source)

        virtual_pre_snapshot_response = (
            platform_pb2.VirtualPreSnapshotResponse())
        virtual_pre_snapshot_response.return_value.CopyFrom(
            platform_pb2.VirtualPreSnapshotResult())
        return virtual_pre_snapshot_response

    def _internal_post_snapshot(self, request):
        """Virtual post snapshot operation wrapper.

        Executed after creating a ZFS snapshot. This plugin operation is run
        after creating a snapshot for a virtual source.

        Run post-snapshot operation for a virtual source.

        Args:
          request (VirtualPostSnapshotRequest): Virtual post snapshot operation
          arguments.

        Returns:
          VirtualPostSnapshotResponse: A response containing the return value
          of the virtual post snapshot operation, as a
          VirtualPostSnapshotResult.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import VirtualSourceDefinition
        from generated.definitions import RepositoryDefinition
        from generated.definitions import SnapshotDefinition
        from generated.definitions import SourceConfigDefinition

        def to_protobuf(snapshot):
            parameters = common_pb2.PluginDefinedObject()
            parameters.json = json.dumps(snapshot.to_dict())
            snapshot_protobuf = common_pb2.Snapshot()
            snapshot_protobuf.parameters.CopyFrom(parameters)
            return snapshot_protobuf

        if not self.post_snapshot_impl:
            raise OperationNotDefinedError(Op.VIRTUAL_POST_SNAPSHOT)

        virtual_source_definition = VirtualSourceDefinition.from_dict(
            json.loads(request.virtual_source.parameters.json))
        mounts = [
            VirtualOperations._from_protobuf_single_subset_mount(m)
            for m in request.virtual_source.mounts
        ]
        virtual_source = VirtualSource(guid=request.virtual_source.guid,
                                       connection=RemoteConnection.from_proto(
                                           request.virtual_source.connection),
                                       parameters=virtual_source_definition,
                                       mounts=mounts)

        repository = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))
        source_config = SourceConfigDefinition.from_dict(
            json.loads(request.source_config.parameters.json))

        snapshot = self.post_snapshot_impl(repository=repository,
                                           source_config=source_config,
                                           virtual_source=virtual_source)

        # Validate that this is a SnapshotDefinition object
        if not isinstance(snapshot, SnapshotDefinition):
            raise IncorrectReturnTypeError(Op.VIRTUAL_POST_SNAPSHOT,
                                           type(snapshot), SnapshotDefinition)

        virtual_post_snapshot_response = (
            platform_pb2.VirtualPostSnapshotResponse())
        virtual_post_snapshot_response.return_value.snapshot.CopyFrom(
            to_protobuf(snapshot))
        return virtual_post_snapshot_response

    def _internal_status(self, request):
        """Virtual status operation wrapper.

        Executed to get the status of a virtual source - active or inactive.

        Run status operation for a virtual source.

        Args:
          request (VirtualStatusRequest):
          Virtual status operation arguments.

        Returns:
          VirtualStatusResponse: A response containing VirtualStatusResult
          if successful or PluginErrorResult in case of an error.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import VirtualSourceDefinition
        from generated.definitions import RepositoryDefinition
        from generated.definitions import SourceConfigDefinition

        #
        # While virtual.status() is not a required operation, this should
        # not be called if it wasn't implemented.
        #
        if not self.status_impl:
            raise OperationNotDefinedError(Op.VIRTUAL_STATUS)

        virtual_source_definition = VirtualSourceDefinition.from_dict(
            json.loads(request.virtual_source.parameters.json))
        mounts = [
            VirtualOperations._from_protobuf_single_subset_mount(m)
            for m in request.virtual_source.mounts
        ]
        virtual_source = VirtualSource(guid=request.virtual_source.guid,
                                       connection=RemoteConnection.from_proto(
                                           request.virtual_source.connection),
                                       parameters=virtual_source_definition,
                                       mounts=mounts)

        repository = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))
        source_config = SourceConfigDefinition.from_dict(
            json.loads(request.source_config.parameters.json))

        virtual_status = self.status_impl(repository=repository,
                                          source_config=source_config,
                                          virtual_source=virtual_source)

        # Validate that this is a Status object.
        if not isinstance(virtual_status, Status):
            raise IncorrectReturnTypeError(Op.VIRTUAL_STATUS,
                                           type(virtual_status), Status)

        virtual_status_response = platform_pb2.VirtualStatusResponse()
        virtual_status_response.return_value.status = virtual_status.value
        return virtual_status_response

    def _internal_initialize(self, request):
        """Initialize operation wrapper.

        Executed during VDB creation after mounting onto the target
        environment.

        Run initialize operation for an empty virtual source.

        Args:
          request (InitializeRequest): Initialize operation arguments.

        Returns:
          InitializeResponse: A response containing InitializeResult
          if successful or PluginErrorResult in case of an error.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import VirtualSourceDefinition
        from generated.definitions import RepositoryDefinition
        from generated.definitions import SourceConfigDefinition

        if not self.initialize_impl:
            raise OperationNotDefinedError(Op.VIRTUAL_INITIALIZE)

        virtual_source_definition = VirtualSourceDefinition.from_dict(
            json.loads(request.virtual_source.parameters.json))
        mounts = [
            VirtualOperations._from_protobuf_single_subset_mount(m)
            for m in request.virtual_source.mounts
        ]
        virtual_source = VirtualSource(guid=request.virtual_source.guid,
                                       connection=RemoteConnection.from_proto(
                                           request.virtual_source.connection),
                                       parameters=virtual_source_definition,
                                       mounts=mounts)

        repository = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))

        config = self.initialize_impl(repository=repository,
                             virtual_source=virtual_source)

        # Validate that this is a SourceConfigDefinition object.
        if not isinstance(config, SourceConfigDefinition):
            raise IncorrectReturnTypeError(Op.VIRTUAL_INITIALIZE, type(config),
                                           SourceConfigDefinition)

        initialize_response = platform_pb2.InitializeResponse()
        initialize_response.return_value.source_config.parameters.json = (
            json.dumps(config.to_dict()))
        return initialize_response

    def _internal_mount_specification(self, request):
        """Virtual mount spec operation wrapper.

        Executed to fetch the ownership spec before mounting onto a target
        environment.

        Run mount spec operation for a virtual source.

        Args:
          virtual_mount_spec_request (VirtualMountSpecRequest):
          Virtual mount spec operation arguments.

        Returns:
          VirtualMountSpecResponse: A response containing the return value of
          the virtual mount spec operation, as a VirtualMountSpecResult.
        """
        # Reasoning for method imports are in this file's docstring.
        from generated.definitions import VirtualSourceDefinition
        from generated.definitions import RepositoryDefinition

        def to_protobuf_single_mount(single_mount):
            single_mount_protobuf = common_pb2.SingleSubsetMount()

            environment_protobuf = single_mount.remote_environment.to_proto()

            single_mount_protobuf.remote_environment.CopyFrom(
                environment_protobuf)
            single_mount_protobuf.mount_path = single_mount.mount_path

            if single_mount.shared_path:
                single_mount_protobuf.shared_path = single_mount.shared_path

            return single_mount_protobuf

        def to_protobuf_ownership_spec(ownership_spec):
            ownership_spec_protobuf = common_pb2.OwnershipSpec()
            ownership_spec_protobuf.uid = ownership_spec.uid
            ownership_spec_protobuf.gid = ownership_spec.gid
            return ownership_spec_protobuf

        if not self.mount_specification_impl:
            raise OperationNotDefinedError(Op.VIRTUAL_MOUNT_SPEC)

        virtual_source_definition = VirtualSourceDefinition.from_dict(
            json.loads(request.virtual_source.parameters.json))
        mounts = [
            VirtualOperations._from_protobuf_single_subset_mount(m)
            for m in request.virtual_source.mounts
        ]
        virtual_source = VirtualSource(guid=request.virtual_source.guid,
                                       connection=RemoteConnection.from_proto(
                                           request.virtual_source.connection),
                                       parameters=virtual_source_definition,
                                       mounts=mounts)

        repository = RepositoryDefinition.from_dict(
            json.loads(request.repository.parameters.json))

        virtual_mount_spec = self.mount_specification_impl(
            repository=repository, virtual_source=virtual_source)

        # Validate that this is a MountSpecification object
        if not isinstance(virtual_mount_spec, MountSpecification):
            raise IncorrectReturnTypeError(Op.VIRTUAL_MOUNT_SPEC,
                                           type(virtual_mount_spec),
                                           MountSpecification)

        virtual_mount_spec_response = platform_pb2.VirtualMountSpecResponse()

        if virtual_mount_spec.ownership_specification:
            ownership_spec = to_protobuf_ownership_spec(
                virtual_mount_spec.ownership_specification)
            virtual_mount_spec_response.return_value.ownership_spec.CopyFrom(
                ownership_spec)

        mounts_list = [
            to_protobuf_single_mount(m) for m in virtual_mount_spec.mounts
        ]
        virtual_mount_spec_response.return_value.mounts.extend(mounts_list)
        return virtual_mount_spec_response
