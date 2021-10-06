from __future__ import absolute_import
#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import json

import pytest
from dlpx.virtualization.api import common_pb2, platform_pb2
from dlpx.virtualization.common import (RemoteConnection, RemoteEnvironment,
                                        RemoteHost, RemoteUser)
from dlpx.virtualization.platform.exceptions import (
    IncorrectReturnTypeError, IncorrectUpgradeObjectTypeError,
    OperationAlreadyDefinedError, PluginRuntimeError)
from mock import MagicMock, patch

from . import fake_generated_definitions
from .fake_generated_definitions import (RepositoryDefinition,
                                        SnapshotDefinition,
                                        SourceConfigDefinition)

TEST_BINARY_PATH = '/binary/path'
TEST_SCRATCH_PATH = '/scratch/path'
TEST_MOUNT_PATH = '/mnt/path'
TEST_SHARED_PATH = '/shared/path'
TEST_GUID = '8e1442c2-64ce-48cf-848c-ce4deacca579'
TEST_HOST_NAME = 'TestHost'
TEST_HOST_REFERENCE = 'UNIX_HOST-1'
TEST_ENVIRONMENT_NAME = 'TestEnvironment'
TEST_ENVIRONMENT_REFERENCE = 'UNIX_HOST_ENVIRONMENT-1'
TEST_USER_NAME = 'TestUser'
TEST_USER_REFERENCE = 'HOST_USER-1'
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
TEST_SNAPSHOT_PARAMS_JSON = '{"resync": false}'
TEST_PRE_UPGRADE_PARAMS = {'obj': json.dumps({'name': 'upgrade'})}
TEST_POST_MIGRATION_METADATA_1 = (json.dumps(
    {'obj': {
        'name': 'upgrade',
        'prettyName': 'prettyUpgrade'
    }}))
TEST_POST_MIGRATION_METADATA_2 = (json.dumps({
    'obj': {
        'name': 'upgrade',
        'prettyName': 'prettyUpgrade',
        'metadata': 'metadata'
    }
}))
TEST_POST_UPGRADE_PARAMS = ({
    u'obj':
    '"{\\"obj\\": {\\"prettyName\\": \\"prettyUpgrade\\", '
    '\\"name\\": \\"upgrade\\", \\"metadata\\": \\"metadata\\"}}"'
})
MIGRATION_IDS = ('2020.1.1', '2020.2.2')


class TestPlugin:
    @staticmethod
    @pytest.fixture
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

        with pytest.raises(OperationAlreadyDefinedError):

            @my_plugin.virtual.configure()
            def configure_impl():
                pass

    class NotModel1:
        pass

    class NotModel2(object):
        pass

    class NotModel3(NotModel1):
        pass

    class Model:
        pass

    class NotModel4(Model):
        def __init__(self):
            self._swagger_types = {}

        @property
        def swagger_types(self):
            return self._swagger_types

    class NotModel5(Model):
        def __init__(self):
            self._attribute_map = {}

        @property
        def attribute_map(self):
            return self._attribute_map

    @staticmethod
    @pytest.fixture(autouse=True,
                    params=[
                        NotModel1(),
                        NotModel2(),
                        NotModel3(),
                        NotModel4(),
                        NotModel5(), 'string', 1
                    ])
    def not_model(request):
        return request.param

    @staticmethod
    def assert_user(user):
        assert isinstance(user, RemoteUser)
        assert user.name == TEST_USER_NAME
        assert user.reference == TEST_USER_REFERENCE

    @staticmethod
    def assert_host(host):
        assert isinstance(host, RemoteHost)
        assert host.name == TEST_HOST_NAME
        assert host.reference == TEST_HOST_REFERENCE
        assert host.binary_path == TEST_BINARY_PATH
        assert host.scratch_path == TEST_SCRATCH_PATH

    @staticmethod
    def assert_host_protobuf(host):
        assert isinstance(host, common_pb2.RemoteHost)
        assert host.name == TEST_HOST_NAME
        assert host.reference == TEST_HOST_REFERENCE
        assert host.binary_path == TEST_BINARY_PATH
        assert host.scratch_path == TEST_SCRATCH_PATH

    @staticmethod
    def assert_environment(environment):
        assert isinstance(environment, RemoteEnvironment)
        assert environment.name == TEST_ENVIRONMENT_NAME
        assert environment.reference == TEST_ENVIRONMENT_REFERENCE
        TestPlugin.assert_host(environment.host)

    @staticmethod
    def assert_environment_protobuf(environment):
        assert isinstance(environment, common_pb2.RemoteEnvironment)
        assert environment.name == TEST_ENVIRONMENT_NAME
        assert environment.reference == TEST_ENVIRONMENT_REFERENCE
        TestPlugin.assert_host_protobuf(environment.host)

    @staticmethod
    def assert_connection(connection):
        assert isinstance(connection, RemoteConnection)
        TestPlugin.assert_environment(connection.environment)
        TestPlugin.assert_user(connection.user)

    @staticmethod
    def assert_mount(mount):
        TestPlugin.assert_environment(mount.remote_environment)
        assert mount.mount_path == TEST_MOUNT_PATH
        assert mount.shared_path == TEST_SHARED_PATH

    @staticmethod
    def assert_mount_protobuf(mount):
        TestPlugin.assert_environment_protobuf(mount.remote_environment)
        assert mount.mount_path == TEST_MOUNT_PATH
        assert mount.shared_path == TEST_SHARED_PATH

    @staticmethod
    def assert_mounts(mounts):
        assert len(mounts) == 1
        TestPlugin.assert_mount(mounts[0])

    @staticmethod
    def assert_virtual_source(virtual_source):
        assert virtual_source.guid == TEST_GUID
        TestPlugin.assert_connection(virtual_source.connection)
        TestPlugin.assert_mounts(virtual_source.mounts)
        assert virtual_source.parameters.name == TEST_VIRTUAL_SOURCE

    @staticmethod
    def assert_direct_source(direct_source):
        assert direct_source.guid == TEST_GUID
        TestPlugin.assert_connection(direct_source.connection)
        assert direct_source.parameters.name == TEST_DIRECT_SOURCE

    @staticmethod
    def assert_staged_mount(staged_mount):
        TestPlugin.assert_environment(staged_mount.remote_environment)
        assert staged_mount.mount_path == TEST_MOUNT_PATH
        assert staged_mount.shared_path == TEST_SHARED_PATH

    @staticmethod
    def assert_staged_source(staged_source):
        assert staged_source.guid == TEST_GUID
        TestPlugin.assert_connection(staged_source.source_connection)
        assert staged_source.parameters.name == TEST_STAGED_SOURCE
        TestPlugin.assert_staged_mount(staged_source.mount)
        TestPlugin.assert_connection(staged_source.staged_connection)

    @staticmethod
    def assert_repository(repository):
        assert repository.name == TEST_REPOSITORY

    @staticmethod
    def assert_source_config(source_config):
        assert source_config.name == TEST_SOURCE_CONFIG

    @staticmethod
    def assert_snapshot(snapshot):
        assert snapshot.name == TEST_SNAPSHOT

    @staticmethod
    def assert_snapshot_parameters(snapshot_parameters):
        assert not snapshot_parameters.resync

    @staticmethod
    @pytest.fixture
    def host():
        host = common_pb2.RemoteHost()
        host.name = TEST_HOST_NAME
        host.reference = TEST_HOST_REFERENCE
        host.binary_path = TEST_BINARY_PATH
        host.scratch_path = TEST_SCRATCH_PATH
        return host

    @staticmethod
    @pytest.fixture
    def environment(host):
        environment = common_pb2.RemoteEnvironment()
        environment.name = TEST_ENVIRONMENT_NAME
        environment.reference = TEST_ENVIRONMENT_REFERENCE
        environment.host.CopyFrom(host)
        return environment

    @staticmethod
    @pytest.fixture
    def mount(environment):
        mount = common_pb2.SingleSubsetMount()
        mount.remote_environment.CopyFrom(environment)
        mount.mount_path = TEST_MOUNT_PATH
        mount.shared_path = TEST_SHARED_PATH
        return mount

    @staticmethod
    @pytest.fixture
    def user():
        user = common_pb2.RemoteUser()
        user.name = TEST_USER_NAME
        user.reference = TEST_USER_REFERENCE
        return user

    @staticmethod
    @pytest.fixture
    def connection(environment, user):
        connection = common_pb2.RemoteConnection()
        connection.environment.CopyFrom(environment)
        connection.user.CopyFrom(user)
        return connection

    @staticmethod
    @pytest.fixture
    def staged_connection(environment, user):
        staged_connection = common_pb2.RemoteConnection()
        staged_connection.environment.CopyFrom(environment)
        staged_connection.user.CopyFrom(user)
        return staged_connection

    @staticmethod
    @pytest.fixture
    def virtual_source(connection, mount):
        virtual_source = common_pb2.VirtualSource()
        virtual_source.guid = TEST_GUID
        virtual_source.connection.CopyFrom(connection)
        virtual_source.parameters.json = TEST_VIRTUAL_SOURCE_JSON
        virtual_source.mounts.extend([mount])
        return virtual_source

    @staticmethod
    @pytest.fixture
    def repository():
        repository = common_pb2.Repository()
        repository.parameters.json = TEST_REPOSITORY_JSON
        return repository

    @staticmethod
    @pytest.fixture
    def source_config():
        source_config = common_pb2.SourceConfig()
        source_config.parameters.json = TEST_SOURCE_CONFIG_JSON
        return source_config

    @staticmethod
    @pytest.fixture
    def snapshot():
        snapshot = common_pb2.Snapshot()
        snapshot.parameters.json = TEST_SNAPSHOT_JSON
        return snapshot

    @staticmethod
    @pytest.fixture
    def snapshot_parameters():
        snapshot_parameters = common_pb2.SnapshotParameters()
        snapshot_parameters.parameters.json = TEST_SNAPSHOT_PARAMS_JSON
        return snapshot_parameters

    @staticmethod
    @pytest.fixture
    def linked_source():
        linked_source = common_pb2.LinkedSource()
        linked_source.guid = TEST_GUID
        return linked_source

    @staticmethod
    @pytest.fixture
    def direct_source(linked_source, connection):
        direct_source = common_pb2.DirectSource()
        direct_source.connection.CopyFrom(connection)
        direct_source.linked_source.CopyFrom(linked_source)
        direct_source.linked_source.parameters.json = TEST_DIRECT_SOURCE_JSON
        return direct_source

    @staticmethod
    @pytest.fixture
    def staged_mount(environment):
        staged_mount = common_pb2.SingleEntireMount()
        staged_mount.remote_environment.CopyFrom(environment)
        staged_mount.mount_path = TEST_MOUNT_PATH
        staged_mount.shared_path = TEST_SHARED_PATH
        return staged_mount

    @staticmethod
    @pytest.fixture
    def staged_source(connection, linked_source, staged_mount,
                      staged_connection):
        staged_source = common_pb2.StagedSource()
        staged_source.source_connection.CopyFrom(connection)
        staged_source.linked_source.CopyFrom(linked_source)
        staged_source.linked_source.parameters.json = TEST_STAGED_SOURCE_JSON
        staged_source.staged_mount.CopyFrom(staged_mount)
        staged_source.staged_connection.CopyFrom(staged_connection)
        return staged_source

    @staticmethod
    def setup_request(request,
                      virtual_source=None,
                      direct_source=None,
                      staged_source=None,
                      repository=None,
                      source_config=None,
                      snapshot=None,
                      snapshot_parameters=None):
        if virtual_source:
            request.virtual_source.CopyFrom(virtual_source)

        if direct_source:
            request.direct_source.CopyFrom(direct_source)

        if staged_source:
            request.staged_source.CopyFrom(staged_source)

        if repository:
            request.repository.CopyFrom(repository)

        if source_config:
            request.source_config.CopyFrom(source_config)

        if snapshot:
            request.snapshot.CopyFrom(snapshot)

        if snapshot_parameters:
            request.snapshot_parameters.CopyFrom(snapshot_parameters)

    @staticmethod
    def assert_plugin_args(**kwargs):
        for key, value in kwargs.items():
            assert value is not None, 'key {} is None'.format(key)

        if 'direct_source' in kwargs:
            TestPlugin.assert_direct_source(kwargs['direct_source'])

        if 'virtual_source' in kwargs:
            TestPlugin.assert_virtual_source(kwargs['virtual_source'])

        if 'staged_source' in kwargs:
            TestPlugin.assert_staged_source(kwargs['staged_source'])

        if 'repository' in kwargs:
            TestPlugin.assert_repository(kwargs['repository'])

        if 'source_config' in kwargs:
            TestPlugin.assert_source_config(kwargs['source_config'])

        if 'snapshot' in kwargs:
            TestPlugin.assert_snapshot(kwargs['snapshot'])

        if 'snapshot_parameters' in kwargs:
            TestPlugin.assert_snapshot_parameters(
                kwargs['snapshot_parameters'])

    @staticmethod
    def test_virtual_configure(my_plugin, virtual_source, repository,
                               snapshot):
        @my_plugin.virtual.configure()
        def virtual_configure_impl(virtual_source, repository, snapshot):
            TestPlugin.assert_plugin_args(virtual_source=virtual_source,
                                          repository=repository,
                                          snapshot=snapshot)

            return SourceConfigDefinition(snapshot.name)

        configure_request = platform_pb2.ConfigureRequest()
        TestPlugin.setup_request(request=configure_request,
                                 virtual_source=virtual_source,
                                 repository=repository,
                                 snapshot=snapshot)

        config_response = my_plugin.virtual._internal_configure(
            configure_request)
        config = config_response.return_value.source_config
        expected_source_config = TEST_SNAPSHOT_JSON
        assert config.parameters.json == expected_source_config

    @staticmethod
    def test_virtual_configure_return_incorrect_type(my_plugin, virtual_source,
                                                     repository, snapshot):
        @my_plugin.virtual.configure()
        def virtual_configure_impl(virtual_source, repository, snapshot):
            TestPlugin.assert_plugin_args(virtual_source=virtual_source,
                                          repository=repository,
                                          snapshot=snapshot)

            # Returns the name rather then the object.
            return snapshot.name

        configure_request = platform_pb2.ConfigureRequest()
        TestPlugin.setup_request(request=configure_request,
                                 virtual_source=virtual_source,
                                 repository=repository,
                                 snapshot=snapshot)

        with pytest.raises(IncorrectReturnTypeError) as err_info:
            my_plugin.virtual._internal_configure(configure_request)

        message = err_info.value.message
        assert message == (
            "The returned object for the virtual.configure() operation was"
            " type 'unicode' but should be of class 'dlpx.virtualization."
            "fake_generated_definitions.SourceConfigDefinition'.")

    @staticmethod
    def test_virtual_unconfigure(my_plugin, virtual_source, repository,
                                 source_config):
        @my_plugin.virtual.unconfigure()
        def virtual_unconfigure_impl(virtual_source, repository,
                                     source_config):
            TestPlugin.assert_plugin_args(virtual_source=virtual_source,
                                          repository=repository,
                                          source_config=source_config)
            return

        unconfigure_request = platform_pb2.UnconfigureRequest()
        TestPlugin.setup_request(request=unconfigure_request,
                                 virtual_source=virtual_source,
                                 repository=repository,
                                 source_config=source_config)

        expected_result = platform_pb2.UnconfigureResult()

        unconfigure_response = my_plugin.virtual._internal_unconfigure(
            unconfigure_request)

        # Check that the response's oneof is set to return_value and not error
        assert unconfigure_response.WhichOneof('result') == 'return_value'
        assert unconfigure_response.return_value == expected_result

    @staticmethod
    def test_virtual_reconfigure(my_plugin, virtual_source, repository,
                                 source_config, snapshot):
        @my_plugin.virtual.reconfigure()
        def virtual_reconfigure_impl(virtual_source, repository, source_config,
                                     snapshot):
            TestPlugin.assert_plugin_args(virtual_source=virtual_source,
                                          source_config=source_config,
                                          repository=repository,
                                          snapshot=snapshot)

            return SourceConfigDefinition(snapshot.name)

        reconfigure_request = platform_pb2.ReconfigureRequest()
        TestPlugin.setup_request(request=reconfigure_request,
                                 virtual_source=virtual_source,
                                 source_config=source_config,
                                 repository=repository,
                                 snapshot=snapshot)

        reconfigure_response = my_plugin.virtual._internal_reconfigure(
            reconfigure_request)

        config = reconfigure_response.return_value.source_config
        expected_source_config = TEST_SNAPSHOT_JSON
        assert config.parameters.json == expected_source_config

    @staticmethod
    def test_virtual_reconfigure_return_incorrect_type(my_plugin,
                                                       virtual_source,
                                                       repository,
                                                       source_config,
                                                       snapshot):
        @my_plugin.virtual.reconfigure()
        def virtual_reconfigure_impl(virtual_source, repository, source_config,
                                     snapshot):
            TestPlugin.assert_plugin_args(virtual_source=virtual_source,
                                          source_config=source_config,
                                          repository=repository,
                                          snapshot=snapshot)

            # Returns the name rather then the object.
            return snapshot.name

        reconfigure_request = platform_pb2.ReconfigureRequest()
        TestPlugin.setup_request(request=reconfigure_request,
                                 virtual_source=virtual_source,
                                 source_config=source_config,
                                 repository=repository,
                                 snapshot=snapshot)

        with pytest.raises(IncorrectReturnTypeError) as err_info:
            my_plugin.virtual._internal_reconfigure(reconfigure_request)

        message = err_info.value.message
        assert message == (
            "The returned object for the virtual.reconfigure() operation was"
            " type 'unicode' but should be of class 'dlpx.virtualization."
            "fake_generated_definitions.SourceConfigDefinition'.")

    @staticmethod
    def test_virtual_start(my_plugin, virtual_source, repository,
                           source_config):
        @my_plugin.virtual.start()
        def virtual_start_impl(virtual_source, repository, source_config):
            TestPlugin.assert_plugin_args(virtual_source=virtual_source,
                                          repository=repository,
                                          source_config=source_config)
            return

        start_request = platform_pb2.StartRequest()
        TestPlugin.setup_request(request=start_request,
                                 virtual_source=virtual_source,
                                 repository=repository,
                                 source_config=source_config)

        expected_result = platform_pb2.StartResult()
        start_response = my_plugin.virtual._internal_start(start_request)

        # Check that the response's oneof is set to return_value and not error
        assert start_response.WhichOneof('result') == 'return_value'
        assert start_response.return_value == expected_result

    @staticmethod
    def test_virtual_stop(my_plugin, virtual_source, repository,
                          source_config):
        @my_plugin.virtual.stop()
        def start_impl(virtual_source, repository, source_config):
            TestPlugin.assert_plugin_args(virtual_source=virtual_source,
                                          repository=repository,
                                          source_config=source_config)
            return

        stop_request = platform_pb2.StopRequest()
        TestPlugin.setup_request(request=stop_request,
                                 virtual_source=virtual_source,
                                 repository=repository,
                                 source_config=source_config)

        expected_result = platform_pb2.StopResult()
        stop_response = my_plugin.virtual._internal_stop(stop_request)

        # Check that the response's oneof is set to return_value and not error
        assert stop_response.WhichOneof('result') == 'return_value'
        assert stop_response.return_value == expected_result

    @staticmethod
    def test_virtual_pre_snapshot(my_plugin, virtual_source, repository,
                                  source_config):
        @my_plugin.virtual.pre_snapshot()
        def virtual_pre_snapshot_impl(virtual_source, repository,
                                      source_config):
            TestPlugin.assert_plugin_args(virtual_source=virtual_source,
                                          repository=repository,
                                          source_config=source_config)
            return

        virtual_pre_snapshot_request = platform_pb2.VirtualPreSnapshotRequest()
        TestPlugin.setup_request(request=virtual_pre_snapshot_request,
                                 virtual_source=virtual_source,
                                 repository=repository,
                                 source_config=source_config)

        expected_result = platform_pb2.VirtualPreSnapshotResult()
        virtual_pre_snapshot_response = (
            my_plugin.virtual._internal_pre_snapshot(
                virtual_pre_snapshot_request))

        # Check that the response's oneof is set to return_value and not error
        assert virtual_pre_snapshot_response.WhichOneof(
            'result') == 'return_value'
        assert virtual_pre_snapshot_response.return_value == expected_result

    @staticmethod
    def test_virtual_post_snapshot(my_plugin, virtual_source, repository,
                                   source_config):
        @my_plugin.virtual.post_snapshot()
        def virtual_post_snapshot_impl(virtual_source, repository,
                                       source_config):
            TestPlugin.assert_plugin_args(virtual_source=virtual_source,
                                          repository=repository,
                                          source_config=source_config)
            return SnapshotDefinition(TEST_SNAPSHOT)

        virtual_post_snapshot_request = (
            platform_pb2.VirtualPostSnapshotRequest())
        TestPlugin.setup_request(request=virtual_post_snapshot_request,
                                 virtual_source=virtual_source,
                                 repository=repository,
                                 source_config=source_config)

        virtual_post_snapshot_response = (
            my_plugin.virtual._internal_post_snapshot(
                virtual_post_snapshot_request))
        expected_snapshot = TEST_SNAPSHOT_JSON

        assert (virtual_post_snapshot_response.return_value.snapshot.
                parameters.json == expected_snapshot)

    @staticmethod
    def test_virtual_status(my_plugin, virtual_source, repository,
                            source_config):

        from dlpx.virtualization.platform import Status

        @my_plugin.virtual.status()
        def virtual_status_impl(virtual_source, repository, source_config):
            TestPlugin.assert_plugin_args(virtual_source=virtual_source,
                                          repository=repository,
                                          source_config=source_config)
            return Status.ACTIVE

        virtual_status_request = platform_pb2.VirtualStatusRequest()
        TestPlugin.setup_request(request=virtual_status_request,
                                 virtual_source=virtual_source,
                                 repository=repository,
                                 source_config=source_config)

        virtual_status_response = my_plugin.virtual._internal_status(
            virtual_status_request)
        expected_status = platform_pb2.VirtualStatusResult().ACTIVE

        assert virtual_status_response.return_value.status == expected_status

    @staticmethod
    def test_virtual_initialize(my_plugin, virtual_source, repository,
                                source_config):
        @my_plugin.virtual.initialize()
        def virtual_initialize_impl(virtual_source, repository):
            TestPlugin.assert_plugin_args(virtual_source=virtual_source,
                                          repository=repository)
            return SourceConfigDefinition(repository.name)

        initialize_request = platform_pb2.InitializeRequest()
        TestPlugin.setup_request(request=initialize_request,
                                 virtual_source=virtual_source,
                                 repository=repository)

        expected_source_config = TEST_REPOSITORY_JSON
        initialize_response = my_plugin.virtual._internal_initialize(
            initialize_request)

        # Check that the response's oneof is set to return_value and not error
        assert initialize_response.WhichOneof('result') == 'return_value'
        actual_source_config = initialize_response.return_value.source_config
        assert actual_source_config.parameters.json == TEST_REPOSITORY_JSON

    @staticmethod
    def test_virtual_initialize_return_none(my_plugin, virtual_source,
                                            repository, source_config):
        @my_plugin.virtual.initialize()
        def virtual_initialize_impl(virtual_source, repository):
            TestPlugin.assert_plugin_args(virtual_source=virtual_source,
                                          repository=repository)
            # Will return none.

        initialize_request = platform_pb2.InitializeRequest()
        TestPlugin.setup_request(request=initialize_request,
                                 virtual_source=virtual_source,
                                 repository=repository)

        with pytest.raises(IncorrectReturnTypeError) as err_info:
            my_plugin.virtual._internal_initialize(initialize_request)
        message = err_info.value.message
        assert message == (
            "The returned object for the virtual.initialize() operation was"
            " type 'NoneType' but should be of class 'dlpx.virtualization."
            "fake_generated_definitions.SourceConfigDefinition'.")

    @staticmethod
    def test_virtual_mount_spec(my_plugin, virtual_source, repository):

        from dlpx.virtualization.platform import (Mount, MountSpecification,
                                                  OwnershipSpecification)

        @my_plugin.virtual.mount_specification()
        def virtual_mount_spec_impl(virtual_source, repository):
            TestPlugin.assert_plugin_args(virtual_source=virtual_source,
                                          repository=repository)

            primary_mount = Mount(virtual_source.connection.environment,
                                  TEST_MOUNT_PATH, TEST_SHARED_PATH)
            another_mount = Mount(virtual_source.connection.environment,
                                  TEST_MOUNT_PATH, TEST_SHARED_PATH)
            ownership_spec = OwnershipSpecification(TEST_UID, TEST_GID)

            return MountSpecification([primary_mount, another_mount],
                                      ownership_spec)

        virtual_mount_spec_request = platform_pb2.VirtualMountSpecRequest()
        TestPlugin.setup_request(request=virtual_mount_spec_request,
                                 virtual_source=virtual_source,
                                 repository=repository)

        virtual_mount_spec_response = (
            my_plugin.virtual._internal_mount_specification(
                virtual_mount_spec_request))

        response_mounts = virtual_mount_spec_response.return_value.mounts

        for mount in response_mounts:
            TestPlugin.assert_mount_protobuf(mount)

        return_value = virtual_mount_spec_response.return_value
        assert return_value.ownership_spec.uid == TEST_UID
        assert return_value.ownership_spec.gid == TEST_GID

    @staticmethod
    def test_repository_discovery(my_plugin, connection):
        @my_plugin.discovery.repository()
        def repository_discovery_impl(source_connection):
            TestPlugin.assert_connection(source_connection)
            return [
                RepositoryDefinition(TEST_REPOSITORY),
                RepositoryDefinition(TEST_REPOSITORY)
            ]

        repository_discovery_request = (
            platform_pb2.RepositoryDiscoveryRequest())
        repository_discovery_request.source_connection.CopyFrom(connection)

        repository_discovery_response = (
            my_plugin.discovery._internal_repository(
                repository_discovery_request))
        repositories = repository_discovery_response.return_value.repositories
        for repository in repositories:
            assert repository.parameters.json == TEST_REPOSITORY_JSON

    @staticmethod
    def test_repository_discovery_bad_return_type(my_plugin, connection):
        @my_plugin.discovery.repository()
        def repository_discovery_impl(source_connection):
            TestPlugin.assert_connection(source_connection)
            return ['string', RepositoryDefinition(TEST_REPOSITORY)]

        repository_discovery_request = (
            platform_pb2.RepositoryDiscoveryRequest())
        repository_discovery_request.source_connection.CopyFrom(connection)

        with pytest.raises(IncorrectReturnTypeError) as err_info:
            my_plugin.discovery._internal_repository(
                repository_discovery_request)

        message = err_info.value.message
        assert message == (
            "The returned object for the discovery.repository() operation was"
            " a list of [type 'str', class 'dlpx.virtualization"
            ".fake_generated_definitions.RepositoryDefinition'] but should"
            " be of type 'list of dlpx.virtualization"
            ".fake_generated_definitions.RepositoryDefinition'.")

    @staticmethod
    def test_source_config_discovery(my_plugin, connection, repository):
        @my_plugin.discovery.source_config()
        def source_config_discovery_impl(source_connection, repository):
            TestPlugin.assert_connection(source_connection)
            TestPlugin.assert_repository(repository)
            return [
                SourceConfigDefinition(TEST_REPOSITORY),
                SourceConfigDefinition(TEST_REPOSITORY)
            ]

        source_config_discovery_request = (
            platform_pb2.SourceConfigDiscoveryRequest())
        source_config_discovery_request.source_connection.CopyFrom(connection)
        source_config_discovery_request.repository.CopyFrom(repository)

        source_config_discovery_response = (
            my_plugin.discovery._internal_source_config(
                source_config_discovery_request))

        configs = source_config_discovery_response.return_value.source_configs
        for source_config in configs:
            assert source_config.parameters.json == TEST_REPOSITORY_JSON

    @staticmethod
    def test_direct_pre_snapshot(my_plugin, direct_source, repository,
                                 source_config, snapshot_parameters):
        @my_plugin.linked.pre_snapshot()
        def mock_direct_pre_snapshot(direct_source, repository, source_config,
                                     optional_snapshot_parameters):
            TestPlugin.assert_plugin_args(
                direct_source=direct_source,
                repository=repository,
                source_config=source_config,
                snapshot_parameters=optional_snapshot_parameters)
            return

        direct_pre_snapshot_request = platform_pb2.DirectPreSnapshotRequest()
        TestPlugin.setup_request(request=direct_pre_snapshot_request,
                                 direct_source=direct_source,
                                 repository=repository,
                                 source_config=source_config,
                                 snapshot_parameters=snapshot_parameters)

        expected_result = platform_pb2.DirectPreSnapshotResult()
        direct_pre_snapshot_response = (
            my_plugin.linked._internal_direct_pre_snapshot(
                direct_pre_snapshot_request))

        # Check that the response's oneof is set to return_value and not error
        assert direct_pre_snapshot_response.WhichOneof(
            'result') == 'return_value'
        assert direct_pre_snapshot_response.return_value == expected_result

    @staticmethod
    def test_direct_pre_snapshot_null_snapparams(my_plugin, direct_source,
                                                 repository, source_config):
        @my_plugin.linked.pre_snapshot()
        def mock_direct_pre_snapshot(direct_source, repository, source_config,
            optional_snapshot_parameters):
            TestPlugin.assert_direct_source(direct_source)
            TestPlugin.assert_repository(repository)
            TestPlugin.assert_source_config(source_config)
            assert not optional_snapshot_parameters
            return

        snapshot_parameters = common_pb2.SnapshotParameters()
        snapshot_parameters.parameters.json = 'null'

        direct_pre_snapshot_request = platform_pb2.DirectPreSnapshotRequest()
        TestPlugin.setup_request(request=direct_pre_snapshot_request,
                                 direct_source=direct_source,
                                 repository=repository,
                                 source_config=source_config,
                                 snapshot_parameters=snapshot_parameters)

        expected_result = platform_pb2.DirectPreSnapshotResult()
        direct_pre_snapshot_response = (
            my_plugin.linked._internal_direct_pre_snapshot(
                direct_pre_snapshot_request))

        # Check that the response's oneof is set to return_value and not error
        assert direct_pre_snapshot_response.WhichOneof(
            'result') == 'return_value'
        assert direct_pre_snapshot_response.return_value == expected_result

    @staticmethod
    def test_direct_post_snapshot(my_plugin, direct_source, repository,
                                  source_config, snapshot_parameters):
        @my_plugin.linked.post_snapshot()
        def direct_post_snapshot_impl(direct_source, repository, source_config,
                                      optional_snapshot_parameters):
            TestPlugin.assert_plugin_args(
                direct_source=direct_source,
                repository=repository,
                source_config=source_config,
                snapshot_parameters=optional_snapshot_parameters)
            return SnapshotDefinition(TEST_SNAPSHOT)

        direct_post_snapshot_request = platform_pb2.DirectPostSnapshotRequest()
        TestPlugin.setup_request(
            request=direct_post_snapshot_request,
            direct_source=direct_source,
            repository=repository,
            source_config=source_config,
            snapshot_parameters=snapshot_parameters)

        direct_post_snapshot_response = (
            my_plugin.linked._internal_direct_post_snapshot(
                direct_post_snapshot_request))
        expected_snapshot = TEST_SNAPSHOT_JSON
        snapshot = direct_post_snapshot_response.return_value.snapshot
        assert snapshot.parameters.json == expected_snapshot

    @staticmethod
    def test_direct_post_snapshot_null_snapparams(my_plugin, direct_source,
        repository, source_config):
        @my_plugin.linked.post_snapshot()
        def direct_post_snapshot_impl(direct_source, repository, source_config,
            optional_snapshot_parameters):
            TestPlugin.assert_direct_source(direct_source)
            TestPlugin.assert_repository(repository)
            TestPlugin.assert_source_config(source_config)
            assert not optional_snapshot_parameters
            return SnapshotDefinition(TEST_SNAPSHOT)

        snapshot_parameters = common_pb2.SnapshotParameters()
        snapshot_parameters.parameters.json = 'null'

        direct_post_snapshot_request = platform_pb2.DirectPostSnapshotRequest()
        TestPlugin.setup_request(
            request=direct_post_snapshot_request,
            direct_source=direct_source,
            repository=repository,
            source_config=source_config,
            snapshot_parameters=snapshot_parameters)

        direct_post_snapshot_response = (
            my_plugin.linked._internal_direct_post_snapshot(
                direct_post_snapshot_request))
        expected_snapshot = TEST_SNAPSHOT_JSON
        snapshot = direct_post_snapshot_response.return_value.snapshot
        assert snapshot.parameters.json == expected_snapshot

    @staticmethod
    def test_staged_pre_snapshot(my_plugin, staged_source, repository,
                                 source_config, snapshot_parameters):
        @my_plugin.linked.pre_snapshot()
        def staged_pre_snapshot_impl(staged_source, repository, source_config,
                                     optional_snapshot_parameters):
            TestPlugin.assert_plugin_args(
                staged_source=staged_source,
                repository=repository,
                source_config=source_config,
                snapshot_parameters=optional_snapshot_parameters)
            return

        staged_pre_snapshot_request = platform_pb2.StagedPreSnapshotRequest()
        TestPlugin.setup_request(
            request=staged_pre_snapshot_request,
            staged_source=staged_source,
            repository=repository,
            source_config=source_config,
            snapshot_parameters=snapshot_parameters)

        expected_result = platform_pb2.StagedPreSnapshotResult()
        response = my_plugin.linked._internal_staged_pre_snapshot(
            staged_pre_snapshot_request)

        # Check that the response's oneof is set to return_value and not error
        assert response.WhichOneof('result') == 'return_value'
        assert (response.return_value == expected_result)

    @staticmethod
    def test_staged_pre_snapshot_null_snapparams(my_plugin, staged_source,
                                                 repository, source_config):
        @my_plugin.linked.pre_snapshot()
        def staged_pre_snapshot_impl(staged_source, repository, source_config,
            optional_snapshot_parameters):
            TestPlugin.assert_staged_source(staged_source)
            TestPlugin.assert_repository(repository)
            TestPlugin.assert_source_config(source_config)
            assert not optional_snapshot_parameters
            return

        snapshot_parameters = common_pb2.SnapshotParameters()
        snapshot_parameters.parameters.json = 'null'

        staged_pre_snapshot_request = platform_pb2.StagedPreSnapshotRequest()
        TestPlugin.setup_request(
            request=staged_pre_snapshot_request,
            staged_source=staged_source,
            repository=repository,
            source_config=source_config,
            snapshot_parameters=snapshot_parameters)

        expected_result = platform_pb2.StagedPreSnapshotResult()
        response = my_plugin.linked._internal_staged_pre_snapshot(
            staged_pre_snapshot_request)

        # Check that the response's oneof is set to return_value and not error
        assert response.WhichOneof('result') == 'return_value'
        assert (response.return_value == expected_result)

    @staticmethod
    def test_staged_post_snapshot(my_plugin, staged_source, repository,
                                  source_config, snapshot_parameters):
        @my_plugin.linked.post_snapshot()
        def staged_post_snapshot_impl(staged_source, repository, source_config,
                                      optional_snapshot_parameters):
            TestPlugin.assert_plugin_args(
                staged_source=staged_source,
                repository=repository,
                source_config=source_config,
                snapshot_parameters=optional_snapshot_parameters)
            return SnapshotDefinition(TEST_SNAPSHOT)

        staged_post_snapshot_request = platform_pb2.StagedPostSnapshotRequest()
        TestPlugin.setup_request(
            request=staged_post_snapshot_request,
            staged_source=staged_source,
            repository=repository,
            source_config=source_config,
            snapshot_parameters=snapshot_parameters)

        response = my_plugin.linked._internal_staged_post_snapshot(
            staged_post_snapshot_request)
        expected = TEST_SNAPSHOT_JSON

        assert response.return_value.snapshot.parameters.json == expected

    @staticmethod
    def test_staged_post_snapshot_null_snapparams(my_plugin, staged_source,
                                                  repository, source_config):
        @my_plugin.linked.post_snapshot()
        def staged_post_snapshot_impl(staged_source, repository, source_config,
            optional_snapshot_parameters):
            TestPlugin.assert_staged_source(staged_source)
            TestPlugin.assert_repository(repository)
            TestPlugin.assert_source_config(source_config)
            assert not optional_snapshot_parameters
            return SnapshotDefinition(TEST_SNAPSHOT)

        snapshot_parameters = common_pb2.SnapshotParameters()
        snapshot_parameters.parameters.json = 'null'

        staged_post_snapshot_request = platform_pb2.StagedPostSnapshotRequest()
        TestPlugin.setup_request(
            request=staged_post_snapshot_request,
            staged_source=staged_source,
            repository=repository,
            source_config=source_config,
            snapshot_parameters=snapshot_parameters)

        response = my_plugin.linked._internal_staged_post_snapshot(
            staged_post_snapshot_request)
        expected = TEST_SNAPSHOT_JSON

        assert response.return_value.snapshot.parameters.json == expected

    @staticmethod
    def test_start_staging(my_plugin, staged_source, repository,
                           source_config):
        @my_plugin.linked.start_staging()
        def start_staging_impl(staged_source, repository, source_config):
            TestPlugin.assert_plugin_args(staged_source=staged_source,
                                          repository=repository,
                                          source_config=source_config)
            return

        start_staging_request = platform_pb2.StartStagingRequest()
        TestPlugin.setup_request(request=start_staging_request,
                                 staged_source=staged_source,
                                 repository=repository,
                                 source_config=source_config)

        expected_result = platform_pb2.StartStagingResult()
        start_staging_response = (
            my_plugin.linked._internal_start_staging(start_staging_request))

        # Check that the response's oneof is set to return_value and not error
        assert start_staging_response.WhichOneof('result') == 'return_value'
        assert start_staging_response.return_value == expected_result

    @staticmethod
    def test_stop_staging(my_plugin, staged_source, repository, source_config):
        @my_plugin.linked.stop_staging()
        def stop_staging_impl(staged_source, repository, source_config):
            TestPlugin.assert_plugin_args(staged_source=staged_source,
                                          repository=repository,
                                          source_config=source_config)
            return

        stop_staging_request = platform_pb2.StopStagingRequest()
        TestPlugin.setup_request(request=stop_staging_request,
                                 staged_source=staged_source,
                                 repository=repository,
                                 source_config=source_config)

        expected_result = platform_pb2.StopStagingResult()
        stop_staging_response = (
            my_plugin.linked._internal_stop_staging(stop_staging_request))

        # Check that the response's oneof is set to return_value and not error
        assert stop_staging_response.WhichOneof('result') == 'return_value'
        assert stop_staging_response.return_value == expected_result

    @staticmethod
    def test_staged_status(my_plugin, staged_source, repository,
                           source_config):

        from dlpx.virtualization.platform import Status

        @my_plugin.linked.status()
        def staged_status_impl(staged_source, repository, source_config):
            TestPlugin.assert_plugin_args(staged_source=staged_source,
                                          repository=repository,
                                          source_config=source_config)
            return Status.ACTIVE

        staged_status_request = platform_pb2.StagedStatusRequest()
        TestPlugin.setup_request(request=staged_status_request,
                                 staged_source=staged_source,
                                 repository=repository,
                                 source_config=source_config)

        staged_status_response = my_plugin.linked._internal_status(
            staged_status_request)
        expected_status = platform_pb2.StagedStatusResult().ACTIVE

        assert staged_status_response.return_value.status == expected_status

    @staticmethod
    def test_staged_worker(my_plugin, staged_source, repository,
                           source_config):
        @my_plugin.linked.worker()
        def staged_worker_impl(staged_source, repository, source_config):
            TestPlugin.assert_plugin_args(staged_source=staged_source,
                                          repository=repository,
                                          source_config=source_config)
            return

        staged_worker_request = platform_pb2.StagedWorkerRequest()
        TestPlugin.setup_request(request=staged_worker_request,
                                 staged_source=staged_source,
                                 repository=repository,
                                 source_config=source_config)

        expected_result = platform_pb2.StagedWorkerResult()
        staged_worker_response = my_plugin.linked._internal_worker(
            staged_worker_request)

        # Check that the response's oneof is set to return_value and not error
        assert staged_worker_response.WhichOneof('result') == 'return_value'
        assert staged_worker_response.return_value == expected_result

    @staticmethod
    def test_staged_mount_spec(my_plugin, staged_source, repository):

        from dlpx.virtualization.platform import (Mount, MountSpecification,
                                                  OwnershipSpecification)

        @my_plugin.linked.mount_specification()
        def staged_mount_spec_impl(staged_source, repository):
            TestPlugin.assert_plugin_args(staged_source=staged_source,
                                          repository=repository)

            mount = Mount(staged_source.source_connection.environment,
                          TEST_MOUNT_PATH)
            ownership_spec = OwnershipSpecification(TEST_UID, TEST_GID)

            return MountSpecification([mount], ownership_spec)

        staged_mount_spec_request = platform_pb2.StagedMountSpecRequest()
        TestPlugin.setup_request(request=staged_mount_spec_request,
                                 staged_source=staged_source,
                                 repository=repository)

        staged_mount_spec_response = (
            my_plugin.linked._internal_mount_specification(
                staged_mount_spec_request))

        staged_mount = staged_mount_spec_response.return_value.staged_mount
        ownership_spec = staged_mount_spec_response.return_value.ownership_spec

        TestPlugin.assert_environment_protobuf(staged_mount.remote_environment)
        assert staged_mount.mount_path == TEST_MOUNT_PATH
        # shared_path is not supported and must be empty
        assert staged_mount.shared_path == ''
        assert ownership_spec.uid == TEST_UID
        assert ownership_spec.gid == TEST_GID

    @staticmethod
    def test_staged_mount_spec_fail(my_plugin, staged_source, repository):

        from dlpx.virtualization.platform import (Mount, MountSpecification,
                                                  OwnershipSpecification)

        @my_plugin.linked.mount_specification()
        def staged_mount_spec_impl(staged_source, repository):
            TestPlugin.assert_plugin_args(staged_source=staged_source,
                                          repository=repository)
            # setting the shared_path should fail in the wrapper
            mount = Mount(staged_source.source_connection.environment,
                          TEST_MOUNT_PATH, TEST_SHARED_PATH)
            ownership_spec = OwnershipSpecification(TEST_UID, TEST_GID)

            return MountSpecification([mount], ownership_spec)

        staged_mount_spec_request = platform_pb2.StagedMountSpecRequest()
        TestPlugin.setup_request(request=staged_mount_spec_request,
                                 staged_source=staged_source,
                                 repository=repository)
        with pytest.raises(PluginRuntimeError) as err_info:
            my_plugin.linked._internal_mount_specification(
                staged_mount_spec_request)

        message = err_info.value.message
        assert message == 'Shared path is not supported for linked sources.'

    @staticmethod
    def test_upgrade_repository_success(my_plugin):
        @my_plugin.upgrade.repository('2020.1.1')
        def upgrade_repository(old_repository):
            return TEST_POST_MIGRATION_METADATA_1

        @my_plugin.upgrade.repository('2020.2.2')
        def upgrade_repository(old_repository):
            return TEST_POST_MIGRATION_METADATA_2

        upgrade_request = platform_pb2.UpgradeRequest()
        upgrade_request.pre_upgrade_parameters.update(TEST_PRE_UPGRADE_PARAMS)
        upgrade_request.type = upgrade_request.REPOSITORY
        upgrade_request.migration_ids.extend(MIGRATION_IDS)

        upgrade_response = \
            (my_plugin.upgrade._internal_repository(upgrade_request))

        expected_response = platform_pb2.UpgradeResponse()
        expected_response.return_value.post_upgrade_parameters\
            .update(TEST_POST_UPGRADE_PARAMS)

        assert expected_response == upgrade_response

    @staticmethod
    def test_upgrade_source_config_success(my_plugin):
        @my_plugin.upgrade.source_config('2020.1.1')
        def upgrade_source_config(old_source_config):
            return TEST_POST_MIGRATION_METADATA_1

        @my_plugin.upgrade.source_config('2020.2.2')
        def upgrade_source_config(old_source_config):
            return TEST_POST_MIGRATION_METADATA_2

        upgrade_request = platform_pb2.UpgradeRequest()
        upgrade_request.pre_upgrade_parameters.update(TEST_PRE_UPGRADE_PARAMS)
        upgrade_request.type = upgrade_request.SOURCECONFIG
        upgrade_request.migration_ids.extend(MIGRATION_IDS)

        upgrade_response = \
            (my_plugin.upgrade._internal_source_config(upgrade_request))

        expected_response = platform_pb2.UpgradeResponse()
        expected_response.return_value.post_upgrade_parameters \
            .update(TEST_POST_UPGRADE_PARAMS)

        assert expected_response == upgrade_response

    @staticmethod
    def test_upgrade_linked_source_success(my_plugin):
        @my_plugin.upgrade.linked_source('2020.1.1')
        def upgrade_linked_source(old_linked_source):
            return TEST_POST_MIGRATION_METADATA_1

        @my_plugin.upgrade.linked_source('2020.2.2')
        def upgrade_linked_source(old_linked_source):
            return TEST_POST_MIGRATION_METADATA_2

        upgrade_request = platform_pb2.UpgradeRequest()
        upgrade_request.pre_upgrade_parameters.update(TEST_PRE_UPGRADE_PARAMS)
        upgrade_request.type = upgrade_request.LINKEDSOURCE
        upgrade_request.migration_ids.extend(MIGRATION_IDS)

        upgrade_response = \
            (my_plugin.upgrade._internal_linked_source(upgrade_request))

        expected_response = platform_pb2.UpgradeResponse()
        expected_response.return_value.post_upgrade_parameters \
            .update(TEST_POST_UPGRADE_PARAMS)

        assert expected_response == upgrade_response

    @staticmethod
    def test_upgrade_virtual_source_success(my_plugin):
        @my_plugin.upgrade.virtual_source('2020.1.1')
        def upgrade_virtual_source(old_virtual_source):
            return TEST_POST_MIGRATION_METADATA_1

        @my_plugin.upgrade.virtual_source('2020.2.2')
        def upgrade_virtual_source(old_virtual_source):
            return TEST_POST_MIGRATION_METADATA_2

        upgrade_request = platform_pb2.UpgradeRequest()
        upgrade_request.pre_upgrade_parameters.update(TEST_PRE_UPGRADE_PARAMS)
        upgrade_request.type = upgrade_request.VIRTUALSOURCE
        upgrade_request.migration_ids.extend(MIGRATION_IDS)

        upgrade_response = \
            (my_plugin.upgrade._internal_virtual_source(upgrade_request))

        expected_response = platform_pb2.UpgradeResponse()
        expected_response.return_value.post_upgrade_parameters \
            .update(TEST_POST_UPGRADE_PARAMS)

        assert expected_response == upgrade_response

    @staticmethod
    def test_upgrade_snapshot_success(my_plugin):
        @my_plugin.upgrade.snapshot('2020.1.1')
        def upgrade_snapshot(old_snapshot):
            return TEST_POST_MIGRATION_METADATA_1

        @my_plugin.upgrade.snapshot('2020.2.2')
        def upgrade_snapshot(old_snapshot):
            return TEST_POST_MIGRATION_METADATA_2

        upgrade_request = platform_pb2.UpgradeRequest()
        upgrade_request.pre_upgrade_parameters.update(TEST_PRE_UPGRADE_PARAMS)
        upgrade_request.type = upgrade_request.SNAPSHOT
        upgrade_request.migration_ids.extend(MIGRATION_IDS)

        upgrade_response = \
            (my_plugin.upgrade._internal_snapshot(upgrade_request))

        expected_response = platform_pb2.UpgradeResponse()
        expected_response.return_value.post_upgrade_parameters \
            .update(TEST_POST_UPGRADE_PARAMS)

        assert expected_response == upgrade_response

    @staticmethod
    def test_upgrade_repository_incorrect_upgrade_object_type(my_plugin):
        upgrade_request = platform_pb2.UpgradeRequest()
        upgrade_request.type = upgrade_request.SNAPSHOT

        with pytest.raises(IncorrectUpgradeObjectTypeError) as err_info:
            my_plugin.upgrade._internal_repository(upgrade_request)

        message = err_info.value.message
        assert message == ("The upgrade operation received objects with 4 type"
                           " but should have had type 1.")

    @staticmethod
    def test_upgrade_source_config_incorrect_upgrade_object_type(my_plugin):
        upgrade_request = platform_pb2.UpgradeRequest()
        upgrade_request.type = upgrade_request.SNAPSHOT

        with pytest.raises(IncorrectUpgradeObjectTypeError) as err_info:
            my_plugin.upgrade._internal_source_config(upgrade_request)

        message = err_info.value.message
        assert message == ("The upgrade operation received objects with 4 type"
                           " but should have had type 0.")

    @staticmethod
    def test_upgrade_linked_source_incorrect_upgrade_object_type(my_plugin):
        upgrade_request = platform_pb2.UpgradeRequest()
        upgrade_request.type = upgrade_request.SNAPSHOT

        with pytest.raises(IncorrectUpgradeObjectTypeError) as err_info:
            my_plugin.upgrade._internal_linked_source(upgrade_request)

        message = err_info.value.message
        assert message == ("The upgrade operation received objects with 4 type"
                           " but should have had type 2.")

    @staticmethod
    def test_upgrade_virtual_source_incorrect_upgrade_object_type(my_plugin):
        upgrade_request = platform_pb2.UpgradeRequest()
        upgrade_request.type = upgrade_request.SNAPSHOT

        with pytest.raises(IncorrectUpgradeObjectTypeError) as err_info:
            my_plugin.upgrade._internal_virtual_source(upgrade_request)

        message = err_info.value.message
        assert message == ("The upgrade operation received objects with 4 type"
                           " but should have had type 3.")

    @staticmethod
    def test_upgrade_snapshot_incorrect_upgrade_object_type(my_plugin):
        upgrade_request = platform_pb2.UpgradeRequest()
        upgrade_request.type = upgrade_request.SOURCECONFIG

        with pytest.raises(IncorrectUpgradeObjectTypeError) as err_info:
            my_plugin.upgrade._internal_snapshot(upgrade_request)

        message = err_info.value.message
        assert message == ("The upgrade operation received objects with 0 type"
                           " but should have had type 4.")

    @staticmethod
    def test_upgrade_snapshot_fail_with_runtime_error(my_plugin):
        @my_plugin.upgrade.snapshot('2020.1.1')
        def upgrade_snapshot(old_snapshot):
            raise RuntimeError('RuntimeError in snapshot migration')

        @my_plugin.upgrade.snapshot('2020.2.2')
        def upgrade_snapshot(old_snapshot):
            raise RuntimeError('RuntimeError in snapshot migration')

        upgrade_request = platform_pb2.UpgradeRequest()
        upgrade_request.pre_upgrade_parameters.update(TEST_PRE_UPGRADE_PARAMS)
        upgrade_request.type = upgrade_request.SNAPSHOT
        upgrade_request.migration_ids.extend(MIGRATION_IDS)

        with pytest.raises(RuntimeError):
            my_plugin.upgrade._internal_snapshot(upgrade_request)
