#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import sys
from dlpx.virtualization.common.exceptions import PluginRuntimeError


class LibraryError(Exception):
    """Plugin-catchable exception

    Some library errors (timeouts, host unreachable, etc.) are potentially
    actionable by plugin code. For example, they may choose to retry, or to
    raise their own plugin-specific exception.

    This exception will be thrown whenever a library call fails due to such an
    actionable error.

    Attributes:
    message - A localized user-readable message.
    """

    @property
    def message(self):
        return self.args[0]

    def __init__(self, id, message):
        self._id = id
        super(LibraryError, self).__init__(message)


class PluginScriptError(Exception):
    """Plugin-catchable exception

    This exception will be thrown whenever a library call is made with check=True
    and it returns a non-zero exit code.

    This can be handy for plugin author who
    chooses to catch exceptions explicitly than checking the exit code of response.

    Attributes:
    message - A localized user-readable message.
    """

    @property
    def message(self):
        return self.args[0]

    def __init__(self, message):
        super(PluginScriptError, self).__init__(message)


class IncorrectArgumentTypeError(PluginRuntimeError):
    """IncorrectArgumentTypeError is thrown when a library function gets
    called with an argument that has an incorrect type.

    Args:
        func (function): The library function being called
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
        parameter_name,
        actual_type,
        expected_type,
        required=True):
        actual, expected = self.get_actual_and_expected_type(
            actual_type, expected_type)

        # Get the name of the function that is throwning this error.
        func_name = sys._getframe(1).f_code.co_name
        message = ("The function {}'s argument '{}' was {} but should"
                   " be of {}{}.".format(
            func_name,
            parameter_name,
            actual,
            expected,
            (' if defined', '')[required]))
        super(IncorrectArgumentTypeError, self).__init__(message)
