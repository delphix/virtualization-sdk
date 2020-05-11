#
# Copyright (c) 2019, 2020 by Delphix. All rights reserved.
#

import json

import mock
import pytest
from dlpx.virtualization._internal import const, exceptions
from dlpx.virtualization._internal.plugin_validator import PluginValidator


class TestPluginValidator:
    @staticmethod
    @pytest.mark.parametrize(
        'schema_content',
        ['{}\nNOT JSON'.format(json.dumps({'random': 'json'}))])
    def test_plugin_bad_schema(plugin_config_file, plugin_config_content,
                               schema_file):
        with pytest.raises(exceptions.UserError) as err_info:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content, schema_file)
            validator.validate_plugin_config()

        message = err_info.value.message
        assert ('Failed to load schemas because {} is not a valid json file.'
                ' Error: Extra data: line 2 column 1 - line 2 column 9'
                ' (char 19 - 27)'.format(schema_file)) in message

    @staticmethod
    @pytest.mark.parametrize('plugin_config_file', ['/dir/plugin_config.yml'])
    def test_plugin_bad_config_file(plugin_config_file):
        with pytest.raises(exceptions.UserError) as err_info:
            validator = PluginValidator(plugin_config_file,
                                        const.PLUGIN_CONFIG_SCHEMA)
            validator.validate_plugin_config()

        message = err_info.value.message
        assert message == ("Unable to read plugin config file '{}'"
                           "\nError code: 2. Error message: No such file or"
                           " directory".format(plugin_config_file))

    @staticmethod
    @mock.patch('os.path.isabs', return_value=False)
    def test_plugin_valid_content(src_dir, plugin_config_file,
                                  plugin_config_content):
        validator = PluginValidator.from_config_content(
            plugin_config_file, plugin_config_content,
            const.PLUGIN_CONFIG_SCHEMA)
        validator.validate_plugin_config()

    @staticmethod
    @pytest.mark.parametrize('src_dir', [None])
    def test_plugin_missing_field(plugin_config_file, plugin_config_content):
        with pytest.raises(exceptions.SchemaValidationError) as err_info:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                const.PLUGIN_CONFIG_SCHEMA)
            validator.validate_plugin_config()
        message = err_info.value.message
        assert "'srcDir' is a required property" in message

    @staticmethod
    @mock.patch('os.path.isabs', return_value=False)
    @pytest.mark.parametrize('external_version,expected',
                             [(1, "1 is not of type 'string'"),
                              (1.0, "1.0 is not of type 'string'"),
                              ('my_version', None), ('1.0.0', None),
                              ('1.0.0_HF', None)])
    def test_plugin_version_format(src_dir, plugin_config_file,
                                   plugin_config_content, expected):
        try:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                const.PLUGIN_CONFIG_SCHEMA)
            validator.validate_plugin_config()
        except exceptions.SchemaValidationError as err_info:
            message = err_info.message
            assert expected in message

    @staticmethod
    @mock.patch('os.path.isabs', return_value=False)
    @pytest.mark.parametrize(
        'entry_point,expected',
        [('staged_plugin', "'staged_plugin' does not match"),
         (':staged_plugin', "':staged_plugin' does not match"),
         ('staged:', "'staged:' does not match"),
         ('staged_plugin::staged', "'staged_plugin::staged' does not match"),
         (':staged_plugin:staged:', "':staged_plugin:staged:' does not match"),
         ('staged_plugin:staged', None)])
    def test_plugin_entry_point(src_dir, plugin_config_file,
                                plugin_config_content, expected):
        try:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                const.PLUGIN_CONFIG_SCHEMA)
            validator.validate_plugin_config()
        except exceptions.SchemaValidationError as err_info:
            message = err_info.message
            assert expected in message

    @staticmethod
    def test_plugin_additional_properties(src_dir, plugin_config_file,
                                          plugin_config_content):
        # Adding an unknown key
        plugin_config_content['unknown_key'] = 'unknown_value'

        try:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                const.PLUGIN_CONFIG_SCHEMA)
            validator.validate_plugin_config()
        except exceptions.SchemaValidationError as err_info:
            message = err_info.message
            assert ("Additional properties are not allowed"
                    " ('unknown_key' was unexpected)" in message)

    @staticmethod
    @pytest.mark.parametrize('host_types', [['xxx']])
    @pytest.mark.parametrize('src_dir', [None])
    def test_multiple_validation_errors(plugin_config_file,
                                        plugin_config_content):
        with pytest.raises(exceptions.SchemaValidationError) as err_info:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                const.PLUGIN_CONFIG_SCHEMA)
            validator.validate_plugin_config()
        message = err_info.value.message
        assert "'srcDir' is a required property" in message
        assert "'xxx' is not one of ['UNIX', 'WINDOWS']" in message

    @staticmethod
    @mock.patch('os.path.isabs', return_value=False)
    @pytest.mark.parametrize(
        'plugin_id , expected',
        [('Staged_plugin', "'Staged_plugin' does not match"),
         ('staged_Plugin', "'staged_Plugin' does not match"),
         ('STAGED', "'STAGED' does not match"),
         ('E3b69c61-4c30-44f7-92c0-504c8388b91e', None),
         ('e3b69c61-4c30-44f7-92c0-504c8388b91e', None)])
    def test_plugin_id(mock_import_plugin, src_dir, plugin_config_file,
                       plugin_config_content, expected):
        try:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                const.PLUGIN_CONFIG_SCHEMA)
            validator.validate_plugin_config()
        except exceptions.SchemaValidationError as err_info:
            message = err_info.message
            assert expected in message

    @staticmethod
    @mock.patch('os.path.isabs', return_value=False)
    @pytest.mark.parametrize('build_number, expected',
                             [('xxx', "'xxx' does not match"), ('1', None),
                              ('1.x', "'1.x' does not match"), ('1.100', None),
                              ('0.1.2', None), ('02.5000', None),
                              (None, "'buildNumber' is a required property"),
                              ('1.0.0_HF', "'1.0.0_HF' does not match"),
                              ('0.0.0', "'0.0.0' does not match"),
                              ('0', "'0' does not match"),
                              ('0.0.00', "'0.0.00' does not match"),
                              ('0.1', None)])
    def test_plugin_build_number_format(src_dir, plugin_config_file,
                                        plugin_config_content, expected):
        try:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                const.PLUGIN_CONFIG_SCHEMA)
            validator.validate_plugin_config()
        except exceptions.SchemaValidationError as err_info:
            message = err_info.message
            assert expected in message

    @staticmethod
    @mock.patch('os.path.isabs', return_value=False)
    @pytest.mark.parametrize(
        'lua_name, expected',
        [('lua toolkit', "'lua toolkit' does not match"),
         ('!lua#toolkit', "'!lua#toolkit' does not match")])
    def test_plugin_lua_name_format(src_dir, plugin_config_file,
                                    plugin_config_content, expected):
        try:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                const.PLUGIN_CONFIG_SCHEMA)
            validator.validate_plugin_config()
        except exceptions.SchemaValidationError as err_info:
            message = err_info.message
            assert expected in message

    @staticmethod
    @mock.patch('os.path.isabs', return_value=False)
    @pytest.mark.parametrize('minimum_lua_version, expected',
                             [('1-2-3', "'1-2-3' does not match"),
                              ('version1.0!', "'version1.0!' does not match"),
                              ('2.3.4', "'2.3.4' does not match")])
    def test_plugin_minimum_lua_version_format(src_dir, plugin_config_file,
                                               plugin_config_content,
                                               expected):
        try:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                const.PLUGIN_CONFIG_SCHEMA)
            validator.validate_plugin_config()
        except exceptions.SchemaValidationError as err_info:
            message = err_info.message
            assert expected in message

    @staticmethod
    def test_plugin_lua_name_without_minimum_lua_version(
            src_dir, plugin_config_file,
            plugin_config_content_missing_minimum_lua_version):
        try:
            validator = PluginValidator.from_config_content(
                plugin_config_file,
                plugin_config_content_missing_minimum_lua_version,
                const.PLUGIN_CONFIG_SCHEMA)
            validator.validate_plugin_config()
        except exceptions.ValidationFailedError as err_info:
            message = err_info.message
            assert ('Failed to process property "luaName" without '
                    '"minimumLuaVersion" set in the plugin config.' in message)

    @staticmethod
    def test_plugin_minimum_lua_version_without_lua_name(
            src_dir, plugin_config_file,
            plugin_config_content_missing_lua_name):
        try:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content_missing_lua_name,
                const.PLUGIN_CONFIG_SCHEMA)
            validator.validate_plugin_config()
        except exceptions.ValidationFailedError as err_info:
            message = err_info.message
            assert ('Failed to process property "minimumLuaVersion" without '
                    '"luaName" set in the plugin config.' in message)
