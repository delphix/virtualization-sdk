#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
# flake8: noqa
from dlpx.virtualization.platform import Plugin

plugin = Plugin()


class ArbitraryError(Exception):
    @property
    def message(self):
        return self.args[0]

    def __init__(self, message):
        super(ArbitraryError, self).__init__(message)


raise ArbitraryError('Got an arbitrary non-platforms error for testing.')
