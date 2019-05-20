#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
from dlpx.virtualization.common.exceptions import (
    PlatformError, PluginRuntimeError)


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


class IncorrectTypeError(PluginRuntimeError):
    """IncorrectTypeError gets thrown when defined plugin class's parameter
     has an incorrect type.

    Args:
        object (class): the class object being initialized
        parameter_name (str): The name of the param being passed in
        actual type (Type or List[Type]): type(s) that was actually passed in
            for the parameter
        expected_type (Type): The type of the parameter that is expected.
        required (bool): If the parameter is required (doesn't have a default)

    Attributes:
        message (str): A user-readable message describing the exception.
    """

    def __init__(
        self,
        object_type,
        parameter_name,
        actual_type,
        expected_type,
        required=True):
        actual, expected = self.get_actual_and_expected_type(
            actual_type, expected_type)

        message = ("{}'s parameter '{}' was {} but should be of {}{}.".format(
            object_type.__name__,
            parameter_name,
            actual,
            expected,
            (' if defined', '')[required]))
        super(IncorrectTypeError, self).__init__(message)


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
