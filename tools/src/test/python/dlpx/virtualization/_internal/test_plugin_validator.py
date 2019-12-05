#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import json
import os

import mock
import pytest
from dlpx.virtualization._internal import exceptions, util_classes
from dlpx.virtualization._internal.plugin_validator import PluginValidator
from dlpx.virtualization._internal.util_classes import ValidationMode


@pytest.fixture
def fake_src_dir(plugin_type):
    """
    This fixture gets the path of the fake plugin src files used for testing
    """
    return os.path.join(os.path.dirname(__file__), 'fake_plugin',
                        plugin_type.lower())


class TestPluginValidator:
    @staticmethod
    @pytest.mark.parametrize(
        'schema_content',
        ['{}\nNOT JSON'.format(json.dumps({'random': 'json'}))])
    def test_plugin_bad_schema(plugin_config_file, plugin_config_content,
                               schema_file):
        with pytest.raises(exceptions.UserError) as err_info:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content, schema_file,
                ValidationMode.ERROR)
            validator.validate()

        message = err_info.value.message
        assert ('Failed to load schemas because {} is not a valid json file.'
                ' Error: Extra data: line 2 column 1 - line 2 column 9'
                ' (char 19 - 27)'.format(schema_file)) in message

    @staticmethod
    @pytest.mark.parametrize('plugin_config_file', ['/dir/plugin_config.yml'])
    def test_plugin_bad_config_file(plugin_config_file):
        with pytest.raises(exceptions.UserError) as err_info:
            validator = PluginValidator(plugin_config_file,
                                        util_classes.PLUGIN_CONFIG_SCHEMA,
                                        ValidationMode.ERROR, True)
            validator.validate()

        message = err_info.value.message
        assert message == ("Unable to read plugin config file '{}'"
                           "\nError code: 2. Error message: No such file or"
                           " directory".format(plugin_config_file))

    @staticmethod
    @mock.patch('os.path.isabs', return_value=False)
    @mock.patch.object(PluginValidator,
                       '_PluginValidator__import_plugin',
                       return_value=({}, None))
    def test_plugin_valid_content(mock_import_plugin, src_dir,
                                  plugin_config_file, plugin_config_content):
        validator = PluginValidator.from_config_content(
            plugin_config_file, plugin_config_content,
            util_classes.PLUGIN_CONFIG_SCHEMA, ValidationMode.ERROR)
        validator.validate()

        mock_import_plugin.assert_called()

    @staticmethod
    @pytest.mark.parametrize('src_dir', [None])
    def test_plugin_missing_field(plugin_config_file, plugin_config_content):
        with pytest.raises(exceptions.SchemaValidationError) as err_info:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                util_classes.PLUGIN_CONFIG_SCHEMA, ValidationMode.ERROR)
            validator.validate()
        message = err_info.value.message
        assert "'srcDir' is a required property" in message

    @staticmethod
    @mock.patch('os.path.isabs', return_value=False)
    @mock.patch.object(PluginValidator,
                       '_PluginValidator__import_plugin',
                       return_value=({}, None))
    @pytest.mark.parametrize('version,expected',
                             [('xxx', "'xxx' does not match"), ('1.0.0', None),
                              ('1.0.0_HF', None)])
    def test_plugin_version_format(mock_import_plugin, src_dir,
                                   plugin_config_file, plugin_config_content,
                                   expected):

        try:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                util_classes.PLUGIN_CONFIG_SCHEMA, ValidationMode.ERROR)
            validator.validate()
            mock_import_plugin.assert_called()
        except exceptions.SchemaValidationError as err_info:
            message = err_info.message
            assert expected in message

    @staticmethod
    @mock.patch('os.path.isabs', return_value=False)
    @mock.patch.object(PluginValidator,
                       '_PluginValidator__import_plugin',
                       return_value=({}, None))
    @pytest.mark.parametrize(
        'entry_point,expected',
        [('staged_plugin', "'staged_plugin' does not match"),
         (':staged_plugin', "':staged_plugin' does not match"),
         ('staged:', "'staged:' does not match"),
         ('staged_plugin::staged', "'staged_plugin::staged' does not match"),
         (':staged_plugin:staged:', "':staged_plugin:staged:' does not match"),
         ('staged_plugin:staged', None)])
    def test_plugin_entry_point(mock_import_plugin, src_dir,
                                plugin_config_file, plugin_config_content,
                                expected):
        try:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                util_classes.PLUGIN_CONFIG_SCHEMA, ValidationMode.ERROR)
            validator.validate()
            mock_import_plugin.assert_called()
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
                util_classes.PLUGIN_CONFIG_SCHEMA, ValidationMode.ERROR)
            validator.validate()
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
                util_classes.PLUGIN_CONFIG_SCHEMA, ValidationMode.ERROR)
            validator.validate()
        message = err_info.value.message
        assert "'srcDir' is a required property" in message
        assert "'xxx' is not one of ['UNIX', 'WINDOWS']" in message

    @staticmethod
    @mock.patch('os.path.isabs', return_value=False)
    @mock.patch.object(PluginValidator,
                       '_PluginValidator__import_plugin',
                       return_value=({}, None))
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
                util_classes.PLUGIN_CONFIG_SCHEMA, ValidationMode.ERROR)
            validator.validate()
            mock_import_plugin.assert_called()
        except exceptions.SchemaValidationError as err_info:
            message = err_info.message
            assert expected in message

    @staticmethod
    @pytest.mark.parametrize('validation_mode',
                             [ValidationMode.INFO, ValidationMode.WARNING])
    def test_plugin_info_warn_mode(plugin_config_file, plugin_config_content,
                                   validation_mode):
        err_info = None
        try:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                util_classes.PLUGIN_CONFIG_SCHEMA, validation_mode)
            validator.validate()
        except Exception as e:
            err_info = e

        assert err_info is None

    @staticmethod
    @pytest.mark.parametrize('entry_point,plugin_type',
                             [('successful:staged', 'STAGED'),
                              ('successful:direct', 'DIRECT')])
    @mock.patch('dlpx.virtualization._internal.file_util.get_src_dir_path')
    def test_successful_validation(mock_file_util, plugin_config_file,
                                   fake_src_dir):
        mock_file_util.return_value = fake_src_dir

        validator = PluginValidator(plugin_config_file,
                                    util_classes.PLUGIN_CONFIG_SCHEMA,
                                    ValidationMode.ERROR, True)
        validator.validate()

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
            validator = PluginValidator(plugin_config_file,
                                        util_classes.PLUGIN_CONFIG_SCHEMA,
                                        ValidationMode.ERROR, True)
            validator.validate()

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
            validator = PluginValidator(plugin_config_file,
                                        util_classes.PLUGIN_CONFIG_SCHEMA,
                                        ValidationMode.ERROR, True)
            validator.validate()

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
            validator = PluginValidator(plugin_config_file,
                                        util_classes.PLUGIN_CONFIG_SCHEMA,
                                        ValidationMode.ERROR, True)
            validator.validate()

        message = err_info.value.message
        assert expected_error in message
        assert '0 Warning(s). 1 Error(s).' in message

    @staticmethod
    @pytest.mark.parametrize('entry_point', ['arbitrary_error:plugin'])
    @mock.patch('dlpx.virtualization._internal.file_util.get_src_dir_path')
    def test_sdk_error(mock_file_util, plugin_config_file, fake_src_dir):
        mock_file_util.return_value = fake_src_dir

        with pytest.raises(exceptions.SDKToolingError) as err_info:
            validator = PluginValidator(plugin_config_file,
                                        util_classes.PLUGIN_CONFIG_SCHEMA,
                                        ValidationMode.ERROR, True)
            validator.validate()

        message = err_info.value.message
        assert ('SDK Error: Got an arbitrary non-platforms error for testing.'
                in message)
        assert '0 Warning(s). 1 Error(s).' in message
