#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

#
# This file is ran both when creating the distribution and when the user
# installs the distribution. This file is ran before anything else when the
# user installs the distribution. This means we cannot assume any dependencies
# exist in their environment. These imports should be limited to builtin
# modules.
#
# If this burden becomes too much, there may be a way to specify requirements
# for setup.py that we can look into. Even then we need to use extra caution
# not to pollute a user's Python installation with packages only needed for
# installation.
#
from setuptools import find_packages, setup

#
# ConfigParser changed names between Python 2 and Python 3. To maintain
# compatibility, try the Python 3 name and fall back to Python 2.
#
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

_SETUP_SETTINGS_PARSER = None


def get_settings_parser():
    global _SETUP_SETTINGS_PARSER
    if _SETUP_SETTINGS_PARSER is None:
        _SETUP_SETTINGS_PARSER = configparser.SafeConfigParser()
        _SETUP_SETTINGS_PARSER.read('src/virtualization/_internal/settings.cfg')
    return _SETUP_SETTINGS_PARSER


def get_version():
    """Reads the version string for this package."""
    return get_settings_parser().get('General', 'package_version')


def get_package_name():
    """
    Returns the name of the distribution. Note that is different from the
    pacakge name.
    """
    return get_settings_parser().get('General', 'distribution_name')


def get_author():
    return get_settings_parser().get('General', 'package_author')


def get_namespace_package():
    return get_settings_parser().get('General', 'namespace_package')


#
# Production requirements should be added here. These requirements will be
# installed (if they do not exist already) on plugin developers' local
# environments.
#
# These should be kept minimal and SHOULD NOT specify a version in case a
# user already have a version of a requirement (or a requirement of a
# requirement) installed in their environment.
#
PROD_REQUIREMENTS = [
    'click >= 7',
    'six'
]


setup(
    name=get_package_name(),
    version=get_version(),
    author=get_author(),
    entry_points={
        'console_scripts': [
            'delphix=virtualization._internal.cli:delphix_sdk']
    },
    package_dir={'': 'src'},  # Our package's root is in the src directory
    package_data={'': ['settings.cfg']},
    namespace_packages=[get_namespace_package()],
    packages=find_packages('src'),
    install_requires=PROD_REQUIREMENTS
)
