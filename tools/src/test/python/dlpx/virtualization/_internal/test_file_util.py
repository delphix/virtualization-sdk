#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import os

import mock
import pytest
from dlpx.virtualization._internal import exceptions, file_util


class TestFileUtil:
    @staticmethod
    def test_delete_paths(plugin_config_file, schema_file, src_dir):
        file_util.delete_paths(plugin_config_file, schema_file, src_dir)

        assert not os.path.exists(plugin_config_file)
        assert not os.path.exists(schema_file)
        assert not os.path.exists(src_dir)

    @staticmethod
    def test_delete_paths_none_values(plugin_config_file):
        file_util.delete_paths(plugin_config_file, None)

        assert not os.path.exists(plugin_config_file)

    @staticmethod
    def test_get_src_dir_path_is_abs_fail():
        expected_message = "The path '{}' should be a relative path, but is " \
                           "not.".format('/absolute/path')
        with pytest.raises(exceptions.UserError) as err_info:
            file_util.get_src_dir_path('/absolute/path', '/absolute/path')
        message = err_info.value.message
        assert expected_message in message

    @staticmethod
    def test_get_src_dir_path_exists_fail():
        expected_message = "The path '{}' does not exist.".format(
            'nonexistent/path')
        with pytest.raises(exceptions.UserError) as err_info:
            file_util.get_src_dir_path('nonexistent/path', 'nonexistent/path')
        message = err_info.value.message
        assert expected_message in message

    @staticmethod
    @mock.patch('os.path.isabs', return_value=False)
    @mock.patch('os.path.exists', return_value=True)
    def test_get_src_dir_path_is_dir_fail(mock_existing_path,
                                          mock_relative_path):
        expected_message = "The path '{}' should be a {} but is not.".format(
            'path/to/a/file', 'directory')
        with pytest.raises(exceptions.UserError) as err_info:
            file_util.get_src_dir_path('path/to/a/file', 'path/to/a/file')
        message = err_info.value.message
        assert expected_message in message

    @staticmethod
    @mock.patch('os.path.isdir', return_value=True)
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.path.isabs', return_value=False)
    @pytest.mark.parametrize(
        'plugin_config_file_path, src_dir_path',
        [(os.path.join(os.getenv('HOME'), 'plugin/file_name'), '.'),
         ('/mongo/file_name', '/src'), ('/plugin/mongo/file_name', '/plugin'),
         ('/plugin/file_name', '/plugin/src/../..')])
    def test_get_src_dir_path_fail(mock_relative_path, mock_existing_path,
                                   mock_directory_path,
                                   plugin_config_file_path, src_dir_path):
        expected_plugin_root_dir = os.path.dirname(plugin_config_file_path)

        expected_plugin_root_dir = file_util.standardize_path(
            expected_plugin_root_dir)
        expected_src_dir = file_util.standardize_path(src_dir_path)

        expected_src_dir = os.path.join(expected_plugin_root_dir,
                                        expected_src_dir)

        expected_message = "The src directory {} is not a subdirectory of " \
                           "the plugin root at {}"\
            .format(expected_src_dir,
                    os.path.dirname(expected_plugin_root_dir))
        with pytest.raises(exceptions.UserError) as err_info:
            file_util.get_src_dir_path(plugin_config_file_path, src_dir_path)
        message = err_info.value.message
        assert expected_message in message

    @staticmethod
    @mock.patch('os.path.isdir', return_value=True)
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('os.path.isabs', return_value=False)
    @pytest.mark.parametrize(
        'plugin_config_file_path, src_dir_path',
        [(os.path.join(os.path.dirname(os.getcwd()),
                       'plugin/filename'), '../plugin/src'),
         (os.path.join(os.getenv('HOME'), 'plugin/file_name'), '~/plugin/src'),
         (os.path.join(os.getcwd(), 'plugin/file_name'), './plugin/src'),
         ('/UPPERCASE/file_name', '/UPPERCASE/src'),
         ('/mongo/file_name', '/mongo/src/main/python'),
         ('~/plugin/file_name', '~/plugin/src'),
         (r'windows\path\some_file', r'windows\path')])
    def test_get_src_dir_path_success(mock_relative_path, mock_existing_path,
                                      mock_directory_path,
                                      plugin_config_file_path, src_dir_path):
        file_util.get_src_dir_path(plugin_config_file_path, src_dir_path)

    @staticmethod
    def test_make_dir_success(tmpdir):
        testdir = os.path.join(tmpdir.strpath, 'test_dir')
        file_util.make_dir(testdir, True)
        assert os.path.exists(testdir)
        assert os.path.isdir(testdir)

    @staticmethod
    def test_make_dir_fail():
        testdir = '/dir/that/does/not/exist/test_dir'
        with pytest.raises(exceptions.UserError) as err_info:
            file_util.make_dir(testdir, True)

        message = err_info.value.message
        assert message == ("Unable to create new directory"
                           " '/dir/that/does/not/exist/test_dir'"
                           "\nError code: 2."
                           " Error message: No such file or directory")

    @staticmethod
    def test_make_dir_force_fail(tmpdir):
        with pytest.raises(exceptions.UserError) as err_info:
            file_util.make_dir(tmpdir.strpath, False)

        message = err_info.value.message
        assert "Error code: 17. Error message: File exists" in message
