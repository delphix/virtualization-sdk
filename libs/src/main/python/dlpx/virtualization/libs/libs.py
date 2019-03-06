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
virtulization libs interface (a client stub) injected into the namespace such
that one can invoke libs.run_bash(run_bash_request). In Jython, that
object will in fact be a Java object that will delegate to a Java implementation
of a lib operation.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
from dlpx.virtualization import libs_pb2
from dlpx.virtualization.internal import libs as internal_libs

__all__ = [
    "run_bash",
    "run_sync",
    "run_powershell",
    "run_expect"]

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

  run_sync_request = libs_pb2.RunSyncRequest()
  run_sync_request.remote_connection.CopyFrom(remote_connection)
  run_sync_request.source_directory = source_directory
  if rsync_user is not None:
    run_sync_request.rsync_user = rsync_user
  if exclude_paths is not None:
    run_sync_request.exclude_paths.extend(exclude_paths)
  if sym_links_to_follow is not None:
    run_sync_request.sym_links_to_follow.extend(sym_links_to_follow)

  internal_libs.run_sync(run_sync_request)


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
  if variables is None:
    variables = {}
  run_expect_request = libs_pb2.RunExpectRequest()
  run_expect_request.remote_connection.CopyFrom(remote_connection)
  run_expect_request.command = command
  for variable, value in variables.items():
    run_expect_request.variables[variable] = value

  internal_libs.run_expect(run_expect_request)