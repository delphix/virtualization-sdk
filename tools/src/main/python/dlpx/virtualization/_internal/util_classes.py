#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import enum
import os

STAGED_TYPE = 'STAGED'
DIRECT_TYPE = 'DIRECT'

OUTPUT_DIR_NAME = '.dvp-gen-output'
PLUGIN_SCHEMAS_DIR = os.path.join(os.path.dirname(__file__),
                                  'validation_schemas')
PLUGIN_CONFIG_SCHEMA = os.path.join(PLUGIN_SCHEMAS_DIR,
                                    'plugin_config_schema.json')

#
# This is a temporary file. Once blackbox has made the transition to 'id'
# instead of 'name' and uses UUIDs for the id, this, and everything
# associated with it can be removed.
#
PLUGIN_CONFIG_SCHEMA_NO_ID_VALIDATION = os.path.join(
    PLUGIN_SCHEMAS_DIR, 'plugin_config_schema_no_id_validation.json')

PLUGIN_SCHEMA = os.path.join(PLUGIN_SCHEMAS_DIR, 'plugin_schema.json')


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
