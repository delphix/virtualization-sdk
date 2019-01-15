#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import logging
import os

from six.moves import configparser

import virtualization._internal

logger = logging.getLogger(__name__)

SETTINGS_FILE_NAME = 'settings.cfg'
_SETTINGS_PARSER = None


def _get_settings():
    """
    Reads the settings file and constructs a Python object from it.

    This assumes that the settings file is in the root
    of virtualization._internal.
    """
    global _SETTINGS_PARSER
    if _SETTINGS_PARSER is None:
        _SETTINGS_PARSER = configparser.SafeConfigParser()
        _SETTINGS_PARSER.read(
            os.path.join(get_internal_package_root(), SETTINGS_FILE_NAME))
    return _SETTINGS_PARSER


def get_version():
    """Returns the version of the virtualization._internal package."""
    return _get_settings().get('General', 'package_version')


def get_internal_package_root():
    """Returns the root directory of the virtualization._internal package."""
    return os.path.dirname(os.path.abspath(virtualization._internal.__file__))
