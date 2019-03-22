#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import json
import pytest
from dlpx.virtualization import platform_pb2
from mock import MagicMock, patch
import fake_generated_definitions

TEST_ENVIRONMENT = 'TestEnvironment'
TEST_USER = 'TestUser'
TEST_HOST = 'TestHost'
TEST_BINARY_PATH = '/test/bin/path'
TEST_SCRATCH_PATH = '/test/scratch/path'
TEST_MOUNT_PATH = '/test/mount/path'
TEST_SHARED_PATH = '/test/shared/path'
TEST_UID = 1
TEST_GID = 2
TEST_REPOSITORY = 'TestRepository'
TEST_SNAPSHOT = 'TestSnapshot'
TEST_SOURCE_CONFIG = 'TestSourceConfig'
TEST_DIRECT_SOURCE = 'TestDirectSource'
TEST_STAGED_SOURCE = 'TestStagedSource'
TEST_VIRTUAL_SOURCE = 'TestVirtualSource'

# This is a simple JSON object that has only "name" property defined.
SIMPLE_JSON = '{{"name": "{0}"}}'

TEST_REPOSITORY_JSON = SIMPLE_JSON.format(TEST_REPOSITORY)
TEST_SNAPSHOT_JSON = SIMPLE_JSON.format(TEST_SNAPSHOT)
TEST_SOURCE_CONFIG_JSON = SIMPLE_JSON.format(TEST_SOURCE_CONFIG)
TEST_DIRECT_SOURCE_JSON = SIMPLE_JSON.format(TEST_DIRECT_SOURCE)
TEST_STAGED_SOURCE_JSON = SIMPLE_JSON.format(TEST_STAGED_SOURCE)
TEST_VIRTUAL_SOURCE_JSON = SIMPLE_JSON.format(TEST_VIRTUAL_SOURCE)

class TestPlugin:

    @staticmethod
    @pytest.fixture(autouse=True)
    def my_plugin():
        mock_module = MagicMock()
        mock_module.generated.definitions = fake_generated_definitions

        modules = {
            'generated': mock_module,
            'generated.definitions': mock_module.generated.definitions
        }
        with patch.dict('sys.modules', modules):
            from dlpx.virtualization.platform import Plugin
            yield Plugin()

    @staticmethod
    def test_disallow_multiple_decorator_invocations(my_plugin):

        @my_plugin.virtual.configure()
        def configure_impl():
            pass

        with pytest.raises(RuntimeError):
            @my_plugin.virtual.configure()
            def configure_impl():
                pass

    @staticmethod
    def test_virtual_configure(my_plugin):

        @my_plugin.virtual.configure()
        def virtual_configure_impl(virtual_source, repository, snapshot):
            return SourceConfig(repository.name, snapshot.name, virtual_source.parameters.name)

        configure_request = platform_pb2.ConfigureRequest()
        configure_request.repository.parameters.json = TEST_REPOSITORY_JSON
        configure_request.snapshot.parameters.json = TEST_SNAPSHOT_JSON
        configure_request.virtual_source.parameters.json = TEST_VIRTUAL_SOURCE_JSON

        config_response = my_plugin.virtual._internal_configure(configure_request)

        expected_source_config = json.dumps(SourceConfig(TEST_REPOSITORY, TEST_SNAPSHOT, TEST_VIRTUAL_SOURCE).to_dict())
        assert config_response.return_value.source_config.parameters.json == expected_source_config

    @staticmethod
    def test_virtual_unconfigure(my_plugin):

        @my_plugin.virtual.unconfigure()
        def virtual_unconfigure_impl(repository, source_config, virtual_source):
            assert repository.name == TEST_REPOSITORY
            assert source_config.name == TEST_SOURCE_CONFIG
            assert virtual_source.parameters.name == TEST_VIRTUAL_SOURCE
            return

        unconfigure_request = platform_pb2.UnconfigureRequest()
        unconfigure_request.repository.parameters.json = TEST_REPOSITORY_JSON
        unconfigure_request.source_config.parameters.json = TEST_SOURCE_CONFIG_JSON
        unconfigure_request.virtual_source.parameters.json = TEST_VIRTUAL_SOURCE_JSON

        expected_result = platform_pb2.UnconfigureResult()

        unconfigure_response = my_plugin.virtual._internal_unconfigure(unconfigure_request)

        # Check that the response's oneof is set to return_value and not error
        assert unconfigure_response.WhichOneof('result') == 'return_value'
        assert unconfigure_response.return_value == expected_result

    @staticmethod
    def test_virtual_reconfigure(my_plugin):

        @my_plugin.virtual.reconfigure()
        def virtual_reconfigure_impl(snapshot, source_config, virtual_source):
            assert snapshot.name == TEST_SNAPSHOT
            assert source_config.name == TEST_SOURCE_CONFIG
            assert virtual_source.parameters.name == TEST_VIRTUAL_SOURCE
            return SourceConfig(snapshot.name, source_config.name, virtual_source.parameters.name)

        reconfigure_request = platform_pb2.ReconfigureRequest()
        reconfigure_request.snapshot.parameters.json = TEST_SNAPSHOT_JSON
        reconfigure_request.source_config.parameters.json = TEST_SOURCE_CONFIG_JSON
        reconfigure_request.virtual_source.parameters.json = TEST_VIRTUAL_SOURCE_JSON

        reconfigure_response = my_plugin.virtual._internal_reconfigure(reconfigure_request)
        expected_source_config = json.dumps(SourceConfig(TEST_SNAPSHOT, TEST_SOURCE_CONFIG, TEST_VIRTUAL_SOURCE).to_dict())

        assert reconfigure_response.return_value.source_config.parameters.json == expected_source_config

    @staticmethod
    def test_virtual_start(my_plugin):

        @my_plugin.virtual.start()
        def virtual_start_impl(repository, source_config, virtual_source):
            assert repository.name == TEST_REPOSITORY
            assert source_config.name == TEST_SOURCE_CONFIG
            assert virtual_source.parameters.name == TEST_VIRTUAL_SOURCE
            return

        start_request = platform_pb2.StartRequest()
        start_request.repository.parameters.json = TEST_REPOSITORY_JSON
        start_request.source_config.parameters.json = TEST_SOURCE_CONFIG_JSON
        start_request.virtual_source.parameters.json = TEST_VIRTUAL_SOURCE_JSON

        expected_result = platform_pb2.StartResult()
        start_response = my_plugin.virtual._internal_start(start_request)

        # Check that the response's oneof is set to return_value and not error
        assert start_response.WhichOneof('result') == 'return_value'
        assert start_response.return_value == expected_result

    @staticmethod
    def test_virtual_stop(my_plugin):

        @my_plugin.virtual.stop()
        def start_impl(repository, source_config, virtual_source):
            assert repository.name == TEST_REPOSITORY
            assert source_config.name == TEST_SOURCE_CONFIG
            assert virtual_source.parameters.name == TEST_VIRTUAL_SOURCE
            return

        stop_request = platform_pb2.StopRequest()
        stop_request.repository.parameters.json = TEST_REPOSITORY_JSON
        stop_request.source_config.parameters.json = TEST_SOURCE_CONFIG_JSON
        stop_request.virtual_source.parameters.json = TEST_VIRTUAL_SOURCE_JSON

        expected_result = platform_pb2.StopResult()
        stop_response = my_plugin.virtual._internal_stop(stop_request)

        # Check that the response's oneof is set to return_value and not error
        assert stop_response.WhichOneof('result') == 'return_value'
        assert stop_response.return_value == expected_result

    @staticmethod
    def test_virtual_pre_snapshot(my_plugin):

        @my_plugin.virtual.pre_snapshot()
        def virtual_pre_snapshot_impl(repository, source_config, virtual_source):
            assert repository.name == TEST_REPOSITORY
            assert source_config.name == TEST_SOURCE_CONFIG
            assert virtual_source.parameters.name == TEST_VIRTUAL_SOURCE
            return

        virtual_pre_snapshot_request = platform_pb2.VirtualPreSnapshotRequest()
        virtual_pre_snapshot_request.repository.parameters.json = TEST_REPOSITORY_JSON
        virtual_pre_snapshot_request.source_config.parameters.json = TEST_SOURCE_CONFIG_JSON
        virtual_pre_snapshot_request.virtual_source.parameters.json = TEST_VIRTUAL_SOURCE_JSON

        expected_result = platform_pb2.VirtualPreSnapshotResult()
        virtual_pre_snapshot_response = my_plugin.virtual._internal_pre_snapshot(virtual_pre_snapshot_request)

        # Check that the response's oneof is set to return_value and not error
        assert virtual_pre_snapshot_response.WhichOneof('result') == 'return_value'
        assert virtual_pre_snapshot_response.return_value == expected_result

    @staticmethod
    def test_virtual_post_snapshot(my_plugin):

        @my_plugin.virtual.post_snapshot()
        def virtual_post_snapshot_impl(repository, source_config, virtual_source):
            assert repository.name == TEST_REPOSITORY
            assert source_config.name == TEST_SOURCE_CONFIG
            assert virtual_source.parameters.name == TEST_VIRTUAL_SOURCE
            return Snapshot(TEST_SNAPSHOT)

        virtual_post_snapshot_request = platform_pb2.VirtualPostSnapshotRequest()
        virtual_post_snapshot_request.repository.parameters.json = TEST_REPOSITORY_JSON
        virtual_post_snapshot_request.source_config.parameters.json = TEST_SOURCE_CONFIG_JSON
        virtual_post_snapshot_request.virtual_source.parameters.json = TEST_VIRTUAL_SOURCE_JSON

        virtual_post_snapshot_response = my_plugin.virtual._internal_post_snapshot(virtual_post_snapshot_request)
        expected_snapshot = json.dumps(Snapshot(TEST_SNAPSHOT).to_dict())

        assert virtual_post_snapshot_response.return_value.snapshot.parameters.json == expected_snapshot

    @staticmethod
    def test_virtual_status(my_plugin):

        from dlpx.virtualization.platform import Status

        @my_plugin.virtual.status()
        def virtual_status_impl(repository, source_config, virtual_source):
            assert repository.name == TEST_REPOSITORY
            assert source_config.name == TEST_SOURCE_CONFIG
            assert virtual_source.parameters.name == TEST_VIRTUAL_SOURCE
            return Status.ACTIVE

        virtual_status_request = platform_pb2.VirtualStatusRequest()
        virtual_status_request.repository.parameters.json = TEST_REPOSITORY_JSON
        virtual_status_request.source_config.parameters.json = TEST_SOURCE_CONFIG_JSON
        virtual_status_request.virtual_source.parameters.json = TEST_VIRTUAL_SOURCE_JSON

        virtual_status_response = my_plugin.virtual._internal_status(virtual_status_request)
        expected_status = platform_pb2.VirtualStatusResult().ACTIVE

        assert virtual_status_response.return_value.status == expected_status

    @staticmethod
    def test_virtual_initialize(my_plugin):

        @my_plugin.virtual.initialize()
        def virtual_initialize_impl(repository, source_config, virtual_source):
            assert repository.name == TEST_REPOSITORY
            assert source_config.name == TEST_SOURCE_CONFIG
            assert virtual_source.parameters.name == TEST_VIRTUAL_SOURCE
            return

        initialize_request = platform_pb2.InitializeRequest()
        initialize_request.repository.parameters.json = TEST_REPOSITORY_JSON
        initialize_request.source_config.parameters.json = TEST_SOURCE_CONFIG_JSON
        initialize_request.virtual_source.parameters.json = TEST_VIRTUAL_SOURCE_JSON
        expected_result = platform_pb2.InitializeResult()
        initialize_response = my_plugin.virtual._internal_initialize(initialize_request)

        # Check that the response's oneof is set to return_value and not error
        assert initialize_response.WhichOneof('result') == 'return_value'
        assert initialize_response.return_value == expected_result

    @staticmethod
    def test_virtual_mount_spec(my_plugin):

        from dlpx.virtualization.platform import Mount, MountSpecification, OwnershipSpecification

        @my_plugin.virtual.mount_specification()
        def virtual_mount_spec_impl(repository, virtual_source):
            assert virtual_source.connection.environment.reference == TEST_ENVIRONMENT
            assert virtual_source.connection.user.reference == TEST_USER
            assert virtual_source.parameters.name == TEST_VIRTUAL_SOURCE
            assert repository.name == TEST_REPOSITORY

            primary_mount = Mount(virtual_source.connection.environment, TEST_MOUNT_PATH, TEST_SHARED_PATH)
            another_mount = Mount(virtual_source.connection.environment, TEST_MOUNT_PATH, TEST_SHARED_PATH)
            ownership_spec = OwnershipSpecification(TEST_UID, TEST_GID)

            return MountSpecification([primary_mount, another_mount], ownership_spec)

        virtual_mount_spec_request = platform_pb2.VirtualMountSpecRequest()
        virtual_mount_spec_request.virtual_source.connection.environment.reference = TEST_ENVIRONMENT
        virtual_mount_spec_request.virtual_source.connection.environment.host.reference = TEST_HOST
        virtual_mount_spec_request.virtual_source.connection.environment.host.binary_path = TEST_BINARY_PATH
        virtual_mount_spec_request.virtual_source.connection.environment.host.scratch_path = TEST_SCRATCH_PATH
        virtual_mount_spec_request.virtual_source.connection.user.reference = TEST_USER
        virtual_mount_spec_request.virtual_source.parameters.json = TEST_VIRTUAL_SOURCE_JSON
        virtual_mount_spec_request.repository.parameters.json = TEST_REPOSITORY_JSON

        virtual_mount_spec_response = my_plugin.virtual._internal_mount_specification(virtual_mount_spec_request)

        response_mounts = virtual_mount_spec_response.return_value.mounts

        for mount in response_mounts:
            assert mount.remote_environment.reference == TEST_ENVIRONMENT
            assert mount.remote_environment.host.reference == TEST_HOST
            assert mount.remote_environment.host.binary_path == TEST_BINARY_PATH
            assert mount.remote_environment.host.scratch_path == TEST_SCRATCH_PATH
            assert mount.mount_path == TEST_MOUNT_PATH
            assert mount.shared_path == TEST_SHARED_PATH

        assert virtual_mount_spec_response.return_value.ownership_spec.uid == TEST_UID
        assert virtual_mount_spec_response.return_value.ownership_spec.gid == TEST_GID

    @staticmethod
    def test_repository_discovery(my_plugin):

        @my_plugin.discovery.repository()
        def repository_discovery_impl(source_connection):
            assert source_connection.environment.reference == TEST_ENVIRONMENT
            assert source_connection.user.reference == TEST_USER
            return [Repository(TEST_REPOSITORY), Repository(TEST_REPOSITORY)]

        repository_discovery_request = platform_pb2.RepositoryDiscoveryRequest()
        repository_discovery_request.source_connection.environment.reference = TEST_ENVIRONMENT
        repository_discovery_request.source_connection.user.reference = TEST_USER

        repository_discovery_response = my_plugin.discovery._internal_repository(repository_discovery_request)

        for repository in repository_discovery_response.return_value.repositories:
            assert repository.parameters.json == TEST_REPOSITORY_JSON

    @staticmethod
    def test_source_config_discovery(my_plugin):

        @my_plugin.discovery.source_config()
        def source_config_discovery_impl(source_connection, repository):
            assert source_connection.environment.reference == TEST_ENVIRONMENT
            assert source_connection.user.reference == TEST_USER
            assert repository.name == TEST_REPOSITORY
            return [SourceConfig(TEST_REPOSITORY, TEST_SNAPSHOT, TEST_ENVIRONMENT),
                    SourceConfig(TEST_REPOSITORY, TEST_SNAPSHOT, TEST_ENVIRONMENT)]

        source_config_discovery_request = platform_pb2.SourceConfigDiscoveryRequest()
        source_config_discovery_request.source_connection.environment.reference =  TEST_ENVIRONMENT
        source_config_discovery_request.source_connection.user.reference = TEST_USER
        source_config_discovery_request.repository.parameters.json = TEST_REPOSITORY_JSON

        source_config_discovery_response = my_plugin.discovery._internal_source_config(source_config_discovery_request)

        for source_config in source_config_discovery_response.return_value.source_configs:
            assert source_config.parameters.json == json.dumps(SourceConfig(TEST_REPOSITORY, TEST_SNAPSHOT, TEST_ENVIRONMENT).to_dict())

    @staticmethod
    def test_direct_pre_snapshot(my_plugin):

        @my_plugin.linked.pre_snapshot()
        def mock_direct_pre_snapshot(direct_source, repository, source_config):
            assert direct_source.parameters.name == TEST_DIRECT_SOURCE
            assert repository.name == TEST_REPOSITORY
            assert source_config.name == TEST_SOURCE_CONFIG
            return

        direct_pre_snapshot_request = platform_pb2.DirectPreSnapshotRequest()
        direct_pre_snapshot_request.direct_source.linked_source.parameters.json = TEST_DIRECT_SOURCE_JSON
        direct_pre_snapshot_request.repository.parameters.json = TEST_REPOSITORY_JSON
        direct_pre_snapshot_request.source_config.parameters.json = TEST_SOURCE_CONFIG_JSON

        expected_result = platform_pb2.DirectPreSnapshotResult()
        direct_pre_snapshot_response = my_plugin.linked._internal_direct_pre_snapshot(direct_pre_snapshot_request)

        # Check that the response's oneof is set to return_value and not error
        assert direct_pre_snapshot_response.WhichOneof('result') == 'return_value'
        assert direct_pre_snapshot_response.return_value == expected_result

    @staticmethod
    def test_direct_post_snapshot(my_plugin):

        @my_plugin.linked.post_snapshot()
        def direct_post_snapshot_impl(direct_source, repository, source_config):
            assert direct_source.parameters.name == TEST_DIRECT_SOURCE
            assert repository.name == TEST_REPOSITORY
            assert source_config.name == TEST_SOURCE_CONFIG
            return Snapshot(TEST_SNAPSHOT)

        direct_post_snapshot_request = platform_pb2.DirectPostSnapshotRequest()
        direct_post_snapshot_request.repository.parameters.json = TEST_REPOSITORY_JSON
        direct_post_snapshot_request.source_config.parameters.json = TEST_SOURCE_CONFIG_JSON
        direct_post_snapshot_request.direct_source.linked_source.parameters.json = TEST_DIRECT_SOURCE_JSON

        direct_post_snapshot_response = my_plugin.linked._internal_direct_post_snapshot(direct_post_snapshot_request)
        expected_snapshot = json.dumps(Snapshot(TEST_SNAPSHOT).to_dict())

        assert direct_post_snapshot_response.return_value.snapshot.parameters.json == expected_snapshot

    @staticmethod
    def test_staged_pre_snapshot(my_plugin):

        @my_plugin.linked.pre_snapshot()
        def staged_pre_snapshot_impl(repository, source_config, staged_source):
            assert repository.name == TEST_REPOSITORY
            assert source_config.name == TEST_SOURCE_CONFIG
            assert staged_source.parameters.name == TEST_STAGED_SOURCE
            return

        staged_pre_snapshot_request = platform_pb2.StagedPreSnapshotRequest()
        staged_pre_snapshot_request.repository.parameters.json = TEST_REPOSITORY_JSON
        staged_pre_snapshot_request.source_config.parameters.json = TEST_SOURCE_CONFIG_JSON
        staged_pre_snapshot_request.staged_source.linked_source.parameters.json = TEST_STAGED_SOURCE_JSON

        expected_result = platform_pb2.StagedPreSnapshotResult()
        staged_pre_snapshot_response = my_plugin.linked._internal_staged_pre_snapshot(staged_pre_snapshot_request)

        # Check that the response's oneof is set to return_value and not error
        assert staged_pre_snapshot_response.WhichOneof('result') == 'return_value'
        assert(staged_pre_snapshot_response.return_value == expected_result)

    @staticmethod
    def test_staged_post_snapshot(my_plugin):

        @my_plugin.linked.post_snapshot()
        def staged_post_snapshot_impl(staged_source, repository, source_config):
            assert staged_source.parameters.name == TEST_STAGED_SOURCE
            assert repository.name == TEST_REPOSITORY
            assert source_config.name == TEST_SOURCE_CONFIG
            return Snapshot(TEST_SNAPSHOT)


        staged_post_snapshot_request = platform_pb2.StagedPostSnapshotRequest()
        staged_post_snapshot_request.repository.parameters.json = TEST_REPOSITORY_JSON
        staged_post_snapshot_request.source_config.parameters.json = TEST_SOURCE_CONFIG_JSON
        staged_post_snapshot_request.staged_source.linked_source.parameters.json = TEST_STAGED_SOURCE_JSON

        staged_post_snapshot_response = my_plugin.linked._internal_staged_post_snapshot(staged_post_snapshot_request)
        expected_snapshot = json.dumps(Snapshot(TEST_SNAPSHOT).to_dict())

        assert staged_post_snapshot_response.return_value.snapshot.parameters.json == expected_snapshot

    @staticmethod
    def test_start_staging(my_plugin):

        @my_plugin.linked.start_staging()
        def start_staging_impl(repository, source_config, staged_source):
            assert repository.name == TEST_REPOSITORY
            assert source_config.name == TEST_SOURCE_CONFIG
            assert staged_source.parameters.name == TEST_STAGED_SOURCE
            return

        start_staging_request = platform_pb2.StartStagingRequest()
        start_staging_request.repository.parameters.json = TEST_REPOSITORY_JSON
        start_staging_request.source_config.parameters.json = TEST_SOURCE_CONFIG_JSON
        start_staging_request.staged_source.linked_source.parameters.json = TEST_STAGED_SOURCE_JSON

        expected_result = platform_pb2.StartStagingResult()
        start_staging_response = my_plugin.linked._internal_start_staging(start_staging_request)

        # Check that the response's oneof is set to return_value and not error
        assert start_staging_response.WhichOneof('result') == 'return_value'
        assert start_staging_response.return_value == expected_result

    @staticmethod
    def test_stop_staging(my_plugin):

        @my_plugin.linked.stop_staging()
        def stop_staging_impl(repository, source_config, staged_source):
            assert repository.name == TEST_REPOSITORY
            assert source_config.name == TEST_SOURCE_CONFIG
            assert staged_source.parameters.name == TEST_STAGED_SOURCE
            return

        stop_staging_request = platform_pb2.StopStagingRequest()
        stop_staging_request.repository.parameters.json = TEST_REPOSITORY_JSON
        stop_staging_request.source_config.parameters.json = TEST_SOURCE_CONFIG_JSON
        stop_staging_request.staged_source.linked_source.parameters.json = TEST_STAGED_SOURCE_JSON

        expected_result = platform_pb2.StopStagingResult()
        stop_staging_response = my_plugin.linked._internal_stop_staging(stop_staging_request)

        # Check that the response's oneof is set to return_value and not error
        assert stop_staging_response.WhichOneof('result') == 'return_value'
        assert stop_staging_response.return_value == expected_result

    @staticmethod
    def test_staged_status(my_plugin):

        from dlpx.virtualization.platform import Status

        @my_plugin.linked.status()
        def staged_status_impl(staged_source, repository, source_config):
            assert staged_source.parameters.name == TEST_STAGED_SOURCE
            assert repository.name == TEST_REPOSITORY
            assert source_config.name == TEST_SOURCE_CONFIG
            return Status.ACTIVE

        staged_status_request = platform_pb2.StagedStatusRequest()
        staged_status_request.repository.parameters.json = TEST_REPOSITORY_JSON
        staged_status_request.source_config.parameters.json = TEST_SOURCE_CONFIG_JSON
        staged_status_request.staged_source.linked_source.parameters.json = TEST_STAGED_SOURCE_JSON

        staged_status_response = my_plugin.linked._internal_status(staged_status_request)
        expected_status = platform_pb2.StagedStatusResult().ACTIVE

        assert staged_status_response.return_value.status == expected_status

    @staticmethod
    def test_staged_worker(my_plugin):

        @my_plugin.linked.worker()
        def staged_worker_impl(repository, source_config, staged_source):
            assert repository.name == TEST_REPOSITORY
            assert source_config.name == TEST_SOURCE_CONFIG
            assert staged_source.parameters.name == TEST_STAGED_SOURCE
            return

        staged_worker_request = platform_pb2.StagedWorkerRequest()
        staged_worker_request.repository.parameters.json = TEST_REPOSITORY_JSON
        staged_worker_request.source_config.parameters.json = TEST_SOURCE_CONFIG_JSON
        staged_worker_request.staged_source.linked_source.parameters.json = TEST_STAGED_SOURCE_JSON

        expected_result = platform_pb2.StagedWorkerResult()
        staged_worker_response = my_plugin.linked._internal_worker(staged_worker_request)

        # Check that the response's oneof is set to return_value and not error
        assert staged_worker_response.WhichOneof('result') == 'return_value'
        assert staged_worker_response.return_value == expected_result

    @staticmethod
    def test_staged_mount_spec(my_plugin):

        from dlpx.virtualization.platform import Mount, MountSpecification, OwnershipSpecification

        @my_plugin.linked.mount_specification()
        def staged_mount_spec_impl(staged_source, repository):
            assert staged_source.connection.environment.reference == TEST_ENVIRONMENT
            assert staged_source.connection.user.reference == TEST_USER
            assert staged_source.parameters.name == TEST_STAGED_SOURCE
            assert repository.name == TEST_REPOSITORY

            mount1 = Mount(staged_source.connection.environment, TEST_MOUNT_PATH)
            ownership_spec = OwnershipSpecification(TEST_UID, TEST_GID)

            return MountSpecification([mount1], ownership_spec)

        staged_mount_spec_request = platform_pb2.StagedMountSpecRequest()
        staged_mount_spec_request.staged_source.connection.environment.reference = TEST_ENVIRONMENT
        staged_mount_spec_request.staged_source.connection.environment.host.reference = TEST_HOST
        staged_mount_spec_request.staged_source.connection.environment.host.binary_path = TEST_BINARY_PATH
        staged_mount_spec_request.staged_source.connection.environment.host.scratch_path = TEST_SCRATCH_PATH
        staged_mount_spec_request.staged_source.connection.user.reference = TEST_USER
        staged_mount_spec_request.staged_source.linked_source.parameters.json = TEST_STAGED_SOURCE_JSON
        staged_mount_spec_request.repository.parameters.json = TEST_REPOSITORY_JSON

        staged_mount_spec_response = my_plugin.linked._internal_mount_specification(staged_mount_spec_request)

        assert staged_mount_spec_response.return_value.staged_mount.remote_environment.reference == TEST_ENVIRONMENT
        assert staged_mount_spec_response.return_value.staged_mount.remote_environment.host.reference == TEST_HOST
        assert staged_mount_spec_response.return_value.staged_mount.remote_environment.host.binary_path == TEST_BINARY_PATH
        assert staged_mount_spec_response.return_value.staged_mount.remote_environment.host.scratch_path == TEST_SCRATCH_PATH
        assert staged_mount_spec_response.return_value.staged_mount.mount_path == TEST_MOUNT_PATH
        assert staged_mount_spec_response.return_value.ownership_spec.uid == TEST_UID
        assert staged_mount_spec_response.return_value.ownership_spec.gid == TEST_GID

"""
The following classes are sample plugin defined types.
"""
class Repository:
    def __init__(self, repository_name):
        self.inner_map = {'name': repository_name}

    def to_dict(self):
        return self.inner_map

class SourceConfig:
    def __init__(self, repository, snapshot, source):
        self.inner_map = {'repository': repository, 'snapshot': snapshot, 'source': source}

    def to_dict(self):
        return self.inner_map

class Snapshot:
    def __init__(self, snapshot_name):
        self.inner_map = {'name': snapshot_name}

    def to_dict(self):
        return self.inner_map
