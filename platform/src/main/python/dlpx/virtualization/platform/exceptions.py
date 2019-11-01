#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
from dlpx.virtualization.common.exceptions import (
    PlatformError, PluginRuntimeError)


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
        actual type (Type or List[Type]): type(s) returned from the operation
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
