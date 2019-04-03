#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

from logging import Handler

from dlpx.virtualization.libs import libs

__all__ = [
    "PlatformHandler"
]


class PlatformHandler(Handler):
    """
    A logging handler that calls into the Virtualization Library.
    """
    def emit(self, record):
        msg = self.format(record)
        libs._log_request(msg, record.levelno)
