# Copyright (c) 2019 by Delphix. All rights reserved.
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
from dlpx.virtualization import libs_pb2
from dlpx.virtualization.libs.exceptions import LibraryError

import logging


__all__ = [
    "run_bash",
    "run_sync",
    "run_powershell",
    "run_expect"
]

def run_bash(remote_connection, command, variables=None, use_login_shell=False):
  """run_bash operation wrapper.

  The run_bash function executes a shell command or script on a remote Unix
  environment using the shell binary shipped in the Delphix Engine on the
  environment. The specified environment user executes this logic from their
  home directory. The Delphix Engine captures and logs all output to stdout and
  stderr from this command. If the function fails, the output is displayed in
  the Delphix Management application and CLI to aid in debugging.

  If successful, the executed logic must exit with an exit code of 0. All other
  exit codes are treated as a function failure.

  Args:
    remote_connection (RemoteConnection): Connection to a remote environment.
    command (str): Bash command to run.
    variables (dict): Environment variables to set before running the command.
    use_login_shell (bool): Whether to use login shell.

  Returns:
    RunBashResponse: The return value of run_bash operation.
  """

  # Since this import only resolves at runtime, we keep it in the function scope to allow unit testing of this module.
  from dlpx.virtualization._engine import libs as internal_libs

  if variables is None:
    variables = {}
  run_bash_request = libs_pb2.RunBashRequest()
  run_bash_request.remote_connection.CopyFrom(remote_connection)
  run_bash_request.command = command
  run_bash_request.use_login_shell = use_login_shell
  for variable, value in variables.items():
    run_bash_request.variables[variable] = value
  run_bash_response = internal_libs.run_bash(run_bash_request)

  return run_bash_response


def _handle_response(response):
  """
   This function handles callback responses. It proceeds differently based on what the response reported...
   All of our callback response types have one of these three setups:
    - If there was a successful callback, this method returns the return value ("result") of the callback
    - If there was an actionable error, this method will throw a LibraryError, which the plugin may choose to catch
    - If there was a non-actionable error, this method calls exit()
  """
  if response.HasField("error"):
    if response.error.HasField("actionable_error"):
      actionable = response.error.actionable_error
      # Give the plugin a chance to catch/handle this problem
      raise LibraryError(actionable.id, actionable.message)

    # Nothing the plugin can do, so quit ASAP
    exit()

  # Unpack the return value from the response
  return response.return_value


def run_sync(remote_connection, source_directory, rsync_user=None,
             exclude_paths=None, sym_links_to_follow=None):
  """run_sync operation wrapper.

     The run_sync function copies files from the remote source host directly into the dSource,
     without involving a staging host.

  Args:
    remote_connection (RemoteConnection): Connection to a remote environment.
    source_directory (str): Directory of files to be synced.
    rsync_user (str): User who has access to the directory to be synced.
    exclude_paths (list of str): Paths to be excluded.
    sym_links_to_follow (list of str): Sym links to follow if any.
  """

  # Since this import only resolves at runtime, we keep it in the function scope to allow unit testing of this module.
  from dlpx.virtualization._engine import libs as internal_libs

  run_sync_request = libs_pb2.RunSyncRequest()
  run_sync_request.remote_connection.CopyFrom(remote_connection)
  run_sync_request.source_directory = source_directory
  if rsync_user is not None:
    run_sync_request.rsync_user = rsync_user
  if exclude_paths is not None:
    run_sync_request.exclude_paths.extend(exclude_paths)
  if sym_links_to_follow is not None:
    run_sync_request.sym_links_to_follow.extend(sym_links_to_follow)

  response = internal_libs.run_sync(run_sync_request)
  _handle_response(response)


def run_powershell(remote_connection, command, variables=None):
  """run_powershell operation wrapper.

  The run_powershell function executes a powershell command or script on a remote windows
  environment using the binary in the environment. The specified environment user executes this logic from their
  home directory. The Delphix Engine captures and logs all output to stdout and
  stderr from this command. If the function fails, the output is displayed in
  the Delphix Management application and CLI to aid in debugging.

  If successful, the executed logic must exit with an exit code of 0. All other
  exit codes are treated as a function failure.

  Args:
    remote_connection (RemoteConnection): Connection to a remote environment.
    script (str): powershell script to run.
    variables (dict): Environment variables to set before running the command.

  Returns:
    RunPowerShellResponse: The return value of run_powershell operation.
  """

  # Since this import only resolves at runtime, we keep it in the function scope to allow unit testing of this module.
  from dlpx.virtualization._engine import libs as internal_libs

  if variables is None:
    variables = {}
  run_powershell_request = libs_pb2.RunPowerShellRequest()
  run_powershell_request.remote_connection.CopyFrom(remote_connection)
  run_powershell_request.command = command
  for variable, value in variables.items():
    run_powershell_request.variables[variable] = value
  run_powershell_response = internal_libs.run_powershell(run_powershell_request)

  return run_powershell_response


def run_expect(remote_connection, command, variables=None):
  """run_expect operation wrapper.

  The run_expect function executes a tcl command or script on a remote Unix
  environment . The specified environment user executes this logic from their
  home directory. The Delphix Engine captures and logs all output to stdout and
  stderr from this command. If the function fails, the output is displayed in
  the Delphix Management application and CLI to aid in debugging.

  If successful, the executed logic must exit with an exit code of 0. All other
  exit codes are treated as a function failure.

  Args:
    remote_connection (RemoteConnection): Connection to a remote environment.
    command (str): Expect(TCL) command to run.
    variables (dict): Environment variables to set before running the command.
  """

  # Since this import only resolves at runtime, we keep it in the function scope to allow unit testing of this module.
  from dlpx.virtualization._engine import libs as internal_libs

  if variables is None:
    variables = {}
  run_expect_request = libs_pb2.RunExpectRequest()
  run_expect_request.remote_connection.CopyFrom(remote_connection)
  run_expect_request.command = command
  for variable, value in variables.items():
    run_expect_request.variables[variable] = value

  internal_libs.run_expect(run_expect_request)


def _log_request(message, log_level):
  """
  This is an internal wrapper around the Virtualization library's logging
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

  internal_libs.log(log_request)
