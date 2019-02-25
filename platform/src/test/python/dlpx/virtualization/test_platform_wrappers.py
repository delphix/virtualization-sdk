#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import json
import mock
import unittest
from dlpx.virtualization import platform_pb2
from dlpx.virtualization.platform import platform_wrappers


class TestWrappers(unittest.TestCase):
    def test_configure_wrapper(self):
        def mock_configure(source, repository, snapshot):
            return SourceConfig("TestRepository", "TestSnapshot", "TestDB")

        with mock.patch('dlpx.virtualization.platform.platform_wrappers.configure',
                        side_effect=mock_configure, create=True):
            configure_request = platform_pb2.ConfigureRequest()
            configure_request.repository.parameters.json = "TestRepository"
            configure_request.snapshot.parameters.json = "TestSnapshot"
            configure_request.source.parameters.json = "TestDB"

            config_response = platform_wrappers.configure_wrapper(configure_request)
            expected_source_config = SourceConfig("TestRepository", "TestSnapshot", "TestDB").to_json()

            assert(config_response.return_value.source_config.parameters.json == expected_source_config)

    def test_repository_discovery_wrapper(self):
        def mock_repository_discovery(source_connection):
            return [Repository("TestRepository1"), Repository("TestRepository2")]

        with mock.patch('dlpx.virtualization.platform.platform_wrappers.repository_discovery',
                        side_effect=mock_repository_discovery, create=True):
            repository_discovery_request = platform_pb2.RepositoryDiscoveryRequest()
            repository_discovery_request.source_connection.environment.name = "TestEnvironment"
            repository_discovery_request.source_connection.user.name = "TestUser"

            repository_discovery_response = platform_wrappers.repository_discovery_wrapper(repository_discovery_request)

            for repository, expected_repository \
                    in zip(repository_discovery_response.return_value.repositories, Repositories.to_json()):
                repository_json = repository.parameters.json
                # protobuf json strings are in unicode, so cast to string
                assert(str(repository_json) == expected_repository)

    def test_source_config_discovery_wrapper(self):
        def mock_source_config_discovery(source_connection, repository):
            return [SourceConfig("TestRepository1", "TestSnapshot1", "TestDB1"),
                    SourceConfig("TestRepository2", "TestSnapshot2", "TestDB2")]

        with mock.patch('dlpx.virtualization.platform.platform_wrappers.source_config_discovery',
                        side_effect=mock_source_config_discovery, create=True):
            source_config_discovery_request = platform_pb2.SourceConfigDiscoveryRequest()
            source_config_discovery_request.source_connection.environment.name = "TestEnvironment"
            source_config_discovery_request.source_connection.user.name = "TestUser"
            source_config_discovery_request.repository.parameters.json = "TestRepository"

            source_config_discovery_response = \
                platform_wrappers.source_config_discovery_wrapper(source_config_discovery_request)

            for source_config, expected_source_config \
                    in zip(source_config_discovery_response.return_value.source_configs, SourceConfigs.to_json()):
                source_config_json = source_config.parameters.json
                # protobuf json strings are in unicode, so cast to string
                assert(str(source_config_json) == expected_source_config)


class Repository:
    def __init__(self, repository_name):
        self.inner_map = {"name": repository_name}

    def to_json(self):
        return json.dumps(self.inner_map)


class SourceConfig:
    def __init__(self, repository, snapshot, source):
        self.inner_map = {"repository": repository, "snapshot": snapshot, "source": source}

    def to_json(self):
        return json.dumps(self.inner_map)


class Repositories:
    @staticmethod
    def to_json():
        return [json.dumps({"name": "TestRepository1"}), json.dumps({"name": "TestRepository2"})]


class SourceConfigs:
    @staticmethod
    def to_json():
        return [json.dumps({"repository": "TestRepository1", "snapshot": "TestSnapshot1", "source": "TestDB1"}),
                json.dumps({"repository": "TestRepository2", "snapshot": "TestSnapshot2", "source": "TestDB2"})]
