#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import logging
import os
import shutil
import traceback

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
    standardized_path = os.path.normcase(standardized_path)
    return standardized_path


def get_src_dir_path(file_name, src_dir):
    """
    Validates 3 requirements of the src_dir before setting the src_dir path:
    - src_dir cannot be an absolute path
    - src_dir must exist
    - src_dir be a valid directory.
    """
    directory_path = str(src_dir)
    if os.path.isabs(directory_path):
        raise exceptions.PathIsAbsoluteError(directory_path)
    if not os.path.exists(directory_path):
        raise exceptions.PathDoesNotExistError(directory_path)
    if not os.path.isdir(directory_path):
        raise exceptions.PathTypeError(directory_path, 'directory')

    #
    # Standardizes the plugin_root_dir and src_dir formats before
    # checking if src_dir is a subdirectory of the plugin's root.
    #
    plugin_root_dir = os.path.dirname(file_name)
    plugin_root_dir = standardize_path(plugin_root_dir)
    src_dir = standardize_path(src_dir)

    src_dir = os.path.join(plugin_root_dir, src_dir)

    if not os.path.abspath(src_dir).startswith(
            plugin_root_dir) or src_dir == plugin_root_dir:
        file_name_abs_path = os.path.abspath(plugin_root_dir)
        raise exceptions.UserError(
            "The src directory {} is not a subdirectory "
            "of the plugin root at {}".format(src_dir, file_name_abs_path))
    return src_dir


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
