#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import os

import click

from virtualization._internal import click_util, logging_util, package_util
from virtualization._internal.commands import initialize
from virtualization._internal.commands import upload as upload_internal

#
# Setup the logger and file handler. This needs to be done immediately as
# logging will not work as expected until this has been done. Other classes
# have module level loggers that are initialized on the import, not when a
# function is called.
#
logging_util.setup_logger()

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
    help='Upload plugin to the provided engine.')
@click.option(
    '-u',
    '--user',
    envvar='DELPHIX_ADMIN_USER',
    callback=click_util.validate_option_exists,
    help='Authenticate to the Delphix Engine with the provided user.')
@click.option(
    '-p',
    '--plugin',
    cls=click_util.MutuallyExclusiveOption,
    type=click.Path(dir_okay=False),
    callback=click_util.validate_option_exists,
    mutually_exclusive=['build'])
@click.option(
    '-b',
    '--build',
    cls=click_util.MutuallyExclusiveOption,
    is_flag=True,
    mutually_exclusive=['plugin'],
    help='Build the plugin prior to uploading.')
@click.password_option(
    confirmation_prompt=False,
    envvar='DELPHIX_ADMIN_PASSWORD',
    help='Authenticate using the provided password.')
def upload(engine, user, password, plugin, build):
    """Upload a plugin to a Delphix Engine."""
    upload_internal.upload(engine, user, plugin, build, password)


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
