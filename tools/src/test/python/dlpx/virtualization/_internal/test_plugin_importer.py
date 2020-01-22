#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
import exceptions
import os
import uuid
from collections import OrderedDict

import mock
import pytest
import yaml
from dlpx.virtualization._internal import (file_util, plugin_util,
                                           plugin_validator)
from dlpx.virtualization._internal.plugin_importer import PluginImporter


@pytest.fixture
def fake_src_dir(plugin_type):
    """
    This fixture gets the path of the fake plugin src files used for testing
    """
    return os.path.join(os.path.dirname(__file__), 'fake_plugin',
                        plugin_type.lower())


def get_plugin_importer(plugin_config_file):
    plugin_config_content = None
    with open(plugin_config_file, 'rb') as f:
        plugin_config_content = yaml.safe_load(f)

    src_dir = file_util.get_src_dir_path(plugin_config_file,
                                         plugin_config_content['srcDir'])
    entry_point_module, entry_point_object = plugin_validator.PluginValidator\
        .split_entry_point(plugin_config_content['entryPoint'])
    plugin_type = plugin_config_content['pluginType']

    return PluginImporter(src_dir, entry_point_module, entry_point_object,
                          plugin_type, True)


class TestPluginImporter:
    @staticmethod
    @mock.patch('importlib.import_module')
    def test_get_plugin_manifest(mock_import, src_dir, plugin_type,
                                 entry_point_module, entry_point_object,
                                 plugin_module_content, plugin_manifest):
        mock_import.return_value = plugin_module_content

        importer = PluginImporter(src_dir, entry_point_module,
                                  entry_point_object, plugin_type, False)
        importer.validate_plugin_module()

        assert importer.result.plugin_manifest == plugin_manifest

    @staticmethod
    @mock.patch('importlib.import_module')
    def test_plugin_module_content_none(mock_import, src_dir, plugin_type,
                                        entry_point_module,
                                        entry_point_object):
        mock_import.return_value = None
        result = ()

        with pytest.raises(exceptions.UserError) as err_info:
            importer = PluginImporter(src_dir, entry_point_module,
                                      entry_point_object, plugin_type, False)
            importer.validate_plugin_module()
            result = importer.result

        message = str(err_info)
        assert result == ()
        assert 'Plugin module content is None.' in message

    @staticmethod
    @mock.patch('importlib.import_module')
    def test_plugin_entry_object_none(mock_import, src_dir, plugin_type,
                                      plugin_name, plugin_module_content):
        mock_import.return_value = plugin_module_content
        result = ()

        with pytest.raises(exceptions.UserError) as err_info:
            importer = PluginImporter(src_dir, plugin_name, None, plugin_type,
                                      False)
            importer.validate_plugin_module()
            result = importer.result

        message = str(err_info)
        assert result == ()
        assert 'Plugin entry point object is None.' in message

    @staticmethod
    @mock.patch('importlib.import_module')
    def test_plugin_entry_point_nonexistent(mock_import, src_dir, plugin_type,
                                            plugin_name,
                                            plugin_module_content):
        entry_point_name = "nonexistent entry point"
        mock_import.return_value = plugin_module_content
        result = ()

        with pytest.raises(exceptions.UserError) as err_info:
            importer = PluginImporter(src_dir, plugin_name, entry_point_name,
                                      plugin_type, False)
            importer.validate_plugin_module()
            result = importer.result

        message = err_info.value.message
        assert result == ()
        assert ('\'{}\' is not a symbol in module'.format(entry_point_name) in
                message)

    @staticmethod
    @mock.patch('importlib.import_module')
    def test_plugin_object_none(mock_import, src_dir, plugin_type, plugin_name,
                                plugin_module_content):
        none_entry_point = "none_entry_point"
        setattr(plugin_module_content, none_entry_point, None)

        mock_import.return_value = plugin_module_content
        result = ()

        with pytest.raises(exceptions.UserError) as err_info:
            importer = PluginImporter(src_dir, plugin_name, none_entry_point,
                                      plugin_type, False)
            importer.validate_plugin_module()
            result = importer.result

        message = err_info.value.message
        assert result == ()
        assert ('Plugin object retrieved from the entry point {} is'
                ' None'.format(none_entry_point)) in message

    @staticmethod
    @pytest.mark.parametrize('entry_point,plugin_type',
                             [('successful:staged', 'STAGED'),
                              ('successful:direct', 'DIRECT')])
    @mock.patch('dlpx.virtualization._internal.file_util.get_src_dir_path')
    def test_successful_validation(mock_file_util, plugin_config_file,
                                   fake_src_dir):
        mock_file_util.return_value = fake_src_dir
        importer = get_plugin_importer(plugin_config_file)
        importer.validate_plugin_module()

    @staticmethod
    @pytest.mark.parametrize(
        'entry_point,plugin_type,expected_errors',
        [('multiple_warnings:staged', 'STAGED', [
            'Error: Named argument mismatch in method repository_discovery',
            'Error: Number of arguments do not match in method stop',
            'Error: Named argument mismatch in method stop',
            'Warning: Implementation missing for required method'
            ' virtual.mount_specification().', '1 Warning(s). 3 Error(s).'
        ]),
         ('multiple_warnings:vfiles', 'DIRECT', [
             'Error: Number of arguments do not match in method status',
             'Error: Named argument mismatch in method status',
             'Warning: Implementation missing for required method'
             ' virtual.reconfigure().', '1 Warning(s). 2 Error(s).'
         ])])
    @mock.patch('dlpx.virtualization._internal.file_util.get_src_dir_path')
    def test_multiple_warnings(mock_file_util, plugin_config_file,
                               fake_src_dir, expected_errors):
        mock_file_util.return_value = fake_src_dir

        with pytest.raises(exceptions.UserError) as err_info:
            importer = get_plugin_importer(plugin_config_file)
            importer.validate_plugin_module()

        message = err_info.value.message
        for error in expected_errors:
            assert error in message

    @staticmethod
    @pytest.mark.parametrize(
        'entry_point,expected_errors', [('upgrade_warnings:direct', [
            'Error: Named argument mismatch in method snap_upgrade.',
            'Error: Number of arguments do not match in method ls_upgrade.',
            'Error: Named argument mismatch in method ls_upgrade.',
            'Error: Named argument mismatch in method ls_upgrade.',
            '0 Warning(s). 4 Error(s).'
        ])])
    @mock.patch('dlpx.virtualization._internal.file_util.get_src_dir_path')
    def test_upgrade_warnings(mock_file_util, plugin_config_file, fake_src_dir,
                              expected_errors):
        mock_file_util.return_value = fake_src_dir

        with pytest.raises(exceptions.UserError) as err_info:
            importer = get_plugin_importer(plugin_config_file)
            importer.validate_plugin_module()

        message = err_info.value.message
        for error in expected_errors:
            assert error in message

    @staticmethod
    @pytest.mark.parametrize(
        'entry_point,expected_error',
        [('op_already_defined:plugin', 'has already been defined'),
         ('dec_not_function:plugin', "decorated by 'linked.pre_snapshot()'"
          " is not a function"),
         ('id_not_string:plugin', "The migration id '['testing', 'out',"
          " 'validation']' used in the function"
          " 'repo_upgrade' should be a string."),
         ('id_bad_format:plugin', "used in the function 'repo_upgrade' does"
          " not follow the correct format"),
         ('id_used:plugin', "'5.04.000.01' used in the function 'snap_upgrade'"
          " has the same canonical form '5.4.0.1' as another migration")])
    @mock.patch('dlpx.virtualization._internal.file_util.get_src_dir_path')
    def test_wrapper_failures(mock_file_util, plugin_config_file, fake_src_dir,
                              expected_error):
        mock_file_util.return_value = fake_src_dir

        with pytest.raises(exceptions.UserError) as err_info:
            importer = get_plugin_importer(plugin_config_file)
            importer.validate_plugin_module()

        message = err_info.value.message
        assert expected_error in message
        assert '0 Warning(s). 1 Error(s).' in message

    @staticmethod
    @pytest.mark.parametrize('entry_point', ['arbitrary_error:plugin'])
    @mock.patch('dlpx.virtualization._internal.file_util.get_src_dir_path')
    def test_sdk_error(mock_file_util, plugin_config_file, fake_src_dir):
        mock_file_util.return_value = fake_src_dir

        with pytest.raises(exceptions.SDKToolingError) as err_info:
            importer = get_plugin_importer(plugin_config_file)
            importer.validate_plugin_module()

        message = err_info.value.message
        assert ('SDK Error: Got an arbitrary non-platforms error for testing.'
                in message)
        assert '0 Warning(s). 1 Error(s).' in message

    @staticmethod
    @mock.patch('os.path.isabs', return_value=False)
    @mock.patch('importlib.import_module')
    def test_plugin_info_warn_mode(mock_import, mock_relative_path,
                                   plugin_config_file, src_dir,
                                   plugin_module_content):
        plugin_config_content = OrderedDict([
            ('id', str(uuid.uuid4())), ('name', 'staged'.encode('utf-8')),
            ('version', '0.1.0'), ('language', 'PYTHON27'),
            ('hostTypes', ['UNIX']), ('pluginType', 'STAGED'.encode('utf-8')),
            ('manualDiscovery', True),
            ('entryPoint', 'staged_plugin:staged'.encode('utf-8')),
            ('srcDir', src_dir), ('schemaFile', 'schema.json'.encode('utf-8'))
        ])
        mock_import.return_value = plugin_module_content
        try:
            plugin_util.get_plugin_manifest(plugin_config_file,
                                            plugin_config_content, False)
        except Exception:
            raise AssertionError()
