#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import logging
import os
import subprocess
import sys

from dlpx.virtualization._internal import file_util, package_util
from dlpx.virtualization._internal.exceptions import SubprocessFailedError

logger = logging.getLogger(__name__)

DVP_DEPENDENCIES = ['dvp-common', 'dvp-libs', 'dvp-platform']


def install_deps(target_dir, local_vsdk_root=None):
    """
    Installs the Python packages needed for the plugin to execute into the
    given target directory.

    Args:
        target_dir: The directory to install the plugin's dependencies into.
        local_vsdk_root: This is an internal field only used for SDK
            developers. It is a path to the root of the SDK repository.
    """

    #
    # If local_vsdk_root is not None, it is assumed this is a development
    # build being done by an SDK developer that is testing wrapper changes.
    # To speed up development, instead of installing the wrappers from a PyPI
    # repository, this will go to local_vsdk_root and for each package will
    # build a distribution locally and install it.
    #
    # This alleviates the need for SDK developers to build and upload dev
    # builds of the wrappers in order to run 'dvp build' and test them.
    #
    if local_vsdk_root:
        package_names = ['common', 'libs', 'platform']

        #
        # Build the wheels for each package in a temporary directory.
        #
        # Pip supports installing directly from a setup.py file but this
        # proved to be incredibly slow due to how it copies source files.
        # If that issue is resolved, it would likely be better to use pip to
        # install directly from the setup.py file instead of needing to build
        # the wheels first. This would remove the need for a temp directory
        # as well.
        #
        with file_util.tmpdir() as wheel_dir:
            for package in package_names:
                _build_wheel(os.path.join(local_vsdk_root, package), wheel_dir)

            packages = {
                os.path.join(wheel_dir, p)
                for p in os.listdir(wheel_dir)
            }

            if len(packages) != len(package_names):
                raise RuntimeError(
                    'An error occurred while attempting to install dev builds '
                    'of the wrappers. Three packages were expected in the '
                    'temporary build directory but instead {} files were '
                    'found:\n\t{}'.format(len(packages),
                                          '\n\t'.join(packages)))

            #
            # Install the packages. this needs to be done inside the tmpdir
            # context, otherwise the distributions will be deleted.
            #
            _pip_install_to_dir(packages, target_dir)

        if os.path.exists(wheel_dir):
            raise RuntimeError('An error occured while attempting to install '
                               'dev builds of the wrappers. {} is a temporary '
                               'directory used to build the wrapper '
                               'distributions. It should have been cleaned up '
                               'but it still exists.'.format(wheel_dir))
    else:
        # This is the production branch that is executed for plugin developers.
        dvp_version = package_util.get_version()
        packages = [
            '{}=={}'.format(pkg, dvp_version) for pkg in DVP_DEPENDENCIES
        ]
        _pip_install_to_dir(packages, target_dir)

    #
    # This is an unfortunate hack. 'protobuf' is installed under the 'google'
    # namespace package. However, there is no __init__.py under 'google'. This
    # is because google assumes it is installed in a site package directory
    # and uses a .pth file to setup the namespace package.
    #
    # The zipimporter used on the Delphix Engine to import the plugin cannot
    # handle .pth files so here an empty __init__.py file is created so
    # 'google' and therefore 'protobuf' can be imported successfully at
    # runtime.
    #
    open(os.path.join(target_dir, 'google', '__init__.py'), 'w').close()


def _execute_pip(pip_args):
    """
    Execute pip with the given args. Raises a SubprocessFailedError if the
    exit code is non-zero.

    Args:
         pip_args: a list of string arguments to pass to pip.
    """
    args = [sys.executable, '-m', 'pip']
    args.extend(pip_args)

    logger.debug('Executing %s', ' '.join(args))
    proc = subprocess.Popen(args,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    all_output, _ = proc.communicate()
    exit_code = proc.wait()

    #
    # If pip failed, raise an error. It's on the caller to log any output. If
    # the command succeeded, log the output to debug so the caller doesn't
    # need to.
    #
    if exit_code != 0:
        raise SubprocessFailedError(' '.join(args), exit_code, all_output)
    else:
        logger.debug(all_output)


def _pip_install_to_dir(dependencies, target_dir):
    """
    Installs dependencies into a target_dir.

    Args:
        dependencies: a set of dependencies to install.
        target_dir: the directory to the install the dependencies into.
    """
    args = ['install', '-t', target_dir]
    args.extend(dependencies)
    _execute_pip(args)


def _build_wheel(package_root, target_dir=None):
    """
    Uses the 'setup.py' file in package_root to build a wheel distribution. If
    target_dir is present, the wheel is built into it. Raises a
    SubprocessFailedError if it fails.

    Args:
        package_root: The path to the root of the package to build. It is
            assumed there is a setup.py file in this directory.
        target_dir: The directory to build the wheel into.
    """
    if not os.path.exists(os.path.join(package_root, 'setup.py')):
        raise RuntimeError(
            'No setup.py file exists in directory {}'.format(package_root))

    args = [sys.executable, 'setup.py', 'bdist_wheel']
    if target_dir:
        args.extend(['-d', target_dir])

    logger.debug('Executing %s', ' '.join(args))
    proc = subprocess.Popen(args,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            cwd=package_root)

    all_output, _ = proc.communicate()
    exit_code = proc.wait()

    if exit_code != 0:
        raise SubprocessFailedError(' '.join(args), exit_code, all_output)
    else:
        logger.debug(all_output)
