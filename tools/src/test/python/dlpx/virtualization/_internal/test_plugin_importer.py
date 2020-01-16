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
                                 plugin_name, plugin_entry_point_name,
                                 plugin_module_content, plugin_manifest):
        mock_import.return_value = plugin_module_content
        importer = PluginImporter(src_dir, plugin_name,
                                  plugin_entry_point_name, plugin_type, False)
        importer.validate_plugin_module()

        assert importer.result.plugin_manifest == plugin_manifest

    @staticmethod
    @mock.patch('importlib.import_module')
    def test_plugin_module_content_none(mock_import, src_dir, plugin_type,
                                        plugin_name, plugin_entry_point_name):
        mock_import.return_value = None
        result = ()

        with pytest.raises(exceptions.UserError) as err_info:
            importer = PluginImporter(src_dir, plugin_name,
                                      plugin_entry_point_name, plugin_type,
                                      False)
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
    @mock.patch('dlpx.virtualization._internal.file_util.get_src_dir_path')
    def test_staged_plugin(mock_file_util, fake_staged_plugin_config):
        src_dir = os.path.dirname(fake_staged_plugin_config)
        mock_file_util.return_value = os.path.join(src_dir, 'src/')
        importer = get_plugin_importer(fake_staged_plugin_config)

        with pytest.raises(exceptions.UserError) as err_info:
            importer.validate_plugin_module()

        message = err_info.value.message
        assert 'Named argument mismatch in method' in message
        assert 'Number of arguments do not match' in message
        assert 'Implementation missing for required method' in message

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.file_util.get_src_dir_path')
    def test_direct_plugin(mock_file_util, fake_direct_plugin_config):
        src_dir = os.path.dirname(fake_direct_plugin_config)
        mock_file_util.return_value = os.path.join(src_dir, 'src/')
        importer = get_plugin_importer(fake_direct_plugin_config)

        with pytest.raises(exceptions.UserError) as err_info:
            importer.validate_plugin_module()

        message = err_info.value.message
        assert 'Named argument mismatch in method' in message
        assert 'Number of arguments do not match' in message
        assert 'Implementation missing for required method' in message

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
