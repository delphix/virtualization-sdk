#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import functools
import logging
import os
import re

from dlpx.virtualization import _internal as virtualization_internal
from dlpx.virtualization.platform import util
from six.moves import configparser

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
    of dlpx.virtualization._internal.
    """
    parser = configparser.SafeConfigParser()
    parser.read(os.path.join(get_internal_package_root(), SETTINGS_FILE_NAME))
    return parser


@_run_once
def get_version():
    """Returns the version of the dlpx.virtualization._internal package."""
    with open(os.path.join(get_internal_package_root(),
                           'VERSION')) as version_file:
        version = version_file.read().strip()
    return version


def get_external_version_string(version_string):
    """Returns the external version string given an external or internal
    (development) version. An external version string contains only digits and
    dots, and follows the following format: "1.1.0". The internal version
    string might include the development build suffix of the following format:
     "1.0.0-internal-001".

    :param version_string: version string in either internal or external format
    :return: version string in external format
    """
    return re.search(r'([0-9]\.[0-9]\.[0-9])', version_string).group(0)


@_run_once
def get_virtualization_api_version():
    return get_external_version_string(util.get_virtualization_api_version())


def get_build_api_version():
    """Returns the sdk build version in the format build command expects"""
    major, minor, micro =\
        (int(n) for n in get_virtualization_api_version().split('.'))
    build_api_version = {
        'type': 'APIVersion',
        'major': major,
        'minor': minor,
        'micro': micro
    }
    return build_api_version


@_run_once
def get_engine_api_version_from_settings():
    """
    Returns the engine api version from dlpx.virtualization._internal package.
    """
    return _get_settings().get('General', 'engine_api_version')


def get_engine_api_version():
    """Returns the engine api version in JSON format."""
    major, minor, micro = (
        int(n) for n in get_engine_api_version_from_settings().split('.'))
    engine_api_version = {
        'type': 'APIVersion',
        'major': major,
        'minor': minor,
        'micro': micro
    }
    return engine_api_version


@_run_once
def get_internal_package_root():
    """
    Returns the root directory of the dlpx.virtualization._internal package.
    """
    for path in virtualization_internal.__path__:
        settings_path = os.path.join(path, SETTINGS_FILE_NAME)
        if os.path.isfile(settings_path):
            return path
    else:
        raise RuntimeError('Could not find settings file')
