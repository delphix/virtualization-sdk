#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

# -*- coding: utf-8 -*-
"""Virtualization Platform API wrappers.

This module contains all Virtualization Platform API wrappers (for details on
the API definition, see platform/src/proto/delphix-platform.proto).

The wrappers are the implementation of the Virtualization Platform API. They
take <OperationName>Request protobuf message as input and return
<OperationName>Response, e.g. ConfigureRequest and ConfigureResponse. The
wrappers are called by the Delphix Engine and their role is to unpack input
*Request protobuf message, delegate to the user defined method that has logic
for the virtualization operation itself (such as configure), and craft a
response object. The wrappers assume that the Python runtime will have
virtulization operation method definitions imported prior, i.e. user defined
configure() method is defined in the runtime and hence we can just
call configure().

Todo:
    * Write wrappers for all remaining virtualization operations.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
from dlpx.virtualization import platform_pb2


def configure_wrapper(configure_request):
    """Configure operation wrapper.

  Executed just after cloning the captured data and mounting it to a target
  environment. Specifically, this hook is run during provision and refresh,
  prior to taking the initial snapshot of the clone. This toolkit hook is run
  before the user-customizable Configure Clone and Before Refresh hooks are
  run. It must return a sourceConfig object that represents the new dataset.

  Configure the data to be usable on the target environment. For database data
  files, this may mean recovering from a crash consistent format or backup.
  For application files, this may mean reconfiguring XML files or rewriting
  hostnames and symlinks.

  Args:
      configure_request (ConfigureRequest): Configure operation arguments.

  Returns:
      ConfigureResponse: A response contiaining the return value of the
      configure operation, as a ConfigureResult.
  """
    config = configure(
        source=configure_request.source,
        repository=configure_request.repository,
        snapshot=configure_request.snapshot)
    configure_response = platform_pb2.ConfigureResponse()
    configure_response.return_value.source_config.json = config.to_json()
    return configure_response
