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
    def test_get_src_dir_path_relative(tmp_path):
        plugin_root = tmp_path / 'plugin'
        src_dir = plugin_root / 'src'
        plugin_root.mkdir()
        src_dir.mkdir()

        cwd = os.getcwd()
        try:
            os.chdir(tmp_path.as_posix())
            actual = file_util.get_src_dir_path('plugin/plugin_config.yml',
                                                'src')
        finally:
            os.chdir(cwd)

        assert actual == src_dir.as_posix()

    @staticmethod
    def test_get_src_dir_path_is_abs_fail():
        expected_message = "The path '{}' should be a relative path, but is " \
                           "not.".format('/absolute/src')
        with pytest.raises(exceptions.UserError) as err_info:
            file_util.get_src_dir_path('/absolute/config', '/absolute/src')
        message = err_info.value.message
        assert expected_message in message

    @staticmethod
    def test_get_src_dir_path_exists_fail():
        expected_path = os.path.join(os.getcwd(), 'fake', 'nonexistent', 'dir')
        expected_message = "The path '{}' does not exist.".format(
            expected_path)
        with pytest.raises(exceptions.UserError) as err_info:
            file_util.get_src_dir_path('fake/plugin_config', 'nonexistent/dir')
        message = err_info.value.message
        assert expected_message in message

    @staticmethod
    @mock.patch('os.path.isabs', return_value=False)
    @mock.patch('os.path.exists', return_value=True)
    def test_get_src_dir_path_is_dir_fail(mock_existing_path,
                                          mock_relative_path):
        expected_path = os.path.join(os.getcwd(), 'fake', 'not', 'dir')
        expected_message = "The path '{}' should be a {} but is not.".format(
            expected_path, 'directory')
        with pytest.raises(exceptions.UserError) as err_info:
            file_util.get_src_dir_path('fake/plugin_config', 'not/dir')
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
        expected_src_dir = file_util.standardize_path(
            os.path.join(expected_plugin_root_dir, src_dir_path))

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

    @staticmethod
    def test_clean_copy_no_tgt_dir(tmp_path):
        #
        # Before:           After:
        #   src/              src/
        #     hello.txt         hello.txt
        #                     tgt/
        #                       hello.txt
        #
        src = tmp_path / 'src'
        src.mkdir()
        f = src / 'hello.txt'
        f.write_text(u'hello')
        tgt = tmp_path / 'tgt'

        file_util.clean_copy(src.as_posix(), tgt.as_posix())

        expected_file = tgt / 'hello.txt'
        assert expected_file.exists()
        assert expected_file.read_text() == 'hello'

    @staticmethod
    def test_clean_copy_removes_tgt_dir(tmp_path):
        #
        # Before:           After:
        #   src/              src/
        #     hello.txt         hello.txt
        #   tgt/              tgt/
        #     remove.txt        hello.txt
        #
        src = tmp_path / 'src'
        src.mkdir()
        src_file = src / 'hello.txt'
        src_file.write_text(u'hello')
        tgt = tmp_path / 'tgt'
        tgt.mkdir()
        tgt_file = tgt / 'remove.txt'
        tgt_file.touch()

        file_util.clean_copy(src.as_posix(), tgt.as_posix())

        expected_file = tgt / 'hello.txt'
        assert expected_file.exists()
        assert expected_file.read_text() == 'hello'
        assert not tgt_file.exists()

    @staticmethod
    def test_clean_copy_nested_tgt_dir(tmp_path):
        #
        # Before:           After:
        #   src/              src/
        #     child/            child/
        #       hello.txt         hello.txt
        #   tgt_parent/       tgt_parent/
        #                       tgt/
        #                         child/
        #                           hello.txt
        #
        src = tmp_path / 'src'
        src.mkdir()
        child = src / 'child'
        child.mkdir()
        src_file = child / 'hello.txt'
        src_file.write_text(u'hello')
        tgt_parent = tmp_path / 'tgt_parent'
        tgt_parent.mkdir()
        tgt = tgt_parent / 'tgt'

        file_util.clean_copy(src.as_posix(), tgt.as_posix())

        expected_file = tgt / 'child' / 'hello.txt'
        assert expected_file.exists()
        assert expected_file.read_text() == 'hello'

    @staticmethod
    def test_tmpdir():
        with file_util.tmpdir() as d:
            assert os.path.exists(d)

        assert not os.path.exists(d)

    @staticmethod
    def test_tmpdir_with_raised_exception():
        try:
            with file_util.tmpdir() as d:
                assert os.path.exists(d)

                raise RuntimeError('test')
        except RuntimeError as e:
            assert e.message == 'test'
            assert not os.path.exists(d)
