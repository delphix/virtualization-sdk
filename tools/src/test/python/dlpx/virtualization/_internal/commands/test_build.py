#
# Copyright (c) 2019, 2020 by Delphix. All rights reserved.
#

import json
import os

import yaml
from dlpx.virtualization._internal import const, exceptions
from dlpx.virtualization._internal.commands import build
from dlpx.virtualization._internal.commands import initialize as init
from dlpx.virtualization._internal.plugin_importer import PluginImporter

import mock
import pytest


@pytest.fixture
def artifact_file_created():
    #
    # For all build tests since we're creating the file, it should not be
    # created via the fixtures.
    #
    return False


class TestBuild:
    @staticmethod
    @mock.patch(
        'dlpx.virtualization._internal.commands.build.patch_dependencies')
    @mock.patch(
        'dlpx.virtualization._internal.plugin_util.get_plugin_manifest',
        return_value={})
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    @mock.patch(
        'dlpx.virtualization._internal.plugin_dependency_util.install_deps')
    @mock.patch('os.path.isabs', return_value=False)
    def test_build_success(mock_relative_path, mock_install_deps,
                           mock_generate_python, mock_plugin_manifest,
                           mock_patch_dependencies,
                           plugin_config_file, artifact_file, artifact_content,
                           codegen_gen_py_inputs):
        gen_py = codegen_gen_py_inputs

        # Before running build assert that the artifact file does not exist.
        assert not os.path.exists(artifact_file)

        build.build(plugin_config_file, artifact_file, False, False)

        mock_generate_python.assert_called_once_with(gen_py.name,
                                                     gen_py.source_dir,
                                                     gen_py.plugin_content_dir,
                                                     gen_py.schema_dict)
        mock_plugin_manifest.assert_called()
        mock_install_deps.assert_called()
        mock_relative_path.assert_called()
        mock_patch_dependencies.assert_called()

        # After running build this file should now exist.
        assert os.path.exists(artifact_file)

        with open(artifact_file, 'rb') as f:
            content = json.load(f)

        assert content == artifact_content

    @staticmethod
    @mock.patch(
        'dlpx.virtualization._internal.plugin_util.get_plugin_manifest',
        return_value={})
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    @mock.patch(
        'dlpx.virtualization._internal.plugin_dependency_util.install_deps')
    @mock.patch('os.path.isabs', return_value=False)
    def test_build_success_with_patched_dependencies(
            mock_relative_path, mock_install_deps,
            mock_generate_python, mock_plugin_manifest,
            plugin_config_file, artifact_file, codegen_gen_py_inputs,
            json_format_file_patched, json_format_content):

        build.build(plugin_config_file, artifact_file, False, False)

        with open(json_format_file_patched, 'r') as f:
            json_format_text = f.read()

        assert json_format_text == json_format_content

    @staticmethod
    @pytest.mark.parametrize('ingestion_strategy',
                             [const.DIRECT_TYPE, const.STAGED_TYPE])
    @pytest.mark.parametrize('host_type',
                             [const.UNIX_HOST_TYPE, const.WINDOWS_HOST_TYPE])
    @mock.patch(
        'dlpx.virtualization._internal.commands.build.patch_dependencies')
    @mock.patch(
        'dlpx.virtualization._internal.plugin_dependency_util.install_deps')
    @mock.patch('os.path.isabs', return_value=False)
    def test_build_success_from_init(mock_relative_path, mock_install_deps,
                                     mock_patch_dependencies,
                                     tmpdir, ingestion_strategy, host_type,
                                     plugin_name, artifact_file):
        # Initialize an empty directory.
        init.init(tmpdir.strpath, ingestion_strategy, plugin_name, host_type)
        plugin_config_file = os.path.join(
            tmpdir.strpath, init.DEFAULT_PLUGIN_CONFIG_FILE)
        # Before running build assert that the artifact file does not exist.
        assert not os.path.exists(artifact_file)

        build.build(plugin_config_file, artifact_file, False, False)

        mock_relative_path.assert_called()
        mock_install_deps.assert_called()

        assert os.path.exists(artifact_file)

    @staticmethod
    @pytest.mark.parametrize('artifact_filename', ['somefile.json'])
    @mock.patch(
        'dlpx.virtualization._internal.commands.build.patch_dependencies')
    @mock.patch.object(PluginImporter,
                       '_PluginImporter__internal_import',
                       return_value=({}, None))
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    @mock.patch(
        'dlpx.virtualization._internal.plugin_dependency_util.install_deps')
    @mock.patch('os.path.isabs', return_value=False)
    def test_build_success_non_default_output_file(
            mock_relative_path, mock_install_deps, mock_generate_python,
            mock_import_plugin, mock_patch_dependencies,
            plugin_config_file, artifact_file,
            artifact_content, codegen_gen_py_inputs):
        gen_py = codegen_gen_py_inputs

        # Before running build assert that the artifact file does not exist.
        assert not os.path.exists(artifact_file)

        build.build(plugin_config_file, artifact_file, False, False)

        mock_generate_python.assert_called_once_with(gen_py.name,
                                                     gen_py.source_dir,
                                                     gen_py.plugin_content_dir,
                                                     gen_py.schema_dict)
        mock_import_plugin.assert_called()

        # After running build this file should now exist.
        assert os.path.exists(artifact_file)

        with open(artifact_file, 'rb') as f:
            content = json.load(f)

        assert content == artifact_content

    @staticmethod
    @mock.patch(
        'dlpx.virtualization._internal.plugin_util.get_plugin_manifest',
        return_value={})
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    @mock.patch(
        'dlpx.virtualization._internal.plugin_dependency_util.install_deps')
    @mock.patch('os.path.isabs', return_value=False)
    def test_build_codegen_fail(mock_relative_path, mock_install_deps,
                                mock_generate_python, mock_plugin_manifest,
                                plugin_config_file, artifact_file,
                                codegen_gen_py_inputs):
        gen_py = codegen_gen_py_inputs

        # Before running build assert that the artifact file does not exist.
        assert not os.path.exists(artifact_file)

        # Raise UserError when codegen is called
        mock_generate_python.side_effect =\
            exceptions.UserError("codegen_error")

        with pytest.raises(exceptions.BuildFailedError) as err_info:
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message

        mock_generate_python.assert_called_once_with(gen_py.name,
                                                     gen_py.source_dir,
                                                     gen_py.plugin_content_dir,
                                                     gen_py.schema_dict)

        # After running build this file should not exist.
        assert not os.path.exists(artifact_file)
        assert not mock_plugin_manifest.called
        assert "codegen_error" in message
        assert "BUILD FAILED" in message

    @staticmethod
    @mock.patch(
        'dlpx.virtualization._internal.plugin_util.get_plugin_manifest',
        return_value={})
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    @mock.patch(
        'dlpx.virtualization._internal.plugin_dependency_util.install_deps')
    @mock.patch('os.path.isabs', return_value=False)
    def test_build_manifest_fail(mock_relative_path, mock_install_deps,
                                 mock_generate_python, mock_plugin_manifest,
                                 plugin_config_file, artifact_file,
                                 codegen_gen_py_inputs):
        gen_py = codegen_gen_py_inputs

        # Before running build assert that the artifact file does not exist.
        assert not os.path.exists(artifact_file)

        # Raise UserError when codegen is called
        mock_plugin_manifest.side_effect =\
            exceptions.UserError("manifest_error")

        with pytest.raises(exceptions.BuildFailedError) as err_info:
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message

        mock_generate_python.assert_called_once_with(gen_py.name,
                                                     gen_py.source_dir,
                                                     gen_py.plugin_content_dir,
                                                     gen_py.schema_dict)
        mock_plugin_manifest.assert_called()

        # After running build this file should not exist.
        assert not os.path.exists(artifact_file)
        assert "manifest_error" in message
        assert "BUILD FAILED" in message

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.build'
                '.prepare_upload_artifact')
    @mock.patch(
        'dlpx.virtualization._internal.commands.build.patch_dependencies')
    @mock.patch(
        'dlpx.virtualization._internal.plugin_util.get_plugin_manifest',
        return_value={})
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    @mock.patch(
        'dlpx.virtualization._internal.plugin_dependency_util.install_deps')
    @mock.patch('os.path.isabs', return_value=False)
    def test_build_prepare_artifact_fail(mock_relative_path, mock_install_deps,
                                         mock_generate_python,
                                         mock_plugin_manifest,
                                         mock_patch_dependencies,
                                         mock_prep_artifact,
                                         plugin_config_file, artifact_file,
                                         codegen_gen_py_inputs):
        gen_py = codegen_gen_py_inputs

        # Before running build assert that the artifact file does not exist.
        assert not os.path.exists(artifact_file)

        # Raise UserError when codegen is called
        mock_prep_artifact.side_effect =\
            exceptions.UserError("prepare_artifact_error")

        with pytest.raises(exceptions.BuildFailedError) as err_info:
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message

        mock_generate_python.assert_called_once_with(gen_py.name,
                                                     gen_py.source_dir,
                                                     gen_py.plugin_content_dir,
                                                     gen_py.schema_dict)
        mock_plugin_manifest.assert_called()
        mock_prep_artifact.assert_called()

        # After running build this file should not exist.
        assert not os.path.exists(artifact_file)
        assert "prepare_artifact_error" in message
        assert "BUILD FAILED" in message

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.build'
                '.generate_upload_artifact')
    @mock.patch(
        'dlpx.virtualization._internal.commands.build.patch_dependencies')
    @mock.patch(
        'dlpx.virtualization._internal.plugin_util.get_plugin_manifest',
        return_value={})
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    @mock.patch(
        'dlpx.virtualization._internal.plugin_dependency_util.install_deps')
    @mock.patch('os.path.isabs', return_value=False)
    def test_build_generate_artifact_fail(
            mock_relative_path, mock_install_deps, mock_generate_python,
            mock_plugin_manifest, mock_patch_dependencies,
            mock_gen_artifact, plugin_config_file,
            artifact_file, codegen_gen_py_inputs):
        gen_py = codegen_gen_py_inputs

        # Before running build assert that the artifact file does not exist.
        assert not os.path.exists(artifact_file)

        # Raise UserError when codegen is called
        mock_gen_artifact.side_effect =\
            exceptions.UserError("generate_artifact_error")

        with pytest.raises(exceptions.BuildFailedError) as err_info:
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message

        mock_generate_python.assert_called_once_with(gen_py.name,
                                                     gen_py.source_dir,
                                                     gen_py.plugin_content_dir,
                                                     gen_py.schema_dict)
        mock_plugin_manifest.assert_called()
        mock_gen_artifact.assert_called()

        # After running build this file should not exist.
        assert not os.path.exists(artifact_file)
        assert "generate_artifact_error" in message
        assert "BUILD FAILED" in message

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.build'
                '.prepare_upload_artifact')
    @mock.patch(
        'dlpx.virtualization._internal.commands.build.patch_dependencies')
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    @mock.patch(
        'dlpx.virtualization._internal.plugin_dependency_util.install_deps')
    @mock.patch('os.path.isabs', return_value=False)
    def test_generate_only_success(mock_relative_path, mock_install_deps,
                                   mock_generate_python, mock_patch_dependencies,
                                   mock_prep_artifact,
                                   plugin_config_file, artifact_file,
                                   codegen_gen_py_inputs):
        gen_py = codegen_gen_py_inputs
        build.build(plugin_config_file, artifact_file, True, False)

        mock_generate_python.assert_called_once_with(gen_py.name,
                                                     gen_py.source_dir,
                                                     gen_py.plugin_content_dir,
                                                     gen_py.schema_dict)

        assert not mock_prep_artifact.called

    @staticmethod
    @pytest.mark.parametrize('plugin_type', ['DIRECT', 'STAGED'])
    def test_get_linked_source_definition_type_direct(plugin_config_content,
                                                      linked_source_def_type):
        link_type = build.get_linked_source_definition_type(
            plugin_config_content)
        assert link_type == linked_source_def_type

    @staticmethod
    def test_prepare_discovery_definition(plugin_config_content,
                                          schema_content,
                                          discovery_definition):
        actual_discovery_definition = build.prepare_discovery_definition(
            plugin_config_content, schema_content)
        assert actual_discovery_definition == discovery_definition

    @staticmethod
    def test_prepare_upload_artifact_success(artifact_content,
                                             plugin_config_content, src_dir,
                                             schema_content):
        upload_artifact = build.prepare_upload_artifact(
            plugin_config_content, src_dir, schema_content, {})

        assert upload_artifact == artifact_content

    @staticmethod
    def test_generate_upload_artifact_success(tmpdir, artifact_content):
        output_file = tmpdir.join('artifact.json')
        build.generate_upload_artifact(output_file.strpath, artifact_content)
        assert json.load(output_file) == artifact_content

    @staticmethod
    @pytest.mark.parametrize('artifact_file', ['/not/a/valid/file'])
    def test_generate_upload_artifact_fail(artifact_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.generate_upload_artifact(artifact_file, 'somestuff')
        message = err_info.value.message
        assert message == ('Failed to write upload_artifact file '
                           'to /not/a/valid/file. Error code: 2. '
                           'Error message: No such file or directory')

    @staticmethod
    @pytest.mark.parametrize('src_dir', ['/not/a/valid/directory'])
    def test_zip_and_encode_source_files_invalid_dir(src_dir):
        with pytest.raises(exceptions.UserError) as err_info:
            build.zip_and_encode_source_files(src_dir)
        message = err_info.value.message
        assert message == ('Failed to read source code directory'
                           ' /not/a/valid/directory. Error code: 2.'
                           ' Error message: No such file or directory')

    @staticmethod
    @mock.patch('compileall.compile_dir')
    def test_zip_and_encode_source_files_compileall_fail(
            mock_compile, src_dir):
        mock_compile.return_value = 0
        with pytest.raises(exceptions.UserError) as err_info:
            build.zip_and_encode_source_files(src_dir)
        message = err_info.value.message
        assert message == ('Failed to compile source code in the directory'
                           ' {}.'.format(src_dir))

    @staticmethod
    @mock.patch('base64.b64encode')
    def test_zip_and_encode_source_files_encode_fail(mock_encode, src_dir):
        mock_encode.side_effect = UnicodeError()
        mock_encode.side_effect.reason = 'something'
        with pytest.raises(exceptions.UserError) as err_info:
            build.zip_and_encode_source_files(src_dir)
        message = err_info.value.message
        assert message == ('Failed to base64 encode source code in the'
                           ' directory {}. Error message: {}'
                           ''.format(src_dir, 'something'))

    @staticmethod
    @mock.patch.object(PluginImporter,
                       '_PluginImporter__internal_import',
                       return_value=({}, None))
    @mock.patch(
        'dlpx.virtualization._internal.commands.build.patch_dependencies')
    @mock.patch(
        'dlpx.virtualization._internal.plugin_dependency_util.install_deps')
    @mock.patch('os.path.isabs', return_value=False)
    @pytest.mark.parametrize('plugin_id',
                             ['77f18ce4-4425-4cd6-b9a7-23653254d660'])
    def test_id_validation_positive(mock_relative_path, mock_install_deps,
                                    mock_patch_dependencies,
                                    mock_import_plugin, plugin_config_file,
                                    artifact_file):
        build.build(plugin_config_file, artifact_file, False)

    @staticmethod
    @mock.patch.object(PluginImporter,
                       '_PluginImporter__internal_import',
                       return_value=({}, None))
    @pytest.mark.parametrize('plugin_id', ['mongo'])
    def test_id_validation_negative(mock_import_plugin, plugin_config_file,
                                    artifact_file):
        with pytest.raises(exceptions.UserError):
            build.build(plugin_config_file, artifact_file, False, False)


class TestPluginUtil:
    @staticmethod
    @pytest.mark.parametrize('plugin_config_file',
                             ['/not/a/real/file/plugin_config.yml'])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_no_plugin_file(mock_generate_python, plugin_config_file,
                            artifact_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message
        assert ("Unable to read plugin config file"
                " '/not/a/real/file/plugin_config.yml'"
                "\nError code: 2. Error message: No such file or"
                " directory") in message

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
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message
        assert ('Command failed because the plugin config file '
                'provided as input \'{}\' was not valid yaml. '
                'Verify the file contents. '
                'Error position: 3:9'.format(plugin_config_file)) in message

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('src_dir', [None])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_plugin_missing_fields(mock_generate_python, plugin_config_file,
                                   artifact_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message
        assert "'srcDir' is a required property" in message

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('language', ['BAD_LANGUAGE'])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_plugin_bad_language(mock_generate_python, plugin_config_file,
                                 artifact_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message
        assert "'BAD_LANGUAGE' is not one of ['PYTHON27']" in message

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('src_dir', [os.path.join('fake', 'dir')])
    @mock.patch('os.path.isabs', return_value=False)
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_plugin_no_src_dir(mock_generate_python, mock_path_is_relative,
                               plugin_config_file, artifact_file, tmpdir):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message
        assert message == "The path '{}' does not exist.".format(
            tmpdir.join(os.path.join('fake', 'dir')).strpath)

        assert not mock_generate_python.called

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_plugin_schema_not_file(mock_generate_python, plugin_config_file,
                                    artifact_file, schema_file):
        # Delete the schema file and create a dir there instead
        os.remove(schema_file)
        os.mkdir(schema_file)
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message
        assert message == "The path '{}' should be a file but is not.".format(
            schema_file)

        assert not mock_generate_python.called

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    @mock.patch('os.path.isabs', return_value=False)
    def test_plugin_src_not_dir(mock_relative_path, mock_generate_python,
                                plugin_config_file, artifact_file, src_dir):
        # Delete the src dir folder and create a file there instead
        os.rmdir(src_dir)
        with open(src_dir, 'w') as f:
            f.write('writing to create file')
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message
        assert message == ("The path '{}' should be a"
                           " directory but is not.".format(src_dir))

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('schema_file', ['/not/a/real/file/schema.json'])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_no_schema_file(mock_generate_python, plugin_config_file,
                            artifact_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False, False)

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
        if os.name == 'nt':
            pytest.skip(
                'skipping this test on windows as os.chmod has issues removing'
                ' permissions on file')
            #
            # The schema_file can be made unreadable on windows using pypiwin32 but
            # since it adds dependency on pypiwin32 for the sdk, skipping this test
            # instead of potentially destabilizing the sdk by adding this dependency.
            #
        else:
            os.chmod(schema_file, 0000)
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message
        assert (
            'Unable to load schemas from \'{}\'\nError code: 13.'
            ' Error message: Permission denied'.format(schema_file)) in message

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize(
        'schema_content',
        ['{}\nNOT JSON'.format(json.dumps({'random': 'json'}))])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_schema_bad_format(mock_generate_python, plugin_config_file,
                               artifact_file, schema_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message
        assert (
            'Failed to load schemas because \'{}\' is not a valid json file.'
            ' Error: Extra data: line 2 column 1 - line 2 column 9'
            ' (char 19 - 27)'.format(schema_file)) in message

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('virtual_source_definition', [None])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_plugin_missing_schema_def(mock_generate_python,
                                       plugin_config_file, artifact_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message
        assert "'virtualSourceDefinition' is a required property" in message

        assert not mock_generate_python.called

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    @pytest.mark.parametrize('additional_definition', [{
        'type': 'objectxxx',
        'additionalProperties': False,
        'properties': {}
    }])
    def test_plugin_extra_schema_def(mock_generate_python, plugin_config_file,
                                     artifact_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message
        assert "Additional properties are not allowed " \
               "('additionalDefinition' was unexpected)" in message

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
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message
        assert "'identityFields' is a required property" in message

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
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message
        assert "'nameField' is a required property" in message

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('manual_discovery, expected', [
        pytest.param(True, True),
        pytest.param(False, False),
        pytest.param(None, True)
    ])
    def test_manual_discovery_parameter(plugin_config_content, src_dir,
                                        schema_content, expected):

        upload_artifact = build.prepare_upload_artifact(
            plugin_config_content, src_dir, schema_content, {})

        assert expected == upload_artifact['discoveryDefinition'][
            'manualSourceConfigDiscovery']

    @staticmethod
    @pytest.mark.parametrize('build_number, expected', [
        pytest.param('0.0.1', '0.0.1'),
        pytest.param('0.1.0', '0.1'),
        pytest.param('1.0.01.0', '1.0.1')
    ])
    def test_build_number_parameter(plugin_config_content, src_dir,
                                    schema_content, expected):

        upload_artifact = build.prepare_upload_artifact(
            plugin_config_content, src_dir, schema_content, {})

        assert expected == upload_artifact['buildNumber']

    @staticmethod
    @pytest.mark.parametrize('extended_start_stop_hooks, expected', [
        pytest.param(True, True),
        pytest.param(False, False),
        pytest.param(None, False),
    ])
    def test_extended_hooks_parameter(plugin_config_content, src_dir,
                                      schema_content, expected):
        upload_artifact = build.prepare_upload_artifact(
            plugin_config_content, src_dir, schema_content, {})
        assert expected == upload_artifact.get('extendedStartStopHooks')

    @staticmethod
    @pytest.mark.parametrize('lua_name, expected', [
        pytest.param('lua-toolkit-1', 'lua-toolkit-1'),
        pytest.param('nix_staged_python', 'nix_staged_python')
    ])
    def test_lua_name_parameter(plugin_config_content, src_dir, schema_content,
                                expected):
        upload_artifact = build.prepare_upload_artifact(
            plugin_config_content, src_dir, schema_content, {})
        assert expected == upload_artifact.get('luaName')

    @staticmethod
    @pytest.mark.parametrize(
        'minimum_lua_version, expected',
        [pytest.param('2.3', '2.3'),
         pytest.param('2.4', '2.4')])
    def test_minimum_lua_version_parameter(plugin_config_content, src_dir,
                                           schema_content, expected):
        upload_artifact = build.prepare_upload_artifact(
            plugin_config_content, src_dir, schema_content, {})
        assert expected == upload_artifact.get('minimumLuaVersion')

    @staticmethod
    @pytest.mark.parametrize('build_number', ['1.0.1'])
    def test_build_change_and_build_again(plugin_config_content, src_dir,
                                          schema_content):
        upload_artifact = build.prepare_upload_artifact(
            plugin_config_content, src_dir, schema_content, {})
        assert plugin_config_content['buildNumber'] == upload_artifact['buildNumber']
        changed_build_number = '7.2.12'
        changed_host_type = ['WINDOWS']
        plugin_config_content['buildNumber'] = changed_build_number
        plugin_config_content['hostTypes'] = changed_host_type
        upload_artifact_2 = build.prepare_upload_artifact(
            plugin_config_content, src_dir, schema_content, {})
        assert changed_build_number == upload_artifact_2.get('buildNumber')
        assert changed_host_type == upload_artifact_2.get('hostTypes')

    @staticmethod
    @pytest.mark.parametrize('repository_definition',
                             [{
                                 'type': 'object',
                                 'properties': {
                                     'name': {
                                         'type': 'badDataType'
                                     }
                                 },
                                 'nameField': 'name',
                                 'identityFields': ['name']
                             }])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_bad_data_type_in_schema(mock_generate_python,
                                     plugin_config_file,
                                     artifact_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message
        exp_error = "'badDataType' is not valid under any of the given schemas"
        assert exp_error in message

        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('host_types', [''])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_empty_host_type(mock_generate_python, plugin_config_file,
                             artifact_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message
        assert "Validation failed" in message
        assert not mock_generate_python.called

    @staticmethod
    @pytest.mark.parametrize('plugin_name', [''])
    @mock.patch('dlpx.virtualization._internal.codegen.generate_python')
    def test_empty_plugin_name(mock_generate_python, plugin_config_file,
                               artifact_file):
        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message
        assert "Validation failed" in message
        assert not mock_generate_python.called

    @staticmethod
    @mock.patch('os.path.isabs', return_value=False)
    def test_non_existing_entry_file(mock_relative_path, plugin_config_file,
                                     plugin_config_content, artifact_file):
        entry_module, _ = plugin_config_content['entryPoint'].split(':')

        with pytest.raises(exceptions.UserError) as err_info:
            build.build(plugin_config_file, artifact_file, False, False)

        message = err_info.value.message
        exp_message = "No module named {module}".format(module=entry_module)
        assert exp_message in message
