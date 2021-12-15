#
# Copyright (c) 2019, 2021 by Delphix. All rights reserved.
#

from logging import Handler

from dlpx.virtualization.libs import libs
from dlpx.virtualization.common.util import to_str

__all__ = [
    "PlatformHandler"
]


class PlatformHandler(Handler):
    """
    A logging handler that calls into the Virtualization Library.
    """
    def emit(self, record):
        msg = self.format(record)
        msg = to_str(msg)
        libs._log_request(msg, record.levelno)
