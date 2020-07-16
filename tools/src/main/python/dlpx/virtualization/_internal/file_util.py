#
# Copyright (c) 2019, 2020 by Delphix. All rights reserved.
#

import logging
import os
import shutil
import tempfile
import traceback
from contextlib import contextmanager

from dlpx.virtualization._internal import exceptions

logger = logging.getLogger(__name__)


def delete_paths(*args):
    """
    Does best effort cleanup of the given paths. Exceptions are logged
    and not raised.

    Directories are recursively deleted.

    Args:
        args (list of str): A list of paths to attempt to delete.
    """
    for path in args:
        if path and os.path.exists(path):
            try:
                if os.path.isdir(path):
                    logger.debug(
                        'A directory exists at %r. Attempting to delete.',
                        path)
                    shutil.rmtree(path)
                else:
                    logger.debug('A file exists at %r. Attempting to delete.',
                                 path)
                    os.remove(path)
            except Exception as e:
                logger.debug('Failed to delete %r: %s.', path, e.message)
                logger.debug(traceback.format_exc())


def validate_paths_do_not_exist(*args):
    """
    Validates the given file paths do not exist.

    Args:
        args (list of str): A list of paths to validate they do not exist.
    Raises:
        PathExistsError: If any of the provided paths already exist.
    """
    logger.info('Validating files and directories to be written do not exist.')
    for path in args:
        if path and os.path.exists(path):
            raise exceptions.PathExistsError(path)
        logger.debug('SUCCESS: Path %r does not exist.', path)


def standardize_path(path):
    standardized_path = os.path.expanduser(path)
    if standardized_path == '.':
        standardized_path = os.path.realpath(standardized_path)
    else:
        standardized_path = os.path.abspath(standardized_path)
    standardized_path = os.path.abspath(standardized_path)
    return standardized_path


def get_src_dir_path(config_file_path, src_dir):
    """
    Validates 4 requirements of src_dir:
    - src_dir must be a relative path
    - src_dir must exist
    - src_dir must be a directory
    - src_dir must be a subdirectory of the plugin root

    Args:
        config_file_path: A path to the plugin's config file. The plugin's
            root is the directory containing the config file. No pre-processing
            is needed.
        src_dir: The path to the plugin's src directory. This is the path
            to be validated.
    Returns:
        str: A normalized, absolute path to the plugin's source directory.
    """
    # Validate the the src directory is not an absolute path. Paths with
    # ~ in them are not considered absolute by os.path.isabs.
    src_dir = os.path.expanduser(src_dir)
    if os.path.isabs(src_dir):
        raise exceptions.PathIsAbsoluteError(src_dir)

    # The plugin root is the directory containing the plugin config file.
    # This is passed in by the CLI so it needs to be standardized and made
    # absolute for comparison later.
    plugin_root_dir = os.path.dirname(config_file_path)
    plugin_root_dir = standardize_path(plugin_root_dir)

    # The plugin's src directory is relative to the plugin root not to the
    # current working directory. os.path.abspath makes a relative path
    # absolute by appending the current working directory to it. The CLI
    # can be executed anywhere so it's not guaranteed that the cwd is the
    # plugin root.
    src_dir_absolute = standardize_path(os.path.join(plugin_root_dir, src_dir))

    if not os.path.exists(src_dir_absolute):
        raise exceptions.PathDoesNotExistError(src_dir_absolute)
    if not os.path.isdir(src_dir_absolute):
        raise exceptions.PathTypeError(src_dir_absolute, 'directory')

    normcase_src_dir = os.path.normcase(src_dir_absolute)
    normcase_plugin_root = os.path.normcase(plugin_root_dir)

    if (
            not normcase_src_dir.startswith(normcase_plugin_root)
            or normcase_src_dir == normcase_plugin_root
    ):
        raise exceptions.UserError(
            "The src directory {} is not a subdirectory "
            "of the plugin root at {}".format(src_dir_absolute,
                                              plugin_root_dir))
    return src_dir_absolute


def make_dir(path, force_remove):

    #
    # Delete the folder if it is there to clear the location. Ignore errors in
    # case the folder didn't exist. Since we'll be creating another dir at
    # that location, we should handle any errors when creating the dir.
    #
    if force_remove:
        shutil.rmtree(path, ignore_errors=True)
    try:
        os.mkdir(path)
        logger.debug('Successfully created directory \'{}\''.format(path))
    except OSError as err:
        raise exceptions.UserError(
            'Unable to create new directory \'{}\''
            '\nError code: {}. Error message: {}'.format(
                path, err.errno, os.strerror(err.errno)))


def clean_copy(src, tgt):
    """
    Copies src into tgt. Deletes tgt if it exists before copying.

    Args:
         src: The directory to copy.
         tgt: The directory to copy to.
    """
    delete_paths(tgt)
    logger.debug('Copying %s to %s', src, tgt)
    shutil.copytree(src, tgt)


@contextmanager
def tmpdir():
    """
    Creates a temporary directory. When the context is exited, the directory
    is deleted.

    This is only needed for Python 2. tempfile in Python 3 has this
    functionality built in.
    """
    temp = None
    try:
        temp = tempfile.mkdtemp()
        yield temp
    finally:
        delete_paths(temp)
