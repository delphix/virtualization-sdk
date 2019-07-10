#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import os

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
    def test_get_src_dir_path(tmpdir):
        test_file = os.path.join(tmpdir.strpath, 'test_file')
        src_dir = file_util.get_src_dir_path(test_file, tmpdir.strpath)
        assert src_dir == tmpdir.strpath

    @staticmethod
    def test_get_src_dir_path_fail(tmpdir):
        test_file = os.path.join(tmpdir.strpath, 'test_file')
        expected_message = 'The path \'{}\' does not exist'.format(test_file)
        with pytest.raises(exceptions.UserError) as err_info:
            file_util.get_src_dir_path(test_file, test_file)

        message = err_info.value.message
        assert expected_message in message

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
