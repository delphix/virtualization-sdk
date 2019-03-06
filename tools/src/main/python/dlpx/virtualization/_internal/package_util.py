#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import functools
import logging
import os

from six.moves import configparser

from dlpx.virtualization import _internal as virtualization_internal

logger = logging.getLogger(__name__)

SETTINGS_FILE_NAME = 'settings.cfg'


def _run_once(fn):
    value = [_run_once]

    @functools.wraps(fn)
    def run_once_wrapper():
        result = value[0]
        if result is _run_once:
            result = fn()
            value[0] = result
        return result

    return run_once_wrapper


@_run_once
def _get_settings():
    """
    Reads the settings file and constructs a Python object from it.

    This assumes that the settings file is in the root
    of virtualization._internal.
    """
    parser = configparser.SafeConfigParser()
    parser.read(os.path.join(get_internal_package_root(), SETTINGS_FILE_NAME))
    return parser


@_run_once
def get_version():
    """Returns the version of the virtualization._internal package."""
    return _get_settings().get('General', 'package_version')


def get_build_api_version():
    """Returns the sdk build version in the format build command expects"""
    major, minor, micro = (int(n) for n in get_version().split('.'))
    build_api_version = {
        'type': 'APIVersion',
        'major': major,
        'minor': minor,
        'micro': micro
    }
    return build_api_version


@_run_once
def get_internal_package_root():
    """Returns the root directory of the virtualization._internal package."""
    for path in virtualization_internal.__path__:
        settings_path = os.path.join(path, SETTINGS_FILE_NAME)
        if os.path.isfile(settings_path):
            return path
    else:
        raise RuntimeError('Could not find settings file')
