#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
import inspect

from dlpx.virtualization.platform.exceptions import DecoratorNotFunctionError


def check_function(impl, operation):
    if not inspect.isfunction(impl) and not inspect.ismethod(impl):
        raise DecoratorNotFunctionError(impl.__name__, operation.value)
    return impl
