#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import json

import mock
import pytest
import yaml

from dlpx.virtualization._internal import exceptions
from dlpx.virtualization._internal.commands import compile


class TestCompile:
    @staticmethod
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_compile_success(mock_generate_python, plugin_config_file,
                             codegen_gen_py_inputs):

        gen_py = codegen_gen_py_inputs
        compile.compile(plugin_config_file)

        mock_generate_python.assert_called_once_with(
            gen_py.name, gen_py.source_dir, gen_py.plugin_content_dir,
            gen_py.schema_dict, compile.GENERATED_MODULE)

    @staticmethod
    @pytest.mark.parametrize('plugin_config_file',
                             ['/not/a/real/file/plugin_config.yml'])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_compile_no_plugin_file(mock_generate_python, plugin_config_file):
        with pytest.raises(exceptions.UserError) as err_info:
            compile.compile(plugin_config_file)

        message = err_info.value.message
        assert message == ("Unable to read plugin config file"
                           " '/not/a/real/file/plugin_config.yml'"
                           "\nError code: 2. Error message: No such file or"
                           " directory")

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('plugin_config_content', [
        '{}\nNOT YAML'.format(
            yaml.dump({'random': 'yaml'}, default_flow_style=False))
    ])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_compile_plugin_bad_format(mock_generate_python,
                                       plugin_config_file):
        with pytest.raises(exceptions.UserError) as err_info:
            compile.compile(plugin_config_file)

        message = err_info.value.message
        assert message == ('Command failed because the plugin config file '
                           'provided as input {!r} was not valid yaml. '
                           'Verify the file contents. '
                           'Error position: 3:9'.format(plugin_config_file))

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('src_dir', [None])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_compile_plugin_missing_fields(mock_generate_python,
                                           plugin_config_file):
        with pytest.raises(exceptions.UserError) as err_info:
            compile.compile(plugin_config_file)

        message = err_info.value.message
        assert message == ("The plugin config file provided is missing some"
                           " required fields. Missing fields are ['srcDir']")

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('language', ['BAD_LANGUAGE'])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_compile_plugin_bad_language(mock_generate_python,
                                         plugin_config_file):
        with pytest.raises(exceptions.UserError) as err_info:
            compile.compile(plugin_config_file)

        message = err_info.value.message
        assert message == ('Invalid language BAD_LANGUAGE found in plugin'
                           ' config file. Please specify PYTHON27 as the'
                           ' language in plugin config file as it is the'
                           ' only supported option now.')

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('src_dir', ['src'])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_compile_plugin_src_dir_not_abs(mock_generate_python,
                                            plugin_config_file):
        with pytest.raises(exceptions.UserError) as err_info:
            compile.compile(plugin_config_file)

        message = err_info.value.message
        assert message == ("The path 'src' found in the plugin config file"
                           " was not absolute. Change the path to be absolute"
                           " and run the command again.")

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('schema_file', ['schema.json'])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_compile_plugin_schema_file_not_abs(mock_generate_python,
                                                plugin_config_file):
        with pytest.raises(exceptions.UserError) as err_info:
            compile.compile(plugin_config_file)

        message = err_info.value.message
        assert message == ("The path 'schema.json' found in the plugin config"
                           " file was not absolute. Change the path to be"
                           " absolute and run the command again.")

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('schema_file', ['/not/a/real/file/schema.json'])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_compile_no_schema_file(mock_generate_python, plugin_config_file):
        with pytest.raises(exceptions.UserError) as err_info:
            compile.compile(plugin_config_file)

        message = err_info.value.message
        assert message == (
            "Unable to load schemas from '/not/a/real/file/schema.json'"
            " Error code: 2. Error message: No such file or directory")

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize(
        'schema_content',
        ['{}\nNOT JSON'.format(json.dumps({'random': 'json'}))])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_compile_schema_bad_format(mock_generate_python,
                                       plugin_config_file, schema_file):
        with pytest.raises(exceptions.UserError) as err_info:
            compile.compile(plugin_config_file)

        message = err_info.value.message
        assert message == (
            'Failed to load schemas because {!r} is not a valid json file.'
            ' Error: Extra data: line 2 column 1 - line 2 column 9'
            ' (char 19 - 27)'.format(schema_file))

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('virtual_source_definition', [None])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_compile_plugin_missing_schema_def(mock_generate_python,
                                               plugin_config_file):
        with pytest.raises(exceptions.UserError) as err_info:
            compile.compile(plugin_config_file)

        message = err_info.value.message
        assert message == ("The schemas file provided is missing some"
                           " required schemas. Missing schema definitions are"
                           " ['virtualSourceDefinition']")

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('source_config_definition',
                             [{
                                 'type': 'object',
                                 'required': ['name', 'path'],
                                 'additionalProperties': False,
                                 'properties': {
                                     'name': {
                                         'type': 'string'
                                     },
                                     'path': {
                                         'type': 'string'
                                     }
                                 },
                                 'nameField': 'name'
                             }])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_compile_plugin_source_config_def_missing_field(
            mock_generate_python, plugin_config_file):
        with pytest.raises(exceptions.UserError) as err_info:
            compile.compile(plugin_config_file)

        message = err_info.value.message
        assert message == ("The provided schema for sourceConfigDefinition is"
                           " missing required fields. Verify that the"
                           " field(s) ['identityFields'] are there.")

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('repository_definition',
                             [{
                                 'type': 'object',
                                 'properties': {
                                     'name': {
                                         'type': 'string'
                                     }
                                 },
                                 'identityFields': ['name']
                             }])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_compile_plugin_repository_def_missing_field(
            mock_generate_python, plugin_config_file):
        with pytest.raises(exceptions.UserError) as err_info:
            compile.compile(plugin_config_file)

        message = err_info.value.message
        assert message == ("The provided schema for repositoryDefinition is"
                           " missing required fields. Verify that the"
                           " field(s) ['nameField'] are there.")

        assert not mock_generate_python.called
