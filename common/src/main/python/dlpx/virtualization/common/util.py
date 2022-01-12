#
# Copyright (c) 2021 by Delphix. All rights reserved.
#


"""
Utility functions to convert between unicode and bytes.
"""

import six


def to_bytes(string, encoding="utf-8"):
    """
    Converts the given object to binary object, bytes (Py3) or str (Py2).

    :param string: The string like object to convert to bytes
    :type string: ``object``
    :param encoding: The encoding to encode the string with.
    :type encoding: ``str``
    :returns: The encoded string.
    :rtype: ``bytes``
    """
    if string is None:
        return

    if isinstance(string, dict):
        for k, v in string.items():
            string[k] = to_bytes(v, encoding=encoding)
        return string

    if isinstance(string, list):
        return [to_bytes(i, encoding=encoding) for i in string]

    if isinstance(string, set):
        return {to_bytes(i, encoding=encoding) for i in string}

    if isinstance(string, str):
        return _to_bytes(string, encoding)

    return string


def _to_bytes(string, encoding):
    if six.PY3:
        if isinstance(string, str):
            return string.encode(encoding)
        else:
            return bytes(string)
    else:
        if isinstance(string, unicode):  # noqa
            return string.encode(encoding)
        else:
            return str(string)


def to_str(b, encoding="utf-8"):
    """
    Converts the given object to a text object, unicode (Py2) or str (Py3).

    :param b: The object to convert
    :type b: ``object``
    :param encoding: The encoding to encode the string with.
    :type encoding: ``str``
    :returns: The decoded string.
    :rtype: ``str``
    """
    if b is None:
        return

    if isinstance(b, dict):
        for k, v in b.items():
            b[k] = to_str(v, encoding=encoding)
        return b

    if isinstance(b, list):
        return [to_str(i, encoding=encoding) for i in b]

    if isinstance(b, set):
        return {to_str(i, encoding=encoding) for i in b}

    if isinstance(b, bytes):
        return _to_str(b, encoding=encoding)
    return b


def _to_str(b, encoding):
    if six.PY3:
        if isinstance(b, bytes):
            try:
                return str(b, encoding)
            except UnicodeDecodeError:
                pass
            raise UnicodeError(
                "Could not decode value with encoding {}".format(encoding)
            )
        else:
            return b
    else:
        if isinstance(b, str):
            try:
                return b.decode(encoding)
            except UnicodeDecodeError:
                pass
            raise UnicodeError(
                "Could not decode value with encoding {}".format(encoding)
            )
        return b


def response_to_str(response):
    """
    The response_to_str function ensures all relevant properties of the given
    response are unicode (py2) / str (py3). Should be called on a response as
    soon as it is received.

    Args:
        response (RunPowerShellResponse or RunBashResponse or RunExpectResponse):
        Response received by run_bash or run_powershell or run_expect
    """
    if response.HasField("return_value"):
        if hasattr(response.return_value, "stdout"):
            response.return_value.stdout = to_str(response.return_value.stdout)
        if hasattr(response.return_value, "stderr"):
            response.return_value.stderr = to_str(response.return_value.stderr)
