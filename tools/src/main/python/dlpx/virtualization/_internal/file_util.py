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


def get_src_dir_path(file_name, src_dir):
    """Get the absolute path if the srcDir provided is relative path and
    validate that srcDir is a valid directory and that it exists.
    """
    if not os.path.isabs(src_dir):
        src_dir = os.path.join(os.path.dirname(file_name), src_dir)

    if not os.path.exists(src_dir):
        raise exceptions.PathDoesNotExistError(src_dir)
    if not os.path.isdir(src_dir):
        raise exceptions.PathTypeError(src_dir, 'directory')
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
        logger.debug('Successfully created directory {!r}'.format(path))
    except OSError as err:
        raise exceptions.UserError(
            'Unable to create new directory {!r}'
            '\nError code: {}. Error message: {}'.format(
                path, err.errno, os.strerror(err.errno)))
