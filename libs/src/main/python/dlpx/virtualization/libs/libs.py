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

Todo:
    * Write wrappers for all remaining virtualization libs operations.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
from dlpx.virtualization import libs_pb2
from dlpx.virtualization.internal import libs as internal_libs


def run_bash(remote_connection, command, variables=None, use_login_shell=False):
  """Run_bash operation wrapper.

  The RunBash function executes a shell command or script on a remote Unix
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
