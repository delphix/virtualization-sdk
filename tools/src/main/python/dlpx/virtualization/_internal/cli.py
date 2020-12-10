#
# Copyright (c) 2019, 2020 by Delphix. All rights reserved.
#

import logging
import os
import sys
import traceback
from contextlib import contextmanager

import click
from dlpx.virtualization._internal import (click_util, const, exceptions,
                                           logging_util, package_util)
from dlpx.virtualization._internal.commands import build as build_internal
from dlpx.virtualization._internal.commands import \
    download_logs as download_logs_internal
from dlpx.virtualization._internal.commands import initialize as init_internal
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
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'],
                        obj=click_util.ConfigFileProcessor.read_config())
#
# This setting is added to workaround the bug in click 7.1 on windows
# when case_sensitive=False is used on click.Options. Line 187 of click
# code at https://github.com/pallets/click/blob/7.x/src/click/types.py
# fails when lower() method is called on normed_value as unicode type is
# received on windows instead of string type. Removing case_sensitive=False
# is not a good workaround as the behaviour of command changes.

# This workaround uses token_normalize_func to convert normed_value
# into an ascii string so that when lower() is called on it, it wont fail.
# Also, chose to separate out this into a different settings instead of
# adding it to CONTEXT_SETTINGS to avoid any side-effects on other commands.
#
CONTEXT_SETTINGS_INIT = dict(help_option_names=['-h', '--help'],
                             obj=click_util.ConfigFileProcessor.read_config(),
                             token_normalize_func=lambda x: x.encode("ascii"))

DVP_CONFIG_MAP = CONTEXT_SETTINGS['obj']


@contextmanager
def command_error_handler():
    try:
        yield
    except exceptions.UserError as err:
        logger.error(err.message)
        logger.debug(traceback.format_exc())
        exit(1)
    except Exception as err:
        logger.debug(err)
        logger.error('Internal error, please contact Delphix.')
        exit(2)


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

    if sys.version_info[:2] != (2, 7):
        raise exceptions.UserError(
            'Python version check failed.'
            'Supported version is 2.7.x, found {}'.format(sys.version_info))


@delphix_sdk.command(context_settings=CONTEXT_SETTINGS_INIT)
@click.option('-r',
              '--root-dir',
              'root',
              default=os.getcwd(),
              show_default=True,
              type=click.Path(exists=True,
                              file_okay=False,
                              dir_okay=True,
                              writable=True,
                              resolve_path=True),
              callback=click_util.validate_option_exists,
              help='Set the plugin root directory.')
@click.option('-n',
              '--plugin-name',
              'name',
              help='Set the name of the plugin that will be displayed '
              'to the Delphix user.')
@click.option(
    '-s',
    '--ingestion-strategy',
    default=const.DIRECT_TYPE,
    show_default=True,
    type=click.Choice([const.DIRECT_TYPE, const.STAGED_TYPE],
                      case_sensitive=False),
    help=('Set the ingestion strategy of the plugin. A "direct" plugin '
          'ingests without a staging server while a "staged" plugin '
          'requires a staging server.'))
@click.option('-t',
              '--host-type',
              default=const.UNIX_HOST_TYPE,
              show_default=True,
              type=click.Choice(
                  [const.UNIX_HOST_TYPE, const.WINDOWS_HOST_TYPE]),
              help='Set the host platform supported by the plugin.')
def init(root, ingestion_strategy, name, host_type):
    """
    Create a plugin in the root directory. The plugin will be valid
    but have no functionality.
    """
    with command_error_handler():
        init_internal.init(root, ingestion_strategy, name, host_type)


@delphix_sdk.command()
@click.option(
    '-c',
    '--plugin-config',
    default='plugin_config.yml',
    show_default=True,
    type=click.Path(exists=True,
                    file_okay=True,
                    dir_okay=False,
                    writable=False,
                    resolve_path=True),
    callback=click_util.validate_option_exists,
    help=('Set the path to plugin config file. '
          'This file contains the configuration required to build the plugin.')
)
@click.option(
    '-a',
    '--upload-artifact',
    cls=click_util.MutuallyExclusiveOption,
    default='artifact.json',
    show_default=True,
    type=click.Path(file_okay=True,
                    dir_okay=False,
                    writable=True,
                    resolve_path=True),
    callback=click_util.validate_option_exists,
    mutually_exclusive=['generate_only'],
    help=(
        'Set the upload artifact. '
        'The upload artifact file generated by build process will be written '
        'to this file and later used by upload command.'))
@click.option(
    '-g',
    '--generate-only',
    cls=click_util.MutuallyExclusiveOption,
    is_flag=True,
    default=False,
    show_default=True,
    mutually_exclusive=['upload_artifact'],
    help=('Only generate the Python classes from the schema definitions. '
          'Do not do a full build or create an upload artifact.'))
@click.option('--dev',
              is_flag=True,
              hidden=True,
              help=('An internal flag that installs dev builds of the '
                    'wrappers. This should only be used by SDK developers.'))
def build(plugin_config, upload_artifact, generate_only, dev):
    """
    Build the plugin code and generate upload artifact file using the
    configuration provided in the plugin config file.
    """
    # Set upload artifact to None if -g is true.
    if generate_only:
        upload_artifact = None

    local_vsdk_root = None

    with command_error_handler():
        if dev:
            if not DVP_CONFIG_MAP.get('dev') or not DVP_CONFIG_MAP.get(
                    'dev').get('vsdk_root'):
                raise RuntimeError("The dev flag was specified but there is "
                                   "not a vsdk_root entry in the dvp config "
                                   "file. Please look in the SDK's README for "
                                   "details on configuring the vsdk_root "
                                   "property.")

            local_vsdk_root = DVP_CONFIG_MAP.get('dev').get('vsdk_root')

        build_internal.build(plugin_config,
                             upload_artifact,
                             generate_only,
                             local_vsdk_root=local_vsdk_root)


@delphix_sdk.command()
@click.option('-e',
              '--engine',
              default=DVP_CONFIG_MAP.get('engine'),
              show_default=True,
              callback=click_util.validate_option_exists,
              help='Upload plugin to the provided Delphix engine.'
              ' This should be either the hostname or IP address.')
@click.option('-u',
              '--user',
              default=DVP_CONFIG_MAP.get('user'),
              show_default=True,
              callback=click_util.validate_option_exists,
              help='Authenticate to the Delphix Engine with the provided user.'
              )
@click.option(
    '-a',
    '--upload-artifact',
    default='artifact.json',
    show_default=True,
    type=click.Path(exists=True,
                    file_okay=True,
                    dir_okay=False,
                    readable=True,
                    resolve_path=True),
    callback=click_util.validate_option_exists,
    help='Path to the upload artifact that was generated through build.')
@click.option('--wait',
              is_flag=True,
              help='Wait for the upload job to complete before returning.')
@click.password_option(cls=click_util.PasswordPromptIf,
                       default=DVP_CONFIG_MAP.get('password'),
                       confirmation_prompt=False,
                       help='Authenticate using the provided password.')
def upload(engine, user, upload_artifact, password, wait):
    """
    Upload the generated upload artifact (the plugin JSON file) that was built
    to a target Delphix Engine.
    Note that the upload artifact should be the file created after running
    the build command and will fail if it's not readable or valid.
    """
    with command_error_handler():
        upload_internal.upload(engine, user, upload_artifact, password, wait)


@delphix_sdk.command()
@click.option('-e',
              '--engine',
              default=DVP_CONFIG_MAP.get('engine'),
              show_default=True,
              callback=click_util.validate_option_exists,
              help='Download plugin logs from the provided Delphix engine.'
              ' This should be either the hostname or IP address.')
@click.option('-c',
              '--plugin-config',
              default='plugin_config.yml',
              show_default=True,
              type=click.Path(exists=True,
                              file_okay=True,
                              dir_okay=False,
                              resolve_path=True),
              callback=click_util.validate_option_exists,
              help='Set the path to plugin config file. '
              'This file contains the plugin name to download logs for.')
@click.option('-u',
              '--user',
              default=DVP_CONFIG_MAP.get('user'),
              show_default=True,
              callback=click_util.validate_option_exists,
              help='Authenticate to the Delphix Engine with the provided user.'
              )
@click.option(
    '-d',
    '--directory',
    default=os.getcwd(),
    show_default=True,
    type=click.Path(exists=True,
                    file_okay=False,
                    dir_okay=True,
                    writable=True,
                    resolve_path=True),
    callback=click_util.validate_option_exists,
    help='Specify the directory of where to download the plugin logs.')
@click.password_option(cls=click_util.PasswordPromptIf,
                       default=DVP_CONFIG_MAP.get('password'),
                       confirmation_prompt=False,
                       help='Authenticate using the provided password.')
def download_logs(engine, plugin_config, user, password, directory):
    """
    Download plugin logs from a target Delphix Engine to a local directory.
    """
    with command_error_handler():
        download_logs_internal.download_logs(engine, plugin_config, user,
                                             password, directory)


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
