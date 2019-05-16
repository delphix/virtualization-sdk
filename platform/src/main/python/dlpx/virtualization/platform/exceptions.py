#
# Copyright (c) 2019 by Delphix. All rights reserved.
#


class PlatformError(Exception):
    """This error should be converted and thrown as a Delphix Fatal exception
    if it gets converted through protobuf.

    Some Platform specific errors (operations not implemented errors,
    specifically) should have been validated already and points to a Delphix
    Engine bug.

    Args:
        message (str): A user-readable message describing the exception.

    Attributes:
        message (str): A user-readable message describing the exception.
    """

    @property
    def message(self):
        return self.args[0]

    def __init__(self, message):
        super(PlatformError, self).__init__(message)


class PluginRuntimeError(Exception):
    """Plugin-catchable exception

    Some Plugin specific errors (type errors, etc.) need to be fixed via the
    plugin code. Potentially actionable by plugin code.

    This exception will be thrown whenever a Platform call fails due to such an
    actionable error.

    Args:
        message (str): A user-readable message describing the exception.

    Attributes:
        message (str): A user-readable message describing the exception.
    """

    @property
    def message(self):
        return self.args[0]

    def __init__(self, message):
        super(PluginRuntimeError, self).__init__(message)


class IncorrectTypeError(PluginRuntimeError):
    """IncorrectTypeError gets thrown when defined plugin class's parameter
     has an incorrect type.

    Args:
        object_type (Type): the type of the object being initialized
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
        actual, expected = _get_actual_and_expected_type(
            actual_type, expected_type)

        message = ("{}'s parameter '{}' was {} but should be of {}{}.".format(
            object_type.__name__,
            parameter_name,
            actual,
            expected,
            (' if defined', '')[required]))
        super(IncorrectTypeError, self).__init__(message)


class IncorrectReturnTypeError(PluginRuntimeError):
    """IncorrectReturnTypeError gets thrown when an operation that was
    implemented by the plugin author returns an object type that is incorrect.

    Args:
        operation (Operation): The Operation enum of the operation being run
        actual type (Type or List[Type]): type(s) returned from the operation
        expected_type (Type): The type of the parameter that was expected.

    Attributes:
    message - A localized user-readable message about what operation should be
    returning what type.

    """

    def __init__(self, operation, actual_type, expected_type):
        actual, expected = _get_actual_and_expected_type(
            actual_type, expected_type)
        message = (
            'The returned object for the {} operation was {} but should be of'
            ' {}.'.format(operation.value, actual, expected))
        super(IncorrectReturnTypeError, self).__init__(message)


def _get_actual_and_expected_type(actual_type, expected_type):
    """ Takes in the the actual and expected types and generates a tuple of
    two strings that are then used to generate the output message.

    Args:
        actual_type (Type or List[Type]): type(s) that was actually passed in
            for the parameter. this will either take the type and make it a
            str or join the types as a string and put it in brackets
        expected_type (Type or List[Type]): The type of the parameter that was
            expected. Or if this is a list then we assume there is one element
            in the list and that type is the expected type in a list. ie if
            expected_type = [str] then the returned expected string with be
            something like <type 'list of str'>

    Returns:
        tuple:
    """
    def _remove_triangle_brackets(type_string):
        return type_string.replace('<', '').replace('>', '')

    if isinstance(expected_type, list):
        if len(expected_type) != 1:
            raise PlatformError('The thrown TypeError should have had a list'
                                ' of size 1 as the expected_type')
        single_type = expected_type[0]
        if single_type.__module__ != '__builtin__':
            type_name = '{}.{}'.format(
                single_type.__module__, single_type.__name__)
        else:
            type_name = single_type.__name__
        expected = "type 'list of {}'".format(type_name)
    else:
        expected = _remove_triangle_brackets(str(expected_type))

    if isinstance(actual_type, list):
        actual = 'a list of [{}]'.format(
            ', '.join(_remove_triangle_brackets(str(single_type))
                      for single_type in actual_type))
    else:
        actual = _remove_triangle_brackets(str(actual_type))

    return actual, expected


class OperationAlreadyDefinedError(PlatformError):
    """OperationAlreadyDefinedError gets thrown when the plugin writer tries
    to define an operation more than ones.

    Args:
        operation (Operation): The Operation enum of the operation being run

    Attributes:
    message - A localized user-readable message about what operation should be
    returning what type.
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
    message - A localized user-readable message about what operation should be
    returning what type.
    """
    def __init__(self, operation):
        message = ('An implementation for the {} operation has not been'
                   ' defined.'.format(operation.value))
        super(OperationNotDefinedError, self).__init__(message)
