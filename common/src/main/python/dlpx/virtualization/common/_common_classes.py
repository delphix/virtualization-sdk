#
# Copyright (c) 2019, 2022 by Delphix. All rights reserved.
#

from abc import ABCMeta
import six
from dlpx.virtualization.api import common_pb2, libs_pb2
from dlpx.virtualization.common.exceptions import IncorrectTypeError

"""Classes used for Plugin Operations

This module defines the non autogenerated classes used as input/output for
plugin operations. These are used instead of protobuf generated classes to
hide the implemenatation details for protobufs and also to provide the
correct types.
"""

__all__ = [
    "RemoteConnection",
    "RemoteEnvironment",
    "RemoteHost",
    "RemoteUser",
    "Credentials",
    "PasswordCredentials",
    "KeyPairCredentials"]


class RemoteConnection(object):
    """Plugin class for RemoteConnection to be used for plugin operations
    and library functions.

    Plugin authors should use this instead of corresponding protobuf generated
    class.

    Args:
        environment: RemoteEnvironment of this RemoteConnection.
        user: RemoteUser of this RemoteConnection.

    """
    def __init__(self, environment, user):
        if isinstance(environment, RemoteEnvironment):
            self.__environment = environment
        else:
            raise IncorrectTypeError(
                RemoteConnection,
                'environment',
                type(environment),
                RemoteEnvironment)

        if isinstance(user, RemoteUser):
            self.__user = user
        else:
            raise IncorrectTypeError(
                RemoteConnection,
                'user',
                type(user),
                RemoteUser)

    @property
    def environment(self):
        return self.__environment

    @property
    def user(self):
        return self.__user

    def to_proto(self):
        """Converts plugin class RemoteConnection to protobuf class
        common_pb2.RemoteConnection
        """
        remote_connection = common_pb2.RemoteConnection()
        remote_connection.environment.CopyFrom(self.environment.to_proto())
        remote_connection.user.CopyFrom(self.user.to_proto())
        return remote_connection

    @staticmethod
    def from_proto(connection):
        """Converts protobuf class common_pb2.RemoteConnection to plugin class
        RemoteConnection
        """
        if not isinstance(connection, common_pb2.RemoteConnection):
            raise IncorrectTypeError(
                RemoteConnection,
                'connection',
                type(connection),
                common_pb2.RemoteConnection)
        environment = RemoteEnvironment.from_proto(connection.environment)
        user = RemoteUser.from_proto(connection.user)
        return RemoteConnection(environment=environment, user=user)


class RemoteEnvironment(object):
    """Plugin class for RemoteEnvironment to be used for plugin operations
    and library functions.

    Plugin authors should use this instead of corresponding protobuf generated
    class.

    Args:
        name: Name of the RemoteEnvironment.
        reference: Reference of the RemoteEnvironment.
        host: RemoteHost of the RemoteEnvironment.

    """
    def __init__(self, name, reference, host):
        if not isinstance(name, six.string_types):
            raise IncorrectTypeError(
                RemoteEnvironment,
                'name',
                type(name),
                six.string_types[0])
        self.__name = name
        if not isinstance(reference, six.string_types):
            raise IncorrectTypeError(
                RemoteEnvironment,
                'reference',
                type(reference),
                six.string_types[0])
        self.__reference = reference

        if isinstance(host, RemoteHost):
            self.host = host
        else:
            raise IncorrectTypeError(
                RemoteEnvironment,
                'host',
                type(host),
                RemoteHost)

    @property
    def name(self):
        return self.__name

    @property
    def reference(self):
        return self.__reference

    def to_proto(self):
        """
        Converts plugin class RemoteEnvironment to protobuf
        class common_pb2.RemoteEnvironment
        """
        remote_environment = common_pb2.RemoteEnvironment()
        remote_environment.name = self.name
        remote_environment.reference = self.reference
        remote_environment.host.CopyFrom(self.host.to_proto())
        return remote_environment

    @staticmethod
    def from_proto(environment):
        """
        Converts protobuf class common_pb2.RemoteEnvironment to plugin
        class RemoteEnvironment
        """
        if not isinstance(environment, common_pb2.RemoteEnvironment):
            raise IncorrectTypeError(
                RemoteEnvironment,
                'environment',
                type(environment),
                common_pb2.RemoteEnvironment)
        return RemoteEnvironment(name=environment.name,
                                 reference=environment.reference,
                                 host=RemoteHost.from_proto(environment.host))


class RemoteHost(object):
    """Plugin class for RemoteHost to be used for plugin operations
    and library functions.

    Plugin authors should use this instead of corresponding protobuf generated
    class.

    Args:
        name: Name of the RemoteHost.
        reference: Reference of the RemoteHost.
        binary_path: binary path of the RemoteHost.
        scratch_path: scratch path of the RemoteHost.

    """
    def __init__(self, name, reference, binary_path, scratch_path):
        if not isinstance(name, six.string_types):
            raise IncorrectTypeError(
                RemoteHost,
                'name',
                type(name),
                six.string_types[0])
        self.__name = name
        if not isinstance(reference, six.string_types):
            raise IncorrectTypeError(
                RemoteHost,
                'reference',
                type(reference),
                six.string_types[0])
        self.__reference = reference
        if not isinstance(binary_path, six.string_types):
            raise IncorrectTypeError(
                RemoteHost,
                'binary_path',
                type(binary_path),
                six.string_types[0])
        self.__binary_path = binary_path
        if not isinstance(scratch_path, six.string_types):
            raise IncorrectTypeError(
                RemoteHost,
                'scratch_path',
                type(scratch_path),
                six.string_types[0])
        self.__scratch_path = scratch_path

    @property
    def name(self):
        return self.__name

    @property
    def reference(self):
        return self.__reference

    @property
    def binary_path(self):
        return self.__binary_path

    @property
    def scratch_path(self):
        return self.__scratch_path

    def to_proto(self):
        """Converts plugin class RemoteHost to protobuf class common_pb2.RemoteHost
        """
        remote_host = common_pb2.RemoteHost()
        remote_host.name = self.name
        remote_host.reference = self.reference
        remote_host.binary_path = self.binary_path
        remote_host.scratch_path = self.scratch_path
        return remote_host

    @staticmethod
    def from_proto(host):
        """Converts protobuf class common_pb2.RemoteHost to plugin class RemoteHost
        """
        if not isinstance(host, common_pb2.RemoteHost):
            raise IncorrectTypeError(
                RemoteHost,
                'host',
                type(host),
                common_pb2.RemoteHost)
        return RemoteHost(name=host.name,
                          reference=host.reference,
                          binary_path=host.binary_path,
                          scratch_path=host.scratch_path)


class RemoteUser(object):
    """Plugin class for RemoteUser to be used for plugin operations
    and library functions.

    Plugin authors should use this instead of corresponding protobuf generated
    class.

    Args:
        name: Name of the RemoteUser.
        reference: Reference of the RemoteUser.
    """
    def __init__(self, name, reference):
        if not isinstance(name, six.string_types):
            raise IncorrectTypeError(
                RemoteUser,
                'name',
                type(name),
                six.string_types[0])
        self.__name = name
        if not isinstance(reference, six.string_types):
            raise IncorrectTypeError(
                RemoteUser,
                'reference',
                type(reference),
                six.string_types[0])
        self.__reference = reference

    @property
    def name(self):
        return self.__name

    @property
    def reference(self):
        return self.__reference

    def to_proto(self):
        """Converts plugin class RemoteUser to protobuf class common_pb2.RemoteUser
        """
        remote_user = common_pb2.RemoteUser()
        remote_user.name = self.name
        remote_user.reference = self.reference
        return remote_user

    @staticmethod
    def from_proto(user):
        """Converts protobuf class common_pb2.RemoteUser to plugin class RemoteUser
        """
        if not isinstance(user, common_pb2.RemoteUser):
            raise IncorrectTypeError(
                RemoteUser,
                'user',
                type(user),
                common_pb2.RemoteUser)
        remote_user = RemoteUser(name=user.name, reference=user.reference)
        return remote_user


class Credentials(object):
    """Plugin base class for CredentialsResult to be used for plugin operations
    and library functions.

    Plugin authors should use this instead of the corresponding protobuf generated
    class.

    Args:
        username: User name.
    """
    def __init__(self, username):
        if not isinstance(username, six.string_types):
            raise IncorrectTypeError(
                Credentials,
                'username',
                type(username),
                six.string_types[0])
        self.__username = username

    __metaclass__ = ABCMeta

    @property
    def username(self):
        return self.__username


class PasswordCredentials(Credentials):
    """Plugin class for CredentialsResult with password to be used for plugin operations
    and library functions.

    Plugin authors should use this instead of the corresponding protobuf generated
    class.

    Args:
        username: User name.
        password: Password.
    """
    def __init__(self, username, password):
        super(PasswordCredentials, self).__init__(username)
        if not isinstance(password, six.string_types):
            raise IncorrectTypeError(
                PasswordCredentials,
                'password',
                type(password),
                six.string_types[0])
        self.__password = password

    @property
    def password(self):
        return self.__password

    @staticmethod
    def from_proto(credentials_result):
        """
        Converts protobuf class libs_pb2.CredentialsResult to plugin
        class PasswordCredentials
        """
        if not isinstance(credentials_result, libs_pb2.CredentialsResult):
            raise IncorrectTypeError(
                PasswordCredentials,
                'credentials_result',
                type(credentials_result),
                libs_pb2.CredentialsResult)
        return PasswordCredentials(
            username=credentials_result.username, password=credentials_result.pasword)


class KeyPairCredentials(Credentials):
    """Plugin class for CredentialsResult with key pair to be used for plugin operations
    and library functions.

    Plugin authors should use this instead of the corresponding protobuf generated
    class.

    Args:
        username (str): User name.
        private_key (str): Private key.
        public_key (str): Public key corresponding to private key. Empty string if
            not present.
    """
    def __init__(self, username, private_key, public_key):
        super(KeyPairCredentials, self).__init__(username)
        if not isinstance(private_key, six.string_types):
            raise IncorrectTypeError(
                KeyPairCredentials,
                'private_key',
                type(private_key),
                six.string_types[0])
        self.__private_key = private_key
        if not isinstance(public_key, six.string_types):
            raise IncorrectTypeError(
                KeyPairCredentials,
                'public_key',
                type(public_key),
                six.string_types[0])
        self.__public_key = public_key

    @property
    def private_key(self):
        return self.__private_key

    @property
    def public_key(self):
        return self.__public_key

    @staticmethod
    def from_proto(credentials_result):
        """Converts protobuf class libs_pb2.CredentialsResult to plugin class
        KeyPairCredentials
        """
        if not isinstance(credentials_result, libs_pb2.CredentialsResult):
            raise IncorrectTypeError(
                KeyPairCredentials,
                'credentials_result',
                type(credentials_result),
                libs_pb2.CredentialsResult)
        return KeyPairCredentials(
            username=credentials_result.username,
            private_key=credentials_result.key_pair.private_key,
            public_key=credentials_result.key_pair.public_key)
