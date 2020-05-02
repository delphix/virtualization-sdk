#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
from dlpx.virtualization.common.exceptions import (PlatformError,
                                                   PluginRuntimeError)


class UserError(Exception):
    """Plugin-raisable user exception

    Plugin authors can raise this exception in their code to fail the
    plugin operation. The message, action and output supplied by the
    plugin author will be shown in Delphix UI.

    All user-visible plugin raised exceptions should extend this.

    Args:
        message (str): A user-readable message describing the exception.
        action (str): Suggested action to be taken.
        output (str): Output to be shown.

    Attributes:
        message (str): A user-readable message describing the exception.
        action (str): Suggested action to be taken.
        output (str): Output to be shown.
    """
    @property
    def message(self):
        return self.args[0]

    def __init__(self, message, action='', output=''):
        super(UserError, self).__init__(message, action, output)


class IncorrectReturnTypeError(PluginRuntimeError):
    """IncorrectReturnTypeError gets thrown when an operation that was
    implemented by the plugin author returns an object type that is incorrect.

    Args:
        operation (Operation): The Operation enum of the operation being run
        actual_type (Type or List[Type]): type(s) returned from the operation
        expected_type (Type): The type of the parameter that was expected.

    Attributes:
        message (str): A localized user-readable message about what operation
            should be returning what type.

    """
    def __init__(self, operation, actual_type, expected_type):
        actual, expected = self.get_actual_and_expected_type(
            actual_type, expected_type)
        message = (
            'The returned object for the {} operation was {} but should be of'
            ' {}.'.format(operation.value, actual, expected))
        super(IncorrectReturnTypeError, self).__init__(message)


class IncorrectUpgradeObjectTypeError(PluginRuntimeError):
    """IncorrectUpgradeObjectTypeError gets thrown when an upgrade workflow was
    called with the incorrect object type to upgrade.

    Args:
        actual_type (platform_pb2.UpgradeRequest.Type): type that was passed in
        expected_type (platform_pb2.UpgradeRequest.Type): expected type

    Attributes:
        message (str): A localized user-readable message about what operation
            should be returning what type.

    """
    def __init__(self, actual_type, expected_type):
        message = (
            'The upgrade operation received objects with {} type but should'
            ' have had type {}.'.format(actual_type, expected_type))
        super(IncorrectUpgradeObjectTypeError, self).__init__(message)


class UnknownMigrationTypeError(PlatformError):
    """UnknownMigrationTypeError gets thrown when the migration type that is
    set on an upgrade migration decorator is not one of PLATFORM or LUA.

    Args:
        actual_type (MigrationType): type that was passed in

    Attributes:
        message (str): A localized user-readable message about what operation
            should be returning what type.

    """
    def __init__(self, actual_type, expected_type):
        message = (
            'The upgrade migrationType received was {} type which is not'
            ' supported.'.format(actual_type))
        super(UnknownMigrationTypeError, self).__init__(message)


class OperationAlreadyDefinedError(PlatformError):
    """OperationAlreadyDefinedError gets thrown when the plugin writer tries
    to define an operation more than ones.

    Args:
        operation (Operation): The Operation enum of the operation being run

    Attributes:
        message (str): A localized user-readable message about what operation
        should be returning what type.
    """
    def __init__(self, operation):
        message = ('An implementation for {} operation has already'
                   ' been defined.'.format(operation.value))
        super(OperationAlreadyDefinedError, self).__init__(message)


class OperationNotDefinedError(PlatformError):
    """OperationNotDefinedError gets thrown when the plugin wrapper tries to
    call the operation but it was not defined.

    Args:
        operation (Operation): The Operation enum of the operation being run

    Attributes:
        message (str): A localized user-readable message about what operation
        should be returning what type.
    """
    def __init__(self, operation):
        message = ('An implementation for the {} operation has not been'
                   ' defined.'.format(operation.value))
        super(OperationNotDefinedError, self).__init__(message)


class MigrationIdIncorrectTypeError(PlatformError):
    """MigrationIdIncorrectType gets thrown when the provided migration id is
    not a string.

    Args:
        migration_id (str): The migration id assigned for this operation
        function_name (str): The name of the function that used the
        decorator with the same migration id.

    Attributes:
        message (str): A localized user-readable message about what operation
        should be returning what type.
    """
    def __init__(self, migration_id, function_name):
        message = ("The migration id '{}' used in the function '{}' should"
                   " be a string.".format(migration_id, function_name))
        super(MigrationIdIncorrectTypeError, self).__init__(message)


class MigrationIdIncorrectFormatError(PlatformError):
    """MigrationIdIncorrectFormat gets thrown when the migration id given is
    not in the correct format. It should be one or more positive integers
    separated by periods.

    Args:
        migration_id (str): The migration id assigned for this operation
        function_name (str): The name of the function that used the
        decorator with the same migration id.
        format (str): The format expected of the migration_id.

    Attributes:
        message (str): A localized user-readable message about what operation
        should be returning what type.
    """
    def __init__(self, message):
        super(MigrationIdIncorrectFormatError, self).__init__(message)

    @classmethod
    def from_fields(cls, migration_id, function_name, format):
        message = ("The migration id '{}' used in the function '{}' does not"
                   " follow the correct format '{}'.".format(
                       migration_id, function_name, format))
        return cls(message)


class MigrationIdAlreadyUsedError(PlatformError):
    """MigrationIdAlreadyUsedError gets thrown when the same migration id is
    used for the same upgrade operation

    Args:
        migration_id (str): The migration id assigned for this operation
        function_name (str): The name of the function that used the
        decorator with the same migration id.

    Attributes:
        message (str): A localized user-readable message about what operation
        should be returning what type.
    """
    def __init__(self, message):
        super(MigrationIdAlreadyUsedError, self).__init__(message)

    @classmethod
    def fromMigrationId(cls, migration_id, std_migration_id, function_name):
        message = ("The migration id '{}' used in the function '{}' has the"
                   " same canonical form '{}' as another migration.".format(
                       migration_id, function_name, std_migration_id))
        return cls(message)

    @classmethod
    def fromLuaVersion(cls, migration_id, function_name, decorator_name):
        message = ("The lua major minor version '{}' used in the function"
                   " '{}' decorated by '{}' has already been used.".format(
                       migration_id, function_name, decorator_name))
        return cls(message)


class DecoratorNotFunctionError(PlatformError):
    """DecoratorNotFunctionError gets thrown when the decorated variable is
    not a function when it should be.

    Args:
        object_name (str): The name of the variable that should have been a
        decorator_name (str): The decorator that is being incorrectly used.

    Attributes:
        message (str): A localized user-readable message about what operation
        should be returning what type.
    """
    def __init__(self, object_name, decorator_name):
        message = ("The object '{}' decorated by '{}' is"
                   " not a function.".format(object_name, decorator_name))
        super(DecoratorNotFunctionError, self).__init__(message)


class IncorrectReferenceFormatError(PluginRuntimeError):
    """There are 2 possible errors that can be thrown with an incorrect
    reference. The reference passed in can be a non-string, throwing an
    IncorrectTypeError. The second error that can be thrown is
    IncorrectReferenceFormatError, which gets thrown when the reference is not
    of the format "UNIX_HOST_ENVIRONMENT-#" nor of
    "WINDOWS_HOST_ENVIRONMENT-#".

    Args:
        reference (str): The incorrectly formatted reference

    Attributes:
        message (str): A user-readable message describing the exception.
    """
    def __init__(self, reference):
        message = ("Reference '{}' is not a correctly formatted host"
                   " environment reference.".format(reference))
        super(IncorrectReferenceFormatError, self).__init__(message)


class IncorrectPluginCodeError(PluginRuntimeError):
    """
    This gets thrown if the import validations come across invalid plugin
    code that causes import to fail, or if the expected plugin entry point is
    not found in the plugin code.
        Args:
        message (str): A user-readable message describing the exception.

    Attributes:
        message (str): A user-readable message describing the exception.
    """
    @property
    def message(self):
        return self.args[0]

    def __init__(self, message):
        super(IncorrectPluginCodeError, self).__init__(message)
