#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import os
import subprocess
import sys

import mock
import pytest
from dlpx.virtualization._internal import file_util, package_util
from dlpx.virtualization._internal import plugin_dependency_util as pdu
from dlpx.virtualization._internal.exceptions import SubprocessFailedError


class TestPluginDependencyUtil:
    @staticmethod
    @mock.patch.object(pdu, '_pip_install_to_dir')
    def test_install_plugin_dependencies(mock_install_to_dir, tmp_path):
        google = tmp_path / 'google'
        google.mkdir()

        pdu.install_deps(tmp_path.as_posix())

        expected_dependencies = [
            '{}=={}'.format(p, package_util.get_version())
            for p in ['dvp-common', 'dvp-libs', 'dvp-platform']
        ]
        mock_install_to_dir.assert_called_once_with(expected_dependencies,
                                                    tmp_path.as_posix())

    @staticmethod
    @mock.patch.object(pdu, '_pip_install_to_dir')
    @mock.patch.object(pdu, '_build_wheel')
    @mock.patch.object(file_util, 'tmpdir')
    def test_install_plugin_dependencies_dev(mock_tmpdir, mock_build_wheel,
                                             mock_install_to_dir, tmp_path):
        wheel_dir = tmp_path / 'wheel'
        build_dir = tmp_path / 'build'
        google = build_dir / 'google'
        wheel_dir.mkdir()
        build_dir.mkdir()
        google.mkdir()

        global packages
        packages = []

        def build_wheel(package, dir):
            dist_path = wheel_dir / os.path.basename(package)
            dist_path.touch()

            global packages
            packages.insert(0, dist_path.as_posix())

        def clean_up(a, b, c):
            file_util.delete_paths(wheel_dir.as_posix())

        mock_tmpdir.return_value.__enter__.return_value = wheel_dir.as_posix()
        mock_tmpdir.return_value.__exit__.side_effect = clean_up
        mock_build_wheel.side_effect = build_wheel

        pdu.install_deps(build_dir.as_posix(), local_vsdk_root='vsdk')
        mock_install_to_dir.assert_called_once_with(packages,
                                                    build_dir.as_posix())

    @staticmethod
    @mock.patch.object(subprocess, 'Popen')
    def test_execute_pip(mock_popen):
        mock_popen.return_value.communicate.return_value = ('output', '')
        mock_popen.return_value.wait.return_value = 0

        pdu._execute_pip(['-h'])

        mock_popen.assert_called_once_with([sys.executable, '-m', 'pip', '-h'],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT)

    @staticmethod
    @mock.patch.object(subprocess, 'Popen')
    def test_execute_pip_non_zero_exit(mock_popen):
        mock_popen.return_value.communicate.return_value = ('output', '')
        mock_popen.return_value.wait.return_value = 1

        with pytest.raises(SubprocessFailedError) as excinfo:
            pdu._execute_pip(['-h'])

        expected_args = [sys.executable, '-m', 'pip', '-h']

        mock_popen.assert_called_once_with(expected_args,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT)

        e = excinfo.value
        assert e.command == ' '.join(expected_args)
        assert e.exit_code == 1
        assert e.output == 'output'

    @staticmethod
    @mock.patch.object(subprocess, 'Popen')
    def test_install_to_dir(mock_popen):
        mock_popen.return_value.communicate.return_value = ('output', '')
        mock_popen.return_value.wait.return_value = 0
        dependencies = ['dvp-common==1.0.0', 'six']

        pdu._pip_install_to_dir(dependencies, 'tgt')

        expected_args = [
            sys.executable, '-m', 'pip', 'install', '-t', 'tgt',
            'dvp-common==1.0.0', 'six'
        ]
        mock_popen.assert_called_once_with(expected_args,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT)

    @staticmethod
    @mock.patch.object(subprocess, 'Popen')
    def test_build_wheel(mock_popen, tmp_path):
        setup_file = tmp_path / 'setup.py'
        setup_file.touch()

        mock_popen.return_value.communicate.return_value = ('output', '')
        mock_popen.return_value.wait.return_value = 0

        pdu._build_wheel(tmp_path.as_posix())

        mock_popen.assert_called_once_with(
            [sys.executable, 'setup.py', 'bdist_wheel'],
            cwd=tmp_path.as_posix(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

    @staticmethod
    def test_build_wheel_fails_with_no_setup_file(tmp_path):
        with pytest.raises(RuntimeError) as excinfo:
            pdu._build_wheel(tmp_path.as_posix())

        assert excinfo.value.message == (
            'No setup.py file exists in directory '
            '{}'.format(tmp_path.as_posix()))

    @staticmethod
    @mock.patch.object(subprocess, 'Popen')
    def test_build_wheel_non_zero_exit(mock_popen, tmp_path):
        setup_file = tmp_path / 'setup.py'
        setup_file.touch()

        mock_popen.return_value.communicate.return_value = ('output', '')
        mock_popen.return_value.wait.return_value = 1

        with pytest.raises(SubprocessFailedError) as excinfo:
            pdu._build_wheel(tmp_path.as_posix())

        e = excinfo.value

        expected_args = [sys.executable, 'setup.py', 'bdist_wheel']
        mock_popen.asesrt_called_once_with(expected_args,
                                           cwd=tmp_path.as_posix(),
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT)

        assert e.command == ' '.join(expected_args)
        assert e.exit_code == 1
        assert e.output == 'output'

    @staticmethod
    @mock.patch.object(subprocess, 'Popen')
    def test_build_wheel_target_dir(mock_popen, tmp_path):
        package_dir = tmp_path / 'pkg'
        setup_file = package_dir / 'setup.py'
        target_dir = tmp_path / 'tgt'
        package_dir.mkdir()
        setup_file.touch()
        target_dir.mkdir()

        mock_popen.return_value.communicate.return_value = ('output', '')
        mock_popen.return_value.wait.return_value = 0

        pdu._build_wheel(package_dir.as_posix(),
                         target_dir=target_dir.as_posix())

        expected_args = [
            sys.executable, 'setup.py', 'bdist_wheel', '-d',
            target_dir.as_posix()
        ]
        mock_popen.assert_called_once_with(expected_args,
                                           cwd=package_dir.as_posix(),
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT)
