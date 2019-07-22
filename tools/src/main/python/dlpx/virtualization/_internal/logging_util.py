#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import logging.config
import os
import sys
import time

LOGGING_DIRECTORY = os.path.expanduser(os.path.join('~', '.dvp', 'logs'))
DEBUG_FILE_NAME = 'debug.log'


def add_console_handler(console_logging_level):
    """
    Adds a console handler to logging.getLogger(__package__) with the given
    logging level.

    This handler will always print to stdout.
    """
    formatter = logging.Formatter('%(message)s')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(console_logging_level)

    logger = logging.getLogger(__package__)
    logger.addHandler(console_handler)
    logger.debug('Console logging configured with logging level %d',
                 console_logging_level)


def setup_logger():
    """
    Sets up virtualization._internal's logger with a single file handler at
    the DEBUG level. If the logging directory does not exist, it will be
    created.

    Logging for this module will not work as expected until this function has
    been called so this should be called immediately.
    """
    log_directory_exists = os.path.exists(LOGGING_DIRECTORY)

    if not log_directory_exists:
        os.makedirs(LOGGING_DIRECTORY)

    _configure_logger(LOGGING_DIRECTORY)

    #
    # We need to setup the logger before we can log anything. Once it's been
    # setup, retroactively log whether we had to create the directory.
    #
    logger = logging.getLogger(__name__)
    if not log_directory_exists:
        logger.debug(
            "Creating and using log directory '%s' as it does not exist.",
            LOGGING_DIRECTORY)
    else:
        logger.debug("Log directory '%s' exists and will be used.",
                     LOGGING_DIRECTORY)


def _configure_logger(log_directory):
    """
    Configures the formatter and handler for file logging and sets up this
    packages logger.

    The configuration of the file handler and logger is contained to this
    function.
    """

    # Use UTC in logging statements for consistency
    class UTCFormatter(logging.Formatter):
        converter = time.gmtime

    debug_log = os.path.join(log_directory, DEBUG_FILE_NAME)

    logging_config = {
        'version': 1,
        #
        # Module level loggers in modules that have been imported prior to
        # setting up this logger should not be disabled when we add the
        # configuration.
        #
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                '()':
                UTCFormatter,
                # Example: 2019-01-08 20:38:14,736 DEBUG    [cli.py:64] debug
                'format': ('%(asctime)s,%(msecs)d %(levelname)-8s'
                           ' [%(filename)s:%(lineno)d] %(message)s'),
                'datefmt':
                '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            #
            # Use a RotatingFileHandler. Once the debug file reaches maxBytes
            # it will be renamed from debug.log to debug.log.1 and debug.log
            # will then continue to be written to. Once backupCount number of
            # files have been created, when the handler needs to create a new
            # file, the oldest file will be deleted.
            #
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'detailed',
                'level': logging.DEBUG,
                'filename': debug_log,
                'maxBytes': 2**20,  # 2MB in bytes
                'backupCount': 5,
            }
        },
        #
        # Setup the package's logger. The level is logging.NOTSET so handlers
        # are in control of what level is logged where.
        #
        'loggers': {
            __package__: {
                'handlers': ['file'],
                'level': logging.NOTSET
            },
            #
            # The root logger's level should be NOTSET as well or else log
            # messages won't be propogated to the virtualization._internal
            # logger.
            #
            '': {
                'level': logging.NOTSET
            }
        }
    }

    logging.config.dictConfig(logging_config)
