#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import logging
import os
import traceback

import click

from dlpx.virtualization._internal import (click_util, exceptions,
                                           logging_util, package_util)
from dlpx.virtualization._internal.commands import initialize
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
    try:
        upload_internal.upload(engine, user, upload_artifact, password)
    except exceptions.UserError as err:
        logger.error(err.message)
        logger.debug(traceback.format_exc())
        exit(1)


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
