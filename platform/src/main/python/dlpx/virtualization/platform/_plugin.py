#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

# -*- coding: utf-8 -*-
"""Plugin for the Virtualization Platform

This module contains a skeleton of a plugin that allows users to extend the
Delphix Dynamic Data Platform's support for external data sources. A plugin is
composed of three different parts that determine how each stage of a data
source's virtualization should be performed: DiscoveryOperations,
LinkedOperations and VirtualOperations. These three classes contain all the
methods available during the process of discovery, direct or staged linking,
and provisioning virtual datasets. Let's see an example of how we can start
writing a plugin that provides an implementation for the "virtual.configure"
plugin operation, which is executed during provisioning a virtual dataset.

Before we start looking at implementations of plugin operations, we have to
initialize the plugin object. Let's say we're writing a plugin for a database
called "my_db". We can initialize the plugin object as such:

  from dlpx.virtualization.platform import Plugin

  my_db_plugin = Plugin()

Now, a plugin writer should write an implementation of their
"virtual.configure" operation and decorate the implementation method with a
corresponding decorator. The decorator's name must start with the name of the
plugin object as assigned in the statement above:

  @my_db_plugin.virtual.configure()
  def my_configure_implementation(source, repository, snapshot):
    do_something()
    ...
    ## The rest of the implementation.
    return

Let's walk through what happens when invoke
"@my_db_plugin.virtual.configure()":

1. my_db_plugin.virtual.configure() function is called. This function allows to
    pass arguments to a decorator. The "self" argument is automatically
    provided on an object method, hence we don't have to pass any arguments.
2. configure_decorator function takes my_configure_implementation function as
    an input and it saves a handle to the implementation on the
    VirtualOperations object under configure_impl property. Then,
    configure_decorator returns my_configure_implementation to make sure that
    we preserve the signature and metadata of the original implementation
    function.
3. configure_wrapper(configure_request) is a function that corresponds to the
    Virtualization Platform API  (see platform.proto) and it accepts a protobuf
    message as input argument, and it returns another protobuf message. This
    function is invoked by the Dynamic Data Platform runtime. For the details
    on the semantics of those protobuf message, see the section below entitled
    "Virtualization Platform API wrappers".
4. configure_wrapper unpacks the received configure_request protobuf message to
    provide input arguments to self.configure_impl method (which points to
    my_configure_implementation). Then, self.configure_impl is invoked with
    the input arguments.
5. self.configure_impl returns a config object that we pack into a protobuf
    message response and return it. The response will be sent back to the
    Dynamic Data Platform runtime.

Virtualization Platform API wrappers

The wrappers are the implementation of the Virtualization Platform API. They
take <OperationName>Request protobuf message as input and return
<OperationName>Response, e.g. ConfigureRequest and ConfigureResponse. The
wrappers are called by the Dynamic Data Platform runtime and input *Request
protobuf message, delegate to the user defined method that has logic for the
virtualization operation itself (such as configure), and craft a response
object.


Note on method level imports: In method imports are needed for plugin defined
modules (from generated.definitions). These imports will fail on a developer's
environment if they haven't generated them yet. If these were module level
imports, the import for dlpx.virtualization.platform.Plugin will more likely
fail. The internal methods should only be called by the platform so it's safe
to have the import in the methods as the objects will exist at runtime.
"""
from dlpx.virtualization.platform import (DiscoveryOperations,
                                          LinkedOperations, UpgradeOperations,
                                          VirtualOperations)

__all__ = ['Plugin']


class Plugin(object):
    def __init__(self):
        self.__discovery = DiscoveryOperations()
        self.__linked = LinkedOperations()
        self.__virtual = VirtualOperations()
        self.__upgrade = UpgradeOperations()

    @property
    def discovery(self):
        return self.__discovery

    @property
    def linked(self):
        return self.__linked

    @property
    def virtual(self):
        return self.__virtual

    @property
    def upgrade(self):
        return self.__upgrade
