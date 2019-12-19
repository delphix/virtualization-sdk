#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
import exceptions

import mock
import pytest
from dlpx.virtualization._internal.plugin_importer import PluginImporter


class TestPluginImporter:
    @staticmethod
    @mock.patch('importlib.import_module')
    def test_get_plugin_manifest(mock_import, src_dir, plugin_type,
                                 plugin_name, plugin_entry_point_name,
                                 plugin_module_content, plugin_manifest):
        mock_import.return_value = plugin_module_content
        importer = PluginImporter(src_dir, plugin_name,
                                  plugin_entry_point_name, plugin_type, False)
        manifest = importer.import_plugin()

        assert manifest == plugin_manifest

    @staticmethod
    @mock.patch('importlib.import_module')
    def test_plugin_module_content_none(mock_import, src_dir, plugin_type,
                                        plugin_name, plugin_entry_point_name):
        mock_import.return_value = None
        manifest = {}

        with pytest.raises(exceptions.UserError) as err_info:
            importer = PluginImporter(src_dir, plugin_name,
                                      plugin_entry_point_name, plugin_type,
                                      False)
            manifest = importer.import_plugin()

        message = str(err_info)
        assert manifest == {}
        assert 'Plugin module content is None.' in message

    @staticmethod
    @mock.patch('importlib.import_module')
    def test_plugin_entry_object_none(mock_import, src_dir, plugin_type,
                                      plugin_name, plugin_module_content):
        mock_import.return_value = plugin_module_content
        manifest = {}

        with pytest.raises(exceptions.UserError) as err_info:
            importer = PluginImporter(src_dir, plugin_name, None, plugin_type,
                                      False)
            manifest = importer.import_plugin()

        message = str(err_info)
        assert manifest == {}
        assert 'Plugin entry point object is None.' in message

    @staticmethod
    @mock.patch('importlib.import_module')
    def test_plugin_entry_point_nonexistent(mock_import, src_dir, plugin_type,
                                            plugin_name,
                                            plugin_module_content):
        entry_point_name = "nonexistent entry point"
        mock_import.return_value = plugin_module_content
        manifest = {}

        with pytest.raises(exceptions.UserError) as err_info:
            importer = PluginImporter(src_dir, plugin_name, entry_point_name,
                                      plugin_type, False)
            manifest = importer.import_plugin()

        message = err_info.value.message
        assert manifest == {}
        assert ('\'{}\' is not a symbol in module'.format(entry_point_name) in
                message)

    @staticmethod
    @mock.patch('importlib.import_module')
    def test_plugin_object_none(mock_import, src_dir, plugin_type, plugin_name,
                                plugin_module_content):
        none_entry_point = "none_entry_point"
        setattr(plugin_module_content, none_entry_point, None)

        mock_import.return_value = plugin_module_content
        manifest = {}

        with pytest.raises(exceptions.UserError) as err_info:
            importer = PluginImporter(src_dir, plugin_name, none_entry_point,
                                      plugin_type, False)
            manifest = importer.import_plugin()

        message = err_info.value.message
        assert manifest == {}
        assert ('Plugin object retrieved from the entry point {} is'
                ' None'.format(none_entry_point)) in message
