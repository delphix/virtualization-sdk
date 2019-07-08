#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import json
import os
import uuid
from collections import OrderedDict

import mock
import pytest
from dlpx.virtualization._internal import exceptions, plugin_util
from dlpx.virtualization._internal.plugin_validator import PluginValidator
from dlpx.virtualization._internal.util_classes import ValidationMode


@pytest.fixture
def plugin_config_file(tmpdir):
    return os.path.join(tmpdir.strpath, 'plugin_config.yml')


@pytest.fixture
def src_dir(tmpdir):
    tmpdir.mkdir('src')
    return os.path.join(tmpdir.strpath, 'src')


class TestPluginValidator:
    @staticmethod
    @pytest.mark.parametrize(
        'schema_content',
        ['{}\nNOT JSON'.format(json.dumps({'random': 'json'}))])
    def test_plugin_bad_schema(plugin_config_file, schema_file):
        plugin_config_content = OrderedDict([
            ('name', 'staged'.encode('utf-8')),
            ('prettyName', 'StagedPlugin'.encode('utf-8')),
            ('version', '0.1.0'), ('language', 'PYTHON27'),
            ('hostTypes', ['UNIX']), ('pluginType', 'STAGED'.encode('utf-8')),
            ('manualDiscovery', True),
            ('entryPoint', 'staged_plugin:staged'.encode('utf-8')),
            ('srcDir', src_dir), ('schemaFile', 'schema.json'.encode('utf-8'))
        ])
        with pytest.raises(exceptions.UserError) as err_info:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content, schema_file,
                ValidationMode.ERROR)
            validator.validate()

        message = err_info.value.message
        assert ('Failed to load schemas because {!r} is not a valid json file.'
                ' Error: Extra data: line 2 column 1 - line 2 column 9'
                ' (char 19 - 27)'.format(schema_file)) in message

    @staticmethod
    def test_plugin_bad_config_file(plugin_config_file):
        with pytest.raises(exceptions.UserError) as err_info:
            validator = PluginValidator(plugin_config_file,
                                        plugin_util.PLUGIN_CONFIG_SCHEMA,
                                        ValidationMode.ERROR, True)
            validator.validate()

        message = err_info.value.message
        assert message == ("Unable to read plugin config file '{}'"
                           "\nError code: 2. Error message: No such file or"
                           " directory".format(plugin_config_file))

    @staticmethod
    @mock.patch.object(PluginValidator,
                       '_PluginValidator__import_plugin',
                       return_value=({}, None))
    def test_plugin_valid_content(mock_import_plugin, src_dir,
                                  plugin_config_file):
        plugin_config_content = OrderedDict([
            ('id', str(uuid.uuid4())), ('name', 'staged'.encode('utf-8')),
            ('version', '0.1.0'), ('language', 'PYTHON27'),
            ('hostTypes', ['UNIX']), ('pluginType', 'STAGED'.encode('utf-8')),
            ('manualDiscovery', True),
            ('entryPoint', 'staged_plugin:staged'.encode('utf-8')),
            ('srcDir', src_dir), ('schemaFile', 'schema.json'.encode('utf-8'))
        ])

        validator = PluginValidator.from_config_content(
            plugin_config_file, plugin_config_content,
            plugin_util.PLUGIN_CONFIG_SCHEMA, ValidationMode.ERROR)
        validator.validate()

        mock_import_plugin.assert_called()

    @staticmethod
    def test_plugin_missing_field(plugin_config_file):
        plugin_config_content = OrderedDict([
            ('name', 'staged'.encode('utf-8')), ('version', '0.1.0'),
            ('language', 'PYTHON27'), ('hostTypes', ['UNIX']),
            ('pluginType', 'STAGED'.encode('utf-8')),
            ('manualDiscovery', True),
            ('entryPoint', 'staged_plugin:staged'.encode('utf-8')),
            ('schemaFile', 'schema.json'.encode('utf-8'))
        ])

        with pytest.raises(exceptions.SchemaValidationError) as err_info:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                plugin_util.PLUGIN_CONFIG_SCHEMA, ValidationMode.ERROR)
            validator.validate()
        message = err_info.value.message
        assert "'srcDir' is a required property" in message

    @staticmethod
    @mock.patch.object(PluginValidator,
                       '_PluginValidator__import_plugin',
                       return_value=({}, None))
    @pytest.mark.parametrize('version, expected', [
        pytest.param('xxx', "'xxx' does not match"),
        pytest.param('1.0.0', None),
        pytest.param('1.0.0_HF', None)
    ])
    def test_plugin_version_format(mock_import_plugin, src_dir,
                                   plugin_config_file, version, expected):
        plugin_config_content = OrderedDict([
            ('id', str(uuid.uuid4())), ('name', 'staged'.encode('utf-8')),
            ('version', version), ('language', 'PYTHON27'),
            ('hostTypes', ['UNIX']), ('pluginType', 'STAGED'.encode('utf-8')),
            ('manualDiscovery', True),
            ('entryPoint', 'staged_plugin:staged'.encode('utf-8')),
            ('srcDir', src_dir), ('schemaFile', 'schema.json'.encode('utf-8'))
        ])

        try:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                plugin_util.PLUGIN_CONFIG_SCHEMA, ValidationMode.ERROR)
            validator.validate()
            mock_import_plugin.assert_called()
        except exceptions.SchemaValidationError as err_info:
            message = err_info.message
            assert expected in message

    @staticmethod
    @mock.patch.object(PluginValidator,
                       '_PluginValidator__import_plugin',
                       return_value=({}, None))
    @pytest.mark.parametrize('entry_point, expected', [
        pytest.param('staged_plugin', "'staged_plugin' does not match"),
        pytest.param(':staged_plugin', "':staged_plugin' does not match"),
        pytest.param('staged:', "'staged:' does not match"),
        pytest.param('staged_plugin::staged',
                     "'staged_plugin::staged' does not match"),
        pytest.param(':staged_plugin:staged:',
                     "':staged_plugin:staged:' does not match"),
        pytest.param('staged_plugin:staged', None)
    ])
    def test_plugin_entry_point(mock_import_plugin, src_dir,
                                plugin_config_file, entry_point, expected):
        plugin_config_content = OrderedDict([
            ('id', str(uuid.uuid4())), ('name', 'staged'.encode('utf-8')),
            ('version', '1.0.0'), ('language', 'PYTHON27'),
            ('hostTypes', ['UNIX']), ('pluginType', 'STAGED'.encode('utf-8')),
            ('manualDiscovery', True),
            ('entryPoint', entry_point.encode('utf-8')), ('srcDir', src_dir),
            ('schemaFile', 'schema.json'.encode('utf-8'))
        ])

        try:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                plugin_util.PLUGIN_CONFIG_SCHEMA, ValidationMode.ERROR)
            validator.validate()
            mock_import_plugin.assert_called()
        except exceptions.SchemaValidationError as err_info:
            message = err_info.message
            assert expected in message

    @staticmethod
    def test_plugin_additional_properties(src_dir, plugin_config_file):
        plugin_config_content = OrderedDict([
            ('id', str(uuid.uuid4())), ('name', 'staged'.encode('utf-8')),
            ('version', '1.0.0'), ('language', 'PYTHON27'),
            ('hostTypes', ['UNIX']), ('pluginType', 'STAGED'.encode('utf-8')),
            ('manualDiscovery', True),
            ('entryPoint', 'staged_plugin:staged'.encode('utf-8')),
            ('unknown_key', 'unknown_value'.encode('utf-8')),
            ('srcDir', src_dir), ('schemaFile', 'schema.json'.encode('utf-8'))
        ])

        try:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                plugin_util.PLUGIN_CONFIG_SCHEMA, ValidationMode.ERROR)
            validator.validate()
        except exceptions.SchemaValidationError as err_info:
            message = err_info.message
            assert "Additional properties are not allowed " \
                   "('unknown_key' was unexpected)" in message

    @staticmethod
    def test_multiple_validation_errors(plugin_config_file):
        plugin_config_content = OrderedDict([
            ('id', str(uuid.uuid4())), ('name', 'staged'.encode('utf-8')),
            ('version', '0.1.0'), ('language', 'PYTHON27'),
            ('hostTypes', ['xxx']), ('pluginType', 'STAGED'.encode('utf-8')),
            ('manualDiscovery', True),
            ('entryPoint', 'staged_plugin:staged'.encode('utf-8')),
            ('schemaFile', 'schema.json'.encode('utf-8'))
        ])

        with pytest.raises(exceptions.SchemaValidationError) as err_info:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                plugin_util.PLUGIN_CONFIG_SCHEMA, ValidationMode.ERROR)
            validator.validate()
        message = err_info.value.message
        assert "'srcDir' is a required property" in message
        assert "'xxx' is not one of ['UNIX', 'WINDOWS']" in message

    @staticmethod
    def test_staged_plugin(fake_staged_plugin_config):
        with pytest.raises(exceptions.UserError) as err_info:
            validator = PluginValidator(fake_staged_plugin_config,
                                        plugin_util.PLUGIN_CONFIG_SCHEMA,
                                        ValidationMode.ERROR, True)
            validator.validate()

        message = err_info.value.message
        assert validator.result.warnings.items() > 0
        assert 'Named argument mismatch in method' in message
        assert 'Number of arguments do not match' in message
        assert 'Implementation missing for required method' in message

    @staticmethod
    def test_direct_plugin(fake_direct_plugin_config):
        with pytest.raises(exceptions.UserError) as err_info:
            validator = PluginValidator(fake_direct_plugin_config,
                                        plugin_util.PLUGIN_CONFIG_SCHEMA,
                                        ValidationMode.ERROR, True)
            validator.validate()

        message = err_info.value.message
        assert validator.result.warnings.items() > 0
        assert 'Named argument mismatch in method' in message
        assert 'Number of arguments do not match' in message
        assert 'Implementation missing for required method' in message

    @staticmethod
    @mock.patch.object(PluginValidator,
                       '_PluginValidator__import_plugin',
                       return_value=({}, None))
    @pytest.mark.parametrize('plugin_id , expected', [
        pytest.param('Staged_plugin', "'Staged_plugin' does not match"),
        pytest.param('staged_Plugin', "'staged_Plugin' does not match"),
        pytest.param('STAGED', "'STAGED' does not match"),
        pytest.param('E3b69c61-4c30-44f7-92c0-504c8388b91e', None),
        pytest.param('e3b69c61-4c30-44f7-92c0-504c8388b91e', None)
    ])
    def test_plugin_id(mock_import_plugin, src_dir, plugin_config_file,
                       plugin_id, expected):
        plugin_config_content = OrderedDict([
            ('id', plugin_id.encode('utf-8')), ('name', 'python_vfiles'),
            ('version', '1.0.0'), ('language', 'PYTHON27'),
            ('hostTypes', ['UNIX']), ('pluginType', 'STAGED'.encode('utf-8')),
            ('manualDiscovery', True),
            ('entryPoint', 'staged_plugin:staged'.encode('utf-8')),
            ('srcDir', src_dir), ('schemaFile', 'schema.json'.encode('utf-8'))
        ])

        try:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                plugin_util.PLUGIN_CONFIG_SCHEMA, ValidationMode.ERROR)
            validator.validate()
            mock_import_plugin.assert_called()
        except exceptions.SchemaValidationError as err_info:
            message = err_info.message
            assert expected in message

    @staticmethod
    @pytest.mark.parametrize('validation_mode',
                             [ValidationMode.INFO, ValidationMode.WARNING])
    def test_plugin_info_warn_mode(plugin_config_file, validation_mode):
        plugin_config_content = OrderedDict([
            ('id', str(uuid.uuid4())), ('name', 'staged'.encode('utf-8')),
            ('version', '0.1.0'), ('language', 'PYTHON27'),
            ('hostTypes', ['UNIX']), ('pluginType', 'STAGED'.encode('utf-8')),
            ('manualDiscovery', True),
            ('entryPoint', 'staged_plugin:staged'.encode('utf-8')),
            ('schemaFile', 'schema.json'.encode('utf-8'))
        ])
        err_info = None
        try:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                plugin_util.PLUGIN_CONFIG_SCHEMA, validation_mode)
            validator.validate()
        except Exception as e:
            err_info = e

        assert err_info is None
