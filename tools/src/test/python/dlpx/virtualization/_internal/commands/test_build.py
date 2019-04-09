#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import json
import os

import mock
import pytest
import yaml

from dlpx.virtualization._internal import exceptions
from dlpx.virtualization._internal.commands import build


@pytest.fixture
def artifact_file_created():
    #
    # For all build tests since we're creating the file, it should not be
    # created via the fixtures.
    #
    return False


class TestBuild:
    @staticmethod
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_build_success(mock_generate_python, plugin_config_file,
                           artifact_file, artifact_content,
                           codegen_gen_py_inputs):
        gen_py = codegen_gen_py_inputs

        # Before running build assert that the artifact file does not exist.
        assert not os.path.exists(artifact_file)

        build.build(plugin_config_file, artifact_file, False)

        mock_generate_python.assert_called_once_with(gen_py.name,
                                                     gen_py.source_dir,
                                                     gen_py.plugin_content_dir,
                                                     gen_py.schema_dict)

        # After running build this file should now exist.
        assert os.path.exists(artifact_file)

        with open(artifact_file, 'rb') as f:
            content = json.load(f)

        assert content == artifact_content

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.build'
                '.prepare_upload_artifact')
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_generate_only_success(mock_generate_python, mock_prep_artifact,
                                   plugin_config_file, artifact_file,
                                   codegen_gen_py_inputs):
        gen_py = codegen_gen_py_inputs
        build.build(plugin_config_file, artifact_file, True)

        mock_generate_python.assert_called_once_with(gen_py.name,
                                                     gen_py.source_dir,
                                                     gen_py.plugin_content_dir,
                                                     gen_py.schema_dict)

        assert not mock_prep_artifact.called


class TestPluginUtil:
    @staticmethod
    @pytest.mark.parametrize('plugin_config_file',
                             ['/not/a/real/file/plugin_config.yml'])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_no_plugin_file(mock_generate_python, plugin_config_file,
                            artifact_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False)

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
    def test_plugin_bad_format(mock_generate_python, plugin_config_file,
                               artifact_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False)

        message = err_info.value.message
        assert message == ('Command failed because the plugin config file '
                           'provided as input {!r} was not valid yaml. '
                           'Verify the file contents. '
                           'Error position: 3:9'.format(plugin_config_file))

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('src_dir', [None])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_plugin_missing_fields(mock_generate_python, plugin_config_file,
                                   artifact_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False)

        message = err_info.value.message
        assert message == ("The plugin config file provided is missing some"
                           " required fields. Missing fields are ['srcDir']")

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('language', ['BAD_LANGUAGE'])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_plugin_bad_language(mock_generate_python, plugin_config_file,
                                 artifact_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False)

        message = err_info.value.message
        assert message == ('Invalid language BAD_LANGUAGE found in plugin'
                           ' config file. Please specify PYTHON27 as the'
                           ' language in plugin config file as it is the'
                           ' only supported option now.')

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('src_dir', ['/not/a/real/dir/src'])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_plugin_no_src_dir(mock_generate_python, plugin_config_file,
                               artifact_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False)

        message = err_info.value.message
        assert message == "The path '/not/a/real/dir/src' does not exist."

        assert not mock_generate_python.called

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_plugin_schema_not_file(mock_generate_python, plugin_config_file,
                                    artifact_file, schema_file):
        # Delete the schema file and create a dir there instead
        os.remove(schema_file)
        os.mkdir(schema_file)
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False)

        message = err_info.value.message
        assert message == 'The path {!r} should be a file but is not.'.format(
            schema_file)

        assert not mock_generate_python.called

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_plugin_src_not_dir(mock_generate_python, plugin_config_file,
                                artifact_file, src_dir):
        # Delete the src dir folder and create a file there instead
        os.rmdir(src_dir)
        with open(src_dir, 'w') as f:
            f.write('writing to create file')
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False)

        message = err_info.value.message
        assert message == ('The path {!r} should be a'
                           ' directory but is not.'.format(src_dir))

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('schema_file', ['/not/a/real/file/schema.json'])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_no_schema_file(mock_generate_python, plugin_config_file,
                            artifact_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False)

        message = err_info.value.message
        assert message == ("The path '/not/a/real/file/schema.json'"
                           " does not exist.")

        assert not mock_generate_python.called

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_schema_file_bad_permission(mock_generate_python,
                                        plugin_config_file, artifact_file,
                                        schema_file):
        # Make it so we can't read the file
        os.chmod(schema_file, 0000)
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False)

        message = err_info.value.message
        assert message == (
            'Unable to load schemas from {!r}\nError code: 13.'
            ' Error message: Permission denied'.format(schema_file))

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize(
        'schema_content',
        ['{}\nNOT JSON'.format(json.dumps({'random': 'json'}))])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_schema_bad_format(mock_generate_python, plugin_config_file,
                               artifact_file, schema_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False)

        message = err_info.value.message
        assert message == (
            'Failed to load schemas because {!r} is not a valid json file.'
            ' Error: Extra data: line 2 column 1 - line 2 column 9'
            ' (char 19 - 27)'.format(schema_file))

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('virtual_source_definition', [None])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_plugin_missing_schema_def(mock_generate_python,
                                       plugin_config_file, artifact_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False)

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
    def test_plugin_source_config_def_missing_field(mock_generate_python,
                                                    plugin_config_file,
                                                    artifact_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False)

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
    def test_plugin_repository_def_missing_field(mock_generate_python,
                                                 plugin_config_file,
                                                 artifact_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False)

        message = err_info.value.message
        assert message == ("The provided schema for repositoryDefinition is"
                           " missing required fields. Verify that the"
                           " field(s) ['nameField'] are there.")

        assert not mock_generate_python.called
