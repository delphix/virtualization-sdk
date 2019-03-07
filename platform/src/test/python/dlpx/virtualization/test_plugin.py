#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import enum
import json
import mock
import pytest
from dlpx.virtualization import platform_pb2
from dlpx.virtualization.platform import plugin


def test_configure():
    my_plugin = plugin.Plugin()

    @my_plugin.virtual.configure()
    def mock_configure(source, repository, snapshot):
        return SourceConfig(repository.parameters.json, snapshot.parameters.json, source.parameters.json)

    with mock.patch('dlpx.virtualization.platform.plugin.configure',
                    side_effect=mock_configure, create=True):
        test_repository = "TestRepository"
        test_snapshot = "TestSnapshot"
        test_source = "TestDB"

        configure_request = platform_pb2.ConfigureRequest()
        configure_request.repository.parameters.json = test_repository
        configure_request.snapshot.parameters.json = test_snapshot
        configure_request.source.parameters.json = test_source

        # __internal_configure is a private method so it has to be accessed via _Class__member.
        config_response = my_plugin.virtual._internal_configure(configure_request)
        expected_source_config = json.dumps(SourceConfig(test_repository, test_snapshot, test_source).to_dict())

        assert(config_response.return_value.source_config.parameters.json == expected_source_config)

def test_disallow_multiple_decorator_invocations():
    my_plugin = plugin.Plugin()

    @my_plugin.virtual.configure()
    def configure_impl():
        pass

    with pytest.raises(RuntimeError):
        @my_plugin.virtual.configure()
        def configure_impl():
            pass

def test_repository_discovery_wrapper():
    def mock_repository_discovery(source_connection):
        return [Repository("TestRepository1"), Repository("TestRepository2")]

    with mock.patch('dlpx.virtualization.platform.plugin.repository_discovery',
                    side_effect=mock_repository_discovery, create=True):
        repository_discovery_request = platform_pb2.RepositoryDiscoveryRequest()
        repository_discovery_request.source_connection.environment.name = "TestEnvironment"
        repository_discovery_request.source_connection.user.name = "TestUser"

        repository_discovery_response = plugin.repository_discovery_wrapper(repository_discovery_request)

        for repository, expected_repository \
                in zip(repository_discovery_response.return_value.repositories, Repositories.to_json()):
            repository_json = repository.parameters.json
            # protobuf json strings are in unicode, so cast to string
            assert(str(repository_json) == expected_repository)

def test_source_config_discovery_wrapper():
    def mock_source_config_discovery(source_connection, repository):
        return [SourceConfig("TestRepository1", "TestSnapshot1", "TestDB1"),
                SourceConfig("TestRepository2", "TestSnapshot2", "TestDB2")]

    with mock.patch('dlpx.virtualization.platform.plugin.source_config_discovery',
                    side_effect=mock_source_config_discovery, create=True):
        source_config_discovery_request = platform_pb2.SourceConfigDiscoveryRequest()
        source_config_discovery_request.source_connection.environment.name = "TestEnvironment"
        source_config_discovery_request.source_connection.user.name = "TestUser"
        source_config_discovery_request.repository.parameters.json = "TestRepository"

        source_config_discovery_response = \
            plugin.source_config_discovery_wrapper(source_config_discovery_request)

        for source_config, expected_source_config \
                in zip(source_config_discovery_response.return_value.source_configs, SourceConfigs.to_json()):
            source_config_json = source_config.parameters.json
            # protobuf json strings are in unicode, so cast to string
            assert(str(source_config_json) == expected_source_config)


def test_direct_pre_snapshot_wrapper():
    with mock.patch('dlpx.virtualization.platform.plugin.direct_pre_snapshot', create=True):
        direct_pre_snapshot_request = platform_pb2.DirectPreSnapshotRequest()
        expected_result = platform_pb2.DirectPreSnapshotResult()
        direct_pre_snapshot_response = plugin.direct_pre_snapshot_wrapper(direct_pre_snapshot_request)

        # Check that the response's oneof is set to return_value and not error
        assert direct_pre_snapshot_response.WhichOneof("result") == "return_value"
        assert direct_pre_snapshot_response.return_value == expected_result


def test_direct_post_snapshot_wrapper():
    def mock_direct_post_snapshot(direct_source, repository, source_config):
        return Snapshot("TestSnapshot")

    with mock.patch('dlpx.virtualization.platform.plugin.direct_post_snapshot',
                    side_effect=mock_direct_post_snapshot, create=True):
        direct_post_snapshot_request = platform_pb2.DirectPostSnapshotRequest()
        direct_post_snapshot_request.repository.parameters.json = "TestRepository"
        direct_post_snapshot_request.source_config.parameters.json = "TestSourceConfig"
        direct_post_snapshot_request.direct_source.linked_source.parameters.json = "TestSource"

        direct_post_snapshot_response = plugin.direct_post_snapshot_wrapper(direct_post_snapshot_request)
        expected_snapshot = json.dumps(Snapshot("TestSnapshot").to_dict())

        assert direct_post_snapshot_response.return_value.snapshot.parameters.json == expected_snapshot


def test_staged_pre_snapshot_wrapper():
    with mock.patch('dlpx.virtualization.platform.plugin.staged_pre_snapshot', create=True):
        staged_pre_snapshot_request = platform_pb2.StagedPreSnapshotRequest()
        expected_result = platform_pb2.StagedPreSnapshotResult()
        staged_pre_snapshot_response = plugin.staged_pre_snapshot_wrapper(staged_pre_snapshot_request)

        # Check that the response's oneof is set to return_value and not error
        assert staged_pre_snapshot_response.WhichOneof("result") == "return_value"
        assert(staged_pre_snapshot_response.return_value == expected_result)


def test_staged_post_snapshot_wrapper():
    def mock_staged_post_snapshot(staged_source, repository, source_config):
        return Snapshot("TestSnapshot")

    with mock.patch('dlpx.virtualization.platform.plugin.staged_post_snapshot',
                    side_effect=mock_staged_post_snapshot, create=True):
        staged_post_snapshot_request = platform_pb2.StagedPostSnapshotRequest()
        staged_post_snapshot_request.repository.parameters.json = "TestRepository"
        staged_post_snapshot_request.source_config.parameters.json = "TestSourceConfig"
        staged_post_snapshot_request.staged_source.linked_source.parameters.json = "TestSource"

        staged_post_snapshot_response = plugin.staged_post_snapshot_wrapper(staged_post_snapshot_request)
        expected_snapshot = json.dumps(Snapshot("TestSnapshot").to_dict())

        assert staged_post_snapshot_response.return_value.snapshot.parameters.json == expected_snapshot


def test_start_staging_wrapper():
    with mock.patch('dlpx.virtualization.platform.plugin.start_staging', create=True):
        start_staging_request = platform_pb2.StartStagingRequest()
        expected_result = platform_pb2.StartStagingResult()
        start_staging_response = plugin.start_staging_wrapper(start_staging_request)

        # Check that the response's oneof is set to return_value and not error
        assert start_staging_response.WhichOneof("result") == "return_value"
        assert start_staging_response.return_value == expected_result


def test_stop_staging_wrapper():
    with mock.patch('dlpx.virtualization.platform.plugin.stop_staging', create=True):
        stop_staging_request = platform_pb2.StopStagingRequest()
        expected_result = platform_pb2.StopStagingResult()
        stop_staging_response = plugin.stop_staging_wrapper(stop_staging_request)

        # Check that the response's oneof is set to return_value and not error
        assert stop_staging_response.WhichOneof("result") == "return_value"
        assert stop_staging_response.return_value == expected_result


def test_staged_status_wrapper():
    def mock_staged_status(staged_source, repository, source_config):
        return Status.ACTIVE

    with mock.patch('dlpx.virtualization.platform.plugin.staged_status',
                    side_effect=mock_staged_status, create=True):
        staged_status_request = platform_pb2.StagedStatusRequest()
        staged_status_request.repository.parameters.json = "TestRepository"
        staged_status_request.source_config.parameters.json = "TestSourceConfig"
        staged_status_request.staged_source.linked_source.parameters.json = "TestDB"

        staged_status_response = plugin.staged_status_wrapper(staged_status_request)
        expected_status = platform_pb2.StagedStatusResult().ACTIVE

        assert staged_status_response.return_value.status == expected_status


def test_staged_worker_wrapper():
    with mock.patch('dlpx.virtualization.platform.plugin.staged_worker', create=True):
        staged_worker_request = platform_pb2.StagedWorkerRequest()
        expected_result = platform_pb2.StagedWorkerResult()
        staged_worker_response = plugin.staged_worker_wrapper(staged_worker_request)

        # Check that the response's oneof is set to return_value and not error
        assert staged_worker_response.WhichOneof("result") == "return_value"
        assert staged_worker_response.return_value == expected_result


def test_staged_mount_spec_wrapper():
    def mock_staged_mount_spec(staged_source, repository):
        return MountSpec(
            [SingleEntireMount(
                RemoteEnvironment("TestEnvironment1", "TestEnvironmentRef1",
                                  RemoteHost("TestHost1", "TestHostRef1", "/tmp/binary", "/tmp/scratch")),
                "/tmp/mount"),
                SingleEntireMount(
                 RemoteEnvironment("TestEnvironment2", "TestEnvironmentRef2",
                                   RemoteHost("TestHost2", "TestHostRef2", "/tmp/binary", "/tmp/scratch")),
                 "/tmp/mount")],
            OwnershipSpec(1, 1))

    with mock.patch('dlpx.virtualization.platform.plugin.staged_mount_spec',
                    side_effect=mock_staged_mount_spec, create=True):
        staged_mount_spec_request = platform_pb2.StagedMountSpecRequest()
        staged_mount_spec_request.repository.parameters.json = "TestRepository"
        staged_mount_spec_request.staged_source.linked_source.parameters.json = "TestDB"

        staged_mount_spec_response = plugin.staged_mount_spec_wrapper(staged_mount_spec_request)
        expected_mount_spec = MountSpec(
            [SingleEntireMount(
                RemoteEnvironment("TestEnvironment1", "TestEnvironmentRef1",
                                  RemoteHost("TestHost1", "TestHostRef1", "/tmp/binary", "/tmp/scratch")),
                "/tmp/mount")],
            OwnershipSpec(1, 1))

        assert staged_mount_spec_response.return_value.ownership_spec.uid == expected_mount_spec.ownership_spec.uid
        assert staged_mount_spec_response.return_value.ownership_spec.gid == expected_mount_spec.ownership_spec.gid
        mount, expected_mount = staged_mount_spec_response.return_value.staged_mount, expected_mount_spec.mounts[0]
        mount.mount_path = expected_mount.mount_path
        mount.remote_environment.name = expected_mount.remote_environment.name
        mount.remote_environment.reference = expected_mount.remote_environment.reference
        mount.remote_environment.host.name = expected_mount.remote_environment.host.reference
        mount.remote_environment.host.reference = expected_mount.remote_environment.host.reference
        mount.remote_environment.host.binary_path = expected_mount.remote_environment.host.binary_path
        mount.remote_environment.host.scratch_path = expected_mount.remote_environment.host.scratch_path


class Repository:
    def __init__(self, repository_name):
        self.inner_map = {"name": repository_name}

    def to_dict(self):
        return self.inner_map


class SourceConfig:
    def __init__(self, repository, snapshot, source):
        self.inner_map = {"repository": repository, "snapshot": snapshot, "source": source}

    def to_dict(self):
        return self.inner_map


class Snapshot:
    def __init__(self, snapshot_name):
        self.inner_map = {'name': snapshot_name}

    def to_dict(self):
        return self.inner_map


class MountSpec:
    def __init__(self, mounts, ownership_spec):
        self.mounts = mounts
        self.ownership_spec = ownership_spec


class SingleEntireMount:
    def __init__(self, remote_environment, mount_path):
        self.remote_environment = remote_environment
        self.mount_path = mount_path


class RemoteEnvironment:
    def __init__(self, name, reference, host):
        self.name = name
        self.reference = reference
        self.host = host


class RemoteHost:
    def __init__(self, name, reference, binary_path, scratch_path):
        self.name = name
        self.reference = reference
        self.binary_path = binary_path
        self.scratch_path = scratch_path


class OwnershipSpec:
    def __init__(self, uid, gid):
        self.uid = uid
        self.gid = gid


class Repositories:
    @staticmethod
    def to_json():
        return [json.dumps({"name": "TestRepository1"}), json.dumps({"name": "TestRepository2"})]


class SourceConfigs:
    @staticmethod
    def to_json():
        return [json.dumps({"repository": "TestRepository1", "snapshot": "TestSnapshot1", "source": "TestDB1"}),
                json.dumps({"repository": "TestRepository2", "snapshot": "TestSnapshot2", "source": "TestDB2"})]


class Status(enum.Enum):
    ACTIVE = 0
    INACTIVE = 1