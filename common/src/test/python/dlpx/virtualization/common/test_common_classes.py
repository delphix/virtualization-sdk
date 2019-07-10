#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import pytest
from dlpx.virtualization import common_pb2
from dlpx.virtualization.common._common_classes import (RemoteConnection, RemoteEnvironment, RemoteHost, RemoteUser)
from dlpx.virtualization.common.exceptions import IncorrectTypeError

@pytest.fixture
def remote_user():
    return RemoteUser("user", "user-reference")


@pytest.fixture
def remote_host():
    return RemoteHost("host", "host-reference", "binary_path", "scratch_path")


@pytest.fixture
def remote_environment(remote_host):
    return RemoteEnvironment("environment", "environment-reference", remote_host)


class TestRemoteConnection:
    @staticmethod
    def test_init_remote_connection_success(remote_user, remote_environment):
        RemoteConnection(remote_environment, remote_user)

    @staticmethod
    def test_init_remote_connection_incorrect_environment(remote_user):
        with pytest.raises(IncorrectTypeError) as err_info:
            RemoteConnection('', remote_user)
        assert err_info.value.message == (
            "RemoteConnection's parameter 'environment' was"
            " type 'str' but should be of class 'dlpx.virtualization"
            ".common._common_classes.RemoteEnvironment'.")

    @staticmethod
    def test_init_remote_connection_incorrect_user(remote_environment):
        with pytest.raises(IncorrectTypeError) as err_info:
            RemoteConnection(remote_environment, '')
        assert err_info.value.message == (
            "RemoteConnection's parameter 'user' was"
            " type 'str' but should be of class 'dlpx.virtualization"
            ".common._common_classes.RemoteUser'.")

    @staticmethod
    def test_remote_connection_to_proto(remote_user, remote_environment):
        remote_connection = RemoteConnection(remote_environment, remote_user)
        remote_connection_proto = remote_connection.to_proto()
        assert isinstance(remote_connection_proto, common_pb2.RemoteConnection)

    @staticmethod
    def test_remote_connection_from_proto_success():
        remote_conn_proto_buf = common_pb2.RemoteConnection()
        remote_conn = RemoteConnection.from_proto(remote_conn_proto_buf)
        assert isinstance(remote_conn, RemoteConnection)

    @staticmethod
    def test_remote_connection_from_proto_fail():
        with pytest.raises(IncorrectTypeError) as err_info:
            RemoteConnection.from_proto('')
        assert err_info.value.message == (
            "RemoteConnection's parameter 'connection' was"
            " type 'str' but should be of class 'dlpx.virtualization"
            ".common_pb2.RemoteConnection'.")


class TestRemoteEnvironment:
    @staticmethod
    def test_init_remote_environment_success(remote_host):
        RemoteEnvironment(name='name', reference='reference', host=remote_host)

    @staticmethod
    def test_init_remote_environment_incorrect_name(remote_host):
        with pytest.raises(IncorrectTypeError) as err_info:
            RemoteEnvironment(1, '', remote_host)
        assert err_info.value.message == (
            "RemoteEnvironment's parameter 'name' was"
            " type 'int' but should be of type 'basestring'.")

    @staticmethod
    def test_init_remote_environment_incorrect_reference(remote_host):
        with pytest.raises(IncorrectTypeError) as err_info:
            RemoteEnvironment('', 1, remote_host)
        assert err_info.value.message == (
            "RemoteEnvironment's parameter 'reference' was"
            " type 'int' but should be of type 'basestring'.")

    @staticmethod
    def test_init_remote_environment_incorrect_host():
        with pytest.raises(IncorrectTypeError) as err_info:
            RemoteEnvironment('', '', '')
        assert err_info.value.message == (
            "RemoteEnvironment's parameter 'host' was"
            " type 'str' but should be of class 'dlpx.virtualization"
            ".common._common_classes.RemoteHost'.")

    @staticmethod
    def test_remote_environment_to_proto(remote_host):
        remote_env = RemoteEnvironment('name', 'reference', remote_host)
        remote_env_proto = remote_env.to_proto()
        assert isinstance(remote_env_proto, common_pb2.RemoteEnvironment)

    @staticmethod
    def test_remote_environment_from_proto_success():
        remote_env_proto_buf = common_pb2.RemoteEnvironment()
        remote_env = RemoteEnvironment.from_proto(remote_env_proto_buf)
        assert isinstance(remote_env, RemoteEnvironment)

    @staticmethod
    def test_remote_environment_from_proto_fail():
        with pytest.raises(IncorrectTypeError) as err_info:
            RemoteEnvironment.from_proto('')
        assert err_info.value.message == (
            "RemoteEnvironment's parameter 'environment' was"
            " type 'str' but should be of class 'dlpx.virtualization"
            ".common_pb2.RemoteEnvironment'.")


class TestRemoteHost:
    @staticmethod
    def test_init_remote_host_success():
        RemoteHost(name='name',
                   reference='reference',
                   binary_path='binary_path',
                   scratch_path='scratch_path')

    @staticmethod
    def test_init_remote_host_incorrect_name():
        with pytest.raises(IncorrectTypeError) as err_info:
            RemoteHost(1, '', '', '')
        assert err_info.value.message == (
            "RemoteHost's parameter 'name' was"
            " type 'int' but should be of type 'basestring'.")

    @staticmethod
    def test_init_remote_host_incorrect_reference():
        with pytest.raises(IncorrectTypeError) as err_info:
            RemoteHost('', 1, '', '')
        assert err_info.value.message == (
            "RemoteHost's parameter 'reference' was"
            " type 'int' but should be of type 'basestring'.")

    @staticmethod
    def test_init_remote_host_incorrect_binary_path():
        with pytest.raises(IncorrectTypeError) as err_info:
            RemoteHost('', '', 1, '')
        assert err_info.value.message == (
            "RemoteHost's parameter 'binary_path' was"
            " type 'int' but should be of type 'basestring'.")

    @staticmethod
    def test_init_remote_host_incorrect_scratch_path():
        with pytest.raises(IncorrectTypeError) as err_info:
            RemoteHost('', '', '', 1)
        assert err_info.value.message == (
            "RemoteHost's parameter 'scratch_path' was"
            " type 'int' but should be of type 'basestring'.")

    @staticmethod
    def test_remote_host_to_proto_non_default():
        remote_host = RemoteHost('name', 'reference', 'binary_path', 'scratch_path')
        remote_host_proto = remote_host.to_proto()
        assert isinstance(remote_host_proto, common_pb2.RemoteHost)

    @staticmethod
    def test_remote_host_from_proto_success():
        remote_host_proto_buf = common_pb2.RemoteHost()
        remote_host = RemoteHost.from_proto(remote_host_proto_buf)
        assert isinstance(remote_host, RemoteHost)

    @staticmethod
    def test_remote_host_from_proto_fail():
        with pytest.raises(IncorrectTypeError) as err_info:
            RemoteHost.from_proto('')
        assert err_info.value.message == (
            "RemoteHost's parameter 'host' was"
            " type 'str' but should be of class 'dlpx.virtualization"
            ".common_pb2.RemoteHost'.")


class TestRemoteUser:
    @staticmethod
    def test_init_remote_user_success():
        RemoteUser(name='name', reference='reference')

    @staticmethod
    def test_init_remote_user_incorrect_name():
        with pytest.raises(IncorrectTypeError) as err_info:
            RemoteUser(1, '')
        assert err_info.value.message == (
            "RemoteUser's parameter 'name' was"
            " type 'int' but should be of type 'basestring'.")

    @staticmethod
    def test_init_remote_user_incorrect_reference():
        with pytest.raises(IncorrectTypeError) as err_info:
            RemoteUser('', 1)
        assert err_info.value.message == (
            "RemoteUser's parameter 'reference' was"
            " type 'int' but should be of type 'basestring'.")

    @staticmethod
    def test_remote_user_to_proto_non_default():
        remote_user = RemoteUser('name', 'reference')
        remote_user_proto = remote_user.to_proto()
        assert isinstance(remote_user_proto, common_pb2.RemoteUser)

    @staticmethod
    def test_remote_user_from_proto_success():
        remote_user_proto_buf = common_pb2.RemoteUser()
        remote_user = RemoteUser.from_proto(remote_user_proto_buf)
        assert isinstance(remote_user, RemoteUser)

    @staticmethod
    def test_remote_user_from_proto_fail():
        with pytest.raises(IncorrectTypeError) as err_info:
            RemoteUser.from_proto('')
        assert err_info.value.message == (
            "RemoteUser's parameter 'user' was"
            " type 'str' but should be of class 'dlpx.virtualization"
            ".common_pb2.RemoteUser'.")
