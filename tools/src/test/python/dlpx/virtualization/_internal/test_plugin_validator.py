#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import os
from collections import OrderedDict

import mock
import pytest

from dlpx.virtualization._internal import exceptions, plugin_util
from dlpx.virtualization._internal.plugin_validator import (PluginValidator,
                                                            ValidationMode)


@pytest.fixture
def plugin_config_file(tmpdir):
    return os.path.join(tmpdir.strpath, 'plugin_config.yml')


@pytest.fixture
def src_dir(tmpdir):
    tmpdir.mkdir('src')
    return os.path.join(tmpdir.strpath, 'src')


@pytest.fixture(scope='session', autouse=True)
def mock_module_import():
    with mock.patch.object(PluginValidator,
                           '_PluginValidator__validate_plugin_entry_point'):
        yield


class TestPluginValidator:
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
    def test_plugin_valid_content(src_dir, plugin_config_file):
        plugin_config_content = OrderedDict([
            ('name', 'staged'.encode('utf-8')),
            ('prettyName', 'StagedPlugin'.encode('utf-8')),
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

    @staticmethod
    def test_plugin_missing_field(plugin_config_file):
        plugin_config_content = OrderedDict([
            ('name', 'staged'.encode('utf-8')),
            ('prettyName', 'StagedPlugin'.encode('utf-8')),
            ('version', '0.1.0'), ('language', 'PYTHON27'),
            ('hostTypes', ['UNIX']), ('pluginType', 'STAGED'.encode('utf-8')),
            ('manualDiscovery', True),
            ('entryPoint', 'staged_plugin:staged'.encode('utf-8')),
            ('schemaFile', 'schema.json'.encode('utf-8'))
        ])

        with pytest.raises(exceptions.UserError) as err_info:
            validator = PluginValidator.from_config_content(
                plugin_config_file, plugin_config_content,
                plugin_util.PLUGIN_CONFIG_SCHEMA, ValidationMode.ERROR)
            validator.validate()
        message = err_info.value.message
        assert "u'srcDir' is a required property" in message

    @staticmethod
    @pytest.mark.parametrize('version, expected', [
        pytest.param('xxx', "u'xxx' does not match"),
        pytest.param('1.0.0', None),
        pytest.param('1.0.0_HF', None)
    ])
    def test_plugin_version_format(src_dir, plugin_config_file, version,
                                   expected):
        plugin_config_content = OrderedDict([
            ('name', 'staged'.encode('utf-8')),
            ('prettyName', 'StagedPlugin'.encode('utf-8')),
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
        except exceptions.UserError as err_info:
            message = err_info.message
            assert expected in message

    @staticmethod
    @pytest.mark.parametrize('entry_point, expected', [
        pytest.param('staged_plugin', "u'staged_plugin' does not match"),
        pytest.param(':staged_plugin', "u':staged_plugin' does not match"),
        pytest.param('staged:', "u'staged:' does not match"),
        pytest.param('staged_plugin::staged',
                     "u'staged_plugin::staged' does not match"),
        pytest.param(':staged_plugin:staged:',
                     "u':staged_plugin:staged:' does not match"),
        pytest.param('staged_plugin:staged', None)
    ])
    def test_plugin_entry_point(src_dir, plugin_config_file, entry_point,
                                expected):
        plugin_config_content = OrderedDict([
            ('name', 'staged'.encode('utf-8')),
            ('prettyName', 'StagedPlugin'.encode('utf-8')),
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
        except exceptions.UserError as err_info:
            message = err_info.message
            assert expected in message
