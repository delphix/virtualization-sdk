#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import enum


class ValidationMode(enum.Enum):
    """
    Defines the validation mode that validator uses.
    INFO - validator will give out info messages if validation fails.
    WARNING - validator will log a warning if validation fails.
    ERROR - validator will raise an exception if validation fails.
    """
    INFO = 1
    WARNING = 2
    ERROR = 3


class MessageUtils:
    """
    Defines helpers methods to format warning and exception messages.
    """

    @staticmethod
    def exception_msg(exceptions):
        exception_msg = '\n'.join(
            MessageUtils.__format_msg('Error', ex)
            for ex in exceptions['exception'])
        return exception_msg

    @staticmethod
    def warning_msg(warnings):
        warning_msg = '\n'.join(
            MessageUtils.__format_msg('Warning', warning)
            for warning in warnings['warning'])
        return warning_msg

    @staticmethod
    def __format_msg(msg_type, msg):
        msg_str = "{}: {}".format(msg_type, msg)
        return msg_str
