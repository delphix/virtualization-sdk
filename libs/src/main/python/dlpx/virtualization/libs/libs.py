# Copyright (c) 2019, 2021 by Delphix. All rights reserved.
#

# -*- coding: utf-8 -*-
"""Virtualization Libs API wrappers.

This module contains all Virtualization Libs API wrappers (for details on
the API definition, see libs/src/proto/libs.proto).

The wrappers are the implementation of the Virtualization Libs API. They take a
number of arguments for a certain operation, construct a <OperationName>Request
protobuf message as input, and and return <OperationName>Response,
e.g. RunBashRequest and RunBashResponse. The wrappers are called by the toolkit
code and their role is to pack input arguments into a *Request protobuf message,
and invoke a Delphix Engine method that has implementation for the requested
libs operation. The wrappers assume that the Python runtime will have a
virtualization libs interface (a client stub) injected into the namespace such
that one can invoke libs.run_bash(run_bash_request). In Jython, that
object will in fact be a Java object that will delegate to a Java implementation
of a lib operation.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import sys

from dlpx.virtualization.api import libs_pb2
from dlpx.virtualization.libs.exceptions import (IncorrectArgumentTypeError,
                                                 LibraryError,
                                                 PluginScriptError)
from dlpx.virtualization.common._common_classes import (RemoteConnection,
                                                        PasswordCredentials,
                                                        KeyPairCredentials)
from dlpx.virtualization.common.util import response_to_str, to_str
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Struct

import logging
import six


__all__ = [
    "run_bash",
    "run_sync",
    "run_powershell",
    "run_expect",
    "retrieve_credentials",
    "upgrade_password"
]


def _handle_response(response):
    """This function handles callback responses. It proceeds differently based
    on what the response reported...

    All of our callback response types have one of these three setups:
    - If there was a successful callback, this method returns the return value
      ("result") of the callback
    - If there was an actionable error, this method will throw a LibraryError,
      which the plugin may choose to catch
    - If there was a non-actionable error, this method calls exit()
    """
    if response.HasField("error"):
        if response.error.HasField("actionable_error"):
            actionable = response.error.actionable_error
            # Give the plugin a chance to catch/handle this problem
            raise LibraryError(actionable.id, actionable.message)

        # Nothing the plugin can do, so quit ASAP
        sys.exit()

    # Unpack the return value from the response
    return response.return_value


def _check_exit_code(response, check):
    """
    This functions checks the exitcode received in response and throws
    PluginScriptError if check is True.

    Args:
    response (RunPowerShellResponse or RunBashResponse or RunExpectResponse): Response
        received by run_bash or run_powershell or run_expect
    check (bool): if True and non-zero exitcode is received in response, raise
        PluginScriptError
    """
    if (check and response.HasField('return_value')
            and response.return_value.exit_code != 0):
        raise PluginScriptError('The script failed with exit code {}.'
                                ' stdout : {} and '
                                ' stderr : {}'.format(
                                      response.return_value.exit_code,
                                      response.return_value.stdout,
                                      response.return_value.stderr))


def run_bash(remote_connection, command, variables=None, use_login_shell=False,
             check=False):
    """run_bash operation wrapper.

    The run_bash function executes a shell command or script on a remote Unix
    environment using the shell binary shipped in the Delphix Engine on the
    environment. The specified environment user executes this logic from their
    home directory. The Delphix Engine captures and logs all output to stdout
    and stderr from this command. If the function fails, the output is
    displayed in the Delphix Management application and CLI to aid in
    debugging.

    If successful, the executed logic must exit with an exit code of 0. All
    other exit codes are treated as a function failure.

    Args:
        remote_connection (RemoteConnection): Connection to a remote
        environment.
        command (str): Bash command to run.
        variables (dict of str:str): Environment variables to set before
        running the command.
        use_login_shell (bool): Whether to use login shell.
        check (bool): if True and non-zero exitcode is received, raise PluginScriptError

    Returns:
        RunBashResponse: The return value of run_bash operation.
    """
    #
    # Since this import only resolves at runtime, we keep it in the function
    # scope to allow unit testing of this module.
    #
    from dlpx.virtualization._engine import libs as internal_libs

    if variables is None:
        variables = {}
    command = to_str(command)
    variables = to_str(variables)

    # Validate all the arguments passed in are the right types based on docs.
    if not isinstance(remote_connection, RemoteConnection):
        raise IncorrectArgumentTypeError(
            'remote_connection',
            type(remote_connection),
            RemoteConnection)
    if not isinstance(command, six.string_types):
        raise IncorrectArgumentTypeError('command', type(command), six.string_types[0])
    if variables and not isinstance(variables, dict):
        raise IncorrectArgumentTypeError(
            'variables',
            type(variables),
            {six.string_types[0]: six.string_types[0]},
            False)
    if (variables and (not all(isinstance(variable, six.string_types)
                               for variable in variables.keys()) or
                       not all(isinstance(value, six.string_types)
                               for value in variables.values()))):
        raise IncorrectArgumentTypeError(
            'variables',
            {(type(variable), type(value))
             for variable, value in variables.items()},
            {six.string_types[0]: six.string_types[0]},
            False)
    if use_login_shell and not isinstance(use_login_shell, bool):
        raise IncorrectArgumentTypeError(
            'use_login_shell', type(use_login_shell), bool, False)

    run_bash_request = libs_pb2.RunBashRequest()
    run_bash_request.remote_connection.CopyFrom(remote_connection.to_proto())
    run_bash_request.command = command
    run_bash_request.use_login_shell = use_login_shell
    for variable, value in variables.items():
        run_bash_request.variables[variable] = value

    run_bash_response = internal_libs.run_bash(run_bash_request)
    response_to_str(run_bash_response)
    _check_exit_code(run_bash_response, check)
    return _handle_response(run_bash_response)


def run_sync(remote_connection, source_directory, rsync_user=None,
             exclude_paths=None, sym_links_to_follow=None):
    """run_sync operation wrapper.

     The run_sync function copies files from the remote source host directly
     into the dSource, without involving a staging host.

    Args:
        remote_connection (RemoteConnection): Connection to a remote
        environment.
        source_directory (str): Directory of files to be synced.
        rsync_user (str): User who has access to the directory to be synced.
        exclude_paths (list of str): Paths to be excluded.
        sym_links_to_follow (list of str): Sym links to follow if any.
    """

    #
    # Since this import only resolves at runtime, we keep it in the function
    # scope to allow unit testing of this module.
    #

    from dlpx.virtualization._engine import libs as internal_libs

    source_directory = to_str(source_directory)
    if rsync_user is not None:
        rsync_user = to_str(rsync_user)
    if exclude_paths is not None:
        exclude_paths = to_str(exclude_paths)
    if sym_links_to_follow is not None:
        sym_links_to_follow = to_str(sym_links_to_follow)

    # Validate all the arguments passed in are the right types based on docs.
    if not isinstance(remote_connection, RemoteConnection):
        raise IncorrectArgumentTypeError(
            'remote_connection',
            type(remote_connection),
            RemoteConnection)
    if not isinstance(source_directory, six.string_types):
        raise IncorrectArgumentTypeError(
            'source_directory', type(source_directory), six.string_types[0])
    if rsync_user and not isinstance(rsync_user, six.string_types):
        raise IncorrectArgumentTypeError(
            'rsync_user',
            type(rsync_user),
            six.string_types[0],
            False)
    if exclude_paths and not isinstance(exclude_paths, list):
        raise IncorrectArgumentTypeError(
            'exclude_paths',
            type(exclude_paths),
            [six.string_types[0]],
            False)
    if (exclude_paths and not all(isinstance(
            path, six.string_types) for path in exclude_paths)):
        raise IncorrectArgumentTypeError(
            'exclude_paths',
            [type(path) for path in exclude_paths],
            [six.string_types[0]],
            False)
    if sym_links_to_follow and not isinstance(sym_links_to_follow, list):
        raise IncorrectArgumentTypeError(
            'sym_links_to_follow',
            type(sym_links_to_follow),
            [six.string_types[0]],
            False)
    if (sym_links_to_follow and not all(isinstance(link, six.string_types)
                                        for link in sym_links_to_follow)):
        raise IncorrectArgumentTypeError(
            'sym_links_to_follow',
            [type(link) for link in sym_links_to_follow],
            [six.string_types[0]],
            False)

    run_sync_request = libs_pb2.RunSyncRequest()
    run_sync_request.remote_connection.CopyFrom(remote_connection.to_proto())
    run_sync_request.source_directory = source_directory
    if rsync_user is not None:
        run_sync_request.rsync_user = rsync_user
    if exclude_paths is not None:
        run_sync_request.exclude_paths.extend(exclude_paths)
    if sym_links_to_follow is not None:
        run_sync_request.sym_links_to_follow.extend(sym_links_to_follow)

    response = internal_libs.run_sync(run_sync_request)
    response_to_str(response)
    _handle_response(response)


def run_powershell(remote_connection, command, variables=None, check=False):
    """run_powershell operation wrapper.

    The run_powershell function executes a powershell command or script on a
    remote windows environment using the binary in the environment. The
    specified environment user executes this logic from their
    home directory. The Delphix Engine captures and logs all output to stdout
    and stderr from this command. If the function fails, the output is
    displayed in the Delphix Management application and CLI to aid in
    debugging.

    If successful, the executed logic must exit with an exit code of 0. All
    other exit codes are treated as a function failure.

    Args:
        remote_connection (RemoteConnection): Connection to a remote
        environment.
        command (str): Powershell script to run.
        variables (dict): Environment variables to set before running the
        command.
        check (bool): if True and non-zero exitcode is received, raise PluginScriptError

    Returns:
        RunPowerShellResponse: The return value of run_powershell operation.
    """
    #
    # Since this import only resolves at runtime, we keep it in the function
    # scope to allow unit testing of this module.
    #
    from dlpx.virtualization._engine import libs as internal_libs

    if variables is None:
        variables = {}

    command = to_str(command)
    variables = to_str(variables)

    # Validate all the arguments passed in are the right types based on docs.
    if not isinstance(remote_connection, RemoteConnection):
        raise IncorrectArgumentTypeError(
            'remote_connection',
            type(remote_connection),
            RemoteConnection)
    if not isinstance(command, six.string_types):
        raise IncorrectArgumentTypeError('command', type(command), six.string_types[0])
    if variables and not isinstance(variables, dict):
        raise IncorrectArgumentTypeError(
            'variables',
            type(variables),
            {six.string_types[0]: six.string_types[0]},
            False)
    if (variables and (not all(isinstance(variable, six.string_types)
                               for variable in variables.keys()) or
                       not all(isinstance(value, six.string_types)
                               for value in variables.values()))):
        raise IncorrectArgumentTypeError(
            'variables',
            {(type(variable), type(value))
             for variable, value in variables.items()},
            {six.string_types[0]: six.string_types[0]},
            False)

    run_powershell_request = libs_pb2.RunPowerShellRequest()
    run_powershell_request.remote_connection.CopyFrom(remote_connection.to_proto())
    run_powershell_request.command = command
    for variable, value in variables.items():
        run_powershell_request.variables[variable] = value
    run_powershell_response = internal_libs.run_powershell(
        run_powershell_request)
    response_to_str(run_powershell_response)
    _check_exit_code(run_powershell_response, check)
    return _handle_response(run_powershell_response)


def run_expect(remote_connection, command, variables=None, check=False):
    """run_expect operation wrapper.

    The run_expect function executes a tcl command or script on a remote Unix
    environment . The specified environment user executes this logic from their
    home directory. The Delphix Engine captures and logs all output to stdout
    and stderr from this command. If the function fails, the output is
    displayed in the Delphix Management application and CLI to aid in
    debugging.

    If successful, the executed logic must exit with an exit code of 0. All
    other exit codes are treated as a function failure.

    Args:
        remote_connection (RemoteConnection): Connection to a remote
        environment.
        command (str): Expect(TCL) command to run.
        variables (dict): Environment variables to set before running the
        command.
    """
    #
    # Since this import only resolves at runtime, we keep it in the function
    # scope to allow unit testing of this module.
    #
    from dlpx.virtualization._engine import libs as internal_libs
    if variables is None:
        variables = {}

    command = to_str(command)
    variables = to_str(variables)

    # Validate all the arguments passed in are the right types based on docs.
    if not isinstance(remote_connection, RemoteConnection):
        raise IncorrectArgumentTypeError(
            'remote_connection',
            type(remote_connection),
            RemoteConnection)
    if not isinstance(command, six.string_types):
        raise IncorrectArgumentTypeError('command', type(command), six.string_types[0])
    if variables and not isinstance(variables, dict):
        raise IncorrectArgumentTypeError(
            'variables',
            type(variables),
            {six.string_types[0]: six.string_types[0]},
            False)
    if (variables and (not all(isinstance(variable, six.string_types)
                               for variable in variables.keys()) or
                       not all(isinstance(value, six.string_types)
                               for value in variables.values()))):
        raise IncorrectArgumentTypeError(
            'variables',
            {(type(variable), type(value))
             for variable, value in variables.items()},
            {six.string_types[0]: six.string_types[0]},
            False)

    run_expect_request = libs_pb2.RunExpectRequest()
    run_expect_request.remote_connection.CopyFrom(remote_connection.to_proto())
    run_expect_request.command = command
    for variable, value in variables.items():
        run_expect_request.variables[variable] = value

    run_expect_response = internal_libs.run_expect(run_expect_request)
    response_to_str(run_expect_response)
    _check_exit_code(run_expect_response, check)
    return _handle_response(run_expect_response)


def _log_request(message, log_level):
    """This is an internal wrapper around the Virtualization library's logging
    API. It maps Python logging level to the library's logging levels:

    logging.DEBUG    -> LogRequest.DEBUG
    logging.INFO     -> LogRequest.INFO
    logging.WARN     -> LogRequest.ERROR
    logging.WARNING  -> LogRequest.ERROR
    logging.ERROR    -> LogRequest.ERROR
    logging.CRITICAL -> LogRequest.ERROR

    Args:
        message (str): The message to be logged by the platform.
        log_level (int): The Python logging level.
    """
    from dlpx.virtualization._engine import libs as internal_libs

    message = to_str(message)
    log_request = libs_pb2.LogRequest()
    log_request.message = message

    #
    # The Virtualization Library API defines only DEBUG, INFO, and ERROR. Map
    # all logging levels into one of those three buckets.
    #
    if log_level <= logging.DEBUG:
        log_request.level = libs_pb2.LogRequest.DEBUG
    elif log_level <= logging.INFO:
        log_request.level = libs_pb2.LogRequest.INFO
    else:
        log_request.level = libs_pb2.LogRequest.ERROR

    response = internal_libs.log(log_request)
    response_to_str(response)
    _handle_response(response)


def retrieve_credentials(credentials_supplier):
    """
    This is an internal wrapper around the Virtualization library's credentials
    retrieval API. Given a supplier provided by Virtualization, retrieves the
    credentials from that supplier.

    Args:
        credentials_supplier (dict): Properties that make up a supplier of credentials.
    Return:
        Subclass of Credentials retrieved from supplier. Either a PasswordCredentials
        or a KeyPairCredentials from dlpx.virtualization.common._common_classes.
    """
    from dlpx.virtualization._engine import libs as internal_libs

    if not isinstance(credentials_supplier, dict):
        raise IncorrectArgumentTypeError(
            'credentials_supplier', type(credentials_supplier), dict)

    credentials_request = libs_pb2.CredentialsRequest()
    credentials_struct = Struct()
    credentials_struct.update(credentials_supplier)
    credentials_request.credentials_supplier.CopyFrom(credentials_struct)

    response = internal_libs.retrieve_credentials(credentials_request)
    response_to_str(response)
    credentials_result = _handle_response(response)
    #
    # As protobuf definition of credentials_result object has all the
    # attributes private_key, public_key and password irrespective of
    # whether it is a keypair or a password credential type, we consider the
    # object to be password credential type if private_key and public_key is
    # not set.
    #
    if (
        not credentials_result.key_pair.private_key and
        not credentials_result.key_pair.public_key
    ):
        return PasswordCredentials(
            credentials_result.username, credentials_result.password)
    return KeyPairCredentials(
        credentials_result.username,
        credentials_result.key_pair.private_key,
        credentials_result.key_pair.public_key)


def upgrade_password(password, username=None):
    """
    This is an internal wrapper around Virtualization's credentials-supplier conversion
    API. It is intended for use during plugin upgrade when a plugin needs to transform
    a password value into a more generic credentials supplier object.

    Args:
        password (str): Plain password string.
        username (str, defaults to None): User name contained in the password
            credential supplier to return.
    Return:
        Credentials supplier (dict) that supplies the given password and username.
    """
    from dlpx.virtualization._engine import libs as internal_libs

    if not isinstance(password, six.string_types):
        raise IncorrectArgumentTypeError(
            'password', type(password), six.string_types[0])
    if username and not isinstance(username, six.string_types):
        raise IncorrectArgumentTypeError(
            'username', type(username), six.string_types[0], required=False)

    upgrade_password_request = libs_pb2.UpgradePasswordRequest()
    upgrade_password_request.password = password
    if username:
        upgrade_password_request.username = username

    response = internal_libs.upgrade_password(upgrade_password_request)
    response_to_str(response)
    upgrade_password_result = _handle_response(response)
    return json_format.MessageToDict(upgrade_password_result.credentials_supplier)
