#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import logging
import os
import traceback
from contextlib import contextmanager

import click

from dlpx.virtualization._internal import (click_util, exceptions,
                                           logging_util, package_util)
from dlpx.virtualization._internal.commands import build as build_internal
from dlpx.virtualization._internal.commands import compile as compile_internal
from dlpx.virtualization._internal.commands import initialize
from dlpx.virtualization._internal.commands import \
    newbuild as newbuild_internal
from dlpx.virtualization._internal.commands import upload as upload_internal

#
# Setup the logger and file handler. This needs to be done immediately as
# logging will not work as expected until this has been done. Other classes
# have module level loggers that are initialized on the import, not when a
# function is called.
#
logging_util.setup_logger()
logger = logging.getLogger(__name__)

__version__ = package_util.get_version()

# This is needed to add -h as an option for the help menu.
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@contextmanager
def command_error_handler():
    try:
        yield
    except exceptions.UserError as err:
        logger.error(err.message)
        logger.debug(traceback.format_exc())
        exit(1)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__)
@click.option(
    '-v',
    '--verbose',
    cls=click_util.MutuallyExclusiveOption,
    mutually_exclusive=['quiet'],
    count=True,
    type=click.IntRange(0, 3),
    help=('Enable verbose mode. '
          'Can be repeated up to three times for increased verbosity.'))
@click.option(
    '-q',
    '--quiet',
    cls=click_util.MutuallyExclusiveOption,
    mutually_exclusive=['verbose'],
    count=True,
    type=click.IntRange(0, 3),
    help=('Enable quiet mode. '
          'Can be repeated up to three times for increased suppression.'))
def delphix_sdk(verbose, quiet):
    """
    The tools of the Delphix Virtualization SDK that help develop, build, and
    upload a plugin.
    """
    console_logging_level = get_console_logging_level(verbose, quiet)
    #
    # Now that we know the desired level, add in the console handler. Nothing
    # will be printed to the console until this is executed.
    #
    logging_util.add_console_handler(console_logging_level)


@delphix_sdk.command()
@click.option(
    '-t',
    '--type',
    default='staged',
    show_default=True,
    type=click.Choice(['direct', 'staged'], case_sensitive=False),
    help='Set the type of plugin.')
@click.option(
    '-r',
    '--root-dir',
    'root',
    default=os.getcwd(),
    show_default=True,
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True),
    help='Set the plugin root directory.')
def init(type, root):
    """Create the skeleton of a Delphix plugin."""
    initialize.init(type, root)


@delphix_sdk.command()
@click.option(
    '-c',
    '--plugin-config',
    'plugin_config',
    default='plugin_config.yml',
    show_default=True,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        resolve_path=True),
    envvar='DX_PLUGIN_CONFIG',
    callback=click_util.validate_option_exists,
    help='Set the path to plugin config file.'
    ' This file contains the configuration required to compile the plugin.')
def compile(plugin_config):
    """
    Compiles the plugin schema and generates the schemas into python objects.

    The plugin_config.yml file should include: \n
    name            the plugin name \n
    prettyName      the plugin's displayed name \n
    version         the plugin version \n
    hostTypes       the list of supported hostTypes (UNIX and/or WINDOWS) \n
    entryPoint      the entry point of the plugin defined by the decorator \n
    srcDir          the directory that the source code is writen in \n
    schemaFile:     the file containing defined schemas in the plugin \n
    manualDiscovery whether or not manual discovery is supported \n
    pluginType      whether the plugin is DIRECT or STAGED \n
    language        language of the source code (ex: PYTHON27 for python2.7) \n
    """

    with command_error_handler():
        compile_internal.compile(plugin_config)


@delphix_sdk.command()
@click.option(
    '-r',
    '--root-dir',
    'root',
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True),
    envvar='PLUGIN_ROOT_DIR',
    callback=click_util.validate_option_exists,
    help='Set the plugin root directory.'
    'This directory contains main.json and all the plugin code to be built.')
@click.option(
    '-o',
    '--outfile',
    type=click.Path(file_okay=True, dir_okay=False, writable=True),
    callback=click_util.validate_option_exists,
    help='Set the output file.'
    'The plugin json file generated by build process will be written'
    'to this file and later used by upload command.')
def build(root, outfile):
    """
    Build the plugin code and generate plugin json file.
    The directory structured required is of the form:

    <root>/ \n
        main.json \n
        resources/ \n
            <resources> \n
        virtual/ \n
            [initialize.py] \n
            [configure.py] \n
            [unconfigure.py] \n
            [reconfigure.py] \n
            [start.py] \n
            [mountSpec.py] \n
            [ownershipSpec.py] \n
            [stop.py] \n
            [preSnapshot.py] \n
            [postSnapshot.py] \n
            [status.py] \n
        staged/ \n
            [resync.py] \n
            [startStaging.py] \n
            [stopStaging.py] \n
            [preSnapshot.py] \n
            [postSnapshot.py] \n
            [status.py] \n
            [worker.py] \n
            [mountSpec.py] \n
            [ownershipSpec.py] \n
        direct/ \n
            [preSnapshot.py] \n
            [postSnapshot.py] \n
        discovery/ \n
            [repositoryDiscovery.py] \n
            [sourceConfigDiscovery.py] \n
        upgrade/ \n
            [fromVersion]/ \n
                [upgradeSnapshot.py] \n
                [upgradeVirtualSource.py] \n
                [upgradeLinkedSource.py] \n
                [upgradeSourceConfig.py] \n

    Notes: \n
        A single plugin cannot be both staged and direct, and so only one of
         the two directories is required (whichever type matches the type
         in the main.json passed in to build the toolkit)
         All other directories and files must exist as expected.

        This script will not check the syntax of your scripts so ensure
         these scripts are functional before building a plugin.

    """

    with command_error_handler():
        build_internal.build(root, outfile)


@delphix_sdk.command()
@click.option(
    '-c',
    '--plugin-config',
    'plugin_config',
    default='plugin_config.yml',
    show_default=True,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        resolve_path=True),
    envvar='DX_PLUGIN_CONFIG',
    callback=click_util.validate_option_exists,
    help='Set the path to plugin config file.'
    'This file contains the configuration required to build the plugin.')
@click.option(
    '-a',
    '--upload-artifact',
    default='artifact.json',
    show_default=True,
    type=click.Path(
        file_okay=True, dir_okay=False, writable=True, resolve_path=True),
    callback=click_util.validate_option_exists,
    help='Set the upload artifact.'
    'The upload artifact file generated by build process will be written'
    'to this file and later used by upload command.')
def newbuild(plugin_config, upload_artifact):
    """
    Build the plugin code and generate upload artifact file using the
    configuration provided in the plugin config file.

    The plugin_config.yml file should include: \n
    name            the plugin name \n
    prettyName      the plugin's displayed name \n
    version         the plugin version \n
    hostTypes       the list of supported hostTypes (UNIX and/or WINDOWS) \n
    entryPoint      the entry point of the plugin defined by the decorator \n
    srcDir          the directory that the source code is writen in \n
    schemaFile:     the file containing defined schemas in the plugin \n
    manualDiscovery whether or not manual discovery is supported \n
    pluginType      whether the plugin is DIRECT or STAGED \n
    language        language of the source code (ex: PYTHON27 for python2.7) \n

    Notes: \n
        This script will not check the syntax of your scripts so ensure
        these scripts are functional before building a plugin.

    """
    with command_error_handler():
        newbuild_internal.build(plugin_config, upload_artifact)


@delphix_sdk.command()
@click.option(
    '-e',
    '--delphix-engine',
    'engine',
    envvar='DELPHIX_ENGINE',
    callback=click_util.validate_option_exists,
    help='Upload plugin to the provided engine.'
    ' This should be either the hostname or IP address.')
@click.option(
    '-u',
    '--user',
    envvar='DELPHIX_ADMIN_USER',
    callback=click_util.validate_option_exists,
    help='Authenticate to the Delphix Engine with the provided user.')
@click.option(
    '-a',
    '--upload-artifact',
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True),
    callback=click_util.validate_option_exists,
    help='Path to the upload artifact that was generated through build.')
@click.password_option(
    confirmation_prompt=False,
    envvar='DELPHIX_ADMIN_PASSWORD',
    help='Authenticate using the provided password.')
def upload(engine, user, upload_artifact, password):
    """
    Upload the generated upload artifact (the plugin JSON file) that was built
    to a target Delphix Engine.
    Note that the upload artifact should be the file created after running
    the build command and will fail if it's not readable or valid.
    """
    with command_error_handler():
        upload_internal.upload(engine, user, upload_artifact, password)


def get_console_logging_level(verbose, quiet):
    """
    Returns the logging level for the console based on the verbose and quiet
    flags.

    Logging levels can be found here:
    https://docs.python.org/2/library/logging.html#logging-levels

    logging.WARNING is 30 and the default console logging level. Each verbose
    flag decreases the logging threshold by one level (a decrement of 10)
    causing more to be printed. Each quiet flag increases the logging
    threshold by one level (an increment of 10) causing less to be printed.


    Three verbose flags will print every message while three quiet flags will
    suppress every message.
    """
    assert verbose == 0 or quiet == 0, (
        'verbose is {} and quiet is {}. Both cannot be non-zero.'.format(
            verbose, quiet))
    return 30 - verbose * 10 + quiet * 10
