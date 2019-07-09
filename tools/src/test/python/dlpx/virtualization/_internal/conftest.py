#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import copy
import json
import os

import pytest
import yaml
from dlpx.virtualization._internal import package_util, util_classes

#
# conftest.py is used to share fixtures among multiple tests files. pytest will
# automatically get discovered in the test class if the figure name is used
# as the input variable. The idea of fixtures is to define certain object
# configs and allow them to get used in different tests but also being allowed
# to set certain parts definated in other fixtures. Read more at:
# https://docs.pytest.org/en/latest/fixture.html
#


@pytest.fixture
def plugin_config_file(tmpdir, plugin_config_filename, plugin_config_content):
    """
    This fixture creates a tempdir and writes the plugin_config_content to the
    file plugin_config_filename. Then it returns the full path of the file. If
    plugin_config_content is a dict we also want to create the full directory
    structure which includes the schema.json file and the src folder. Also
    it will do a yaml dump. If it's not a dict assume it's just a string and
     write that directly.
    """
    if isinstance(plugin_config_content, dict):
        plugin_config_content = yaml.dump(plugin_config_content,
                                          default_flow_style=False)

    f = tmpdir.join(plugin_config_filename)
    f.write(plugin_config_content)
    return f.strpath


@pytest.fixture
def plugin_config_filename():
    return 'plugin_config.yml'


@pytest.fixture
def fake_staged_plugin_config():
    return os.path.join(os.path.dirname(__file__),
                        'fake_plugin/staged/plugin_config.yml')


@pytest.fixture
def fake_direct_plugin_config():
    return os.path.join(os.path.dirname(__file__),
                        'fake_plugin/direct/plugin_config.yml')


@pytest.fixture
def src_dir(tmpdir, src_dirname):
    """
    This fixture creates a tempdir and makes a directory in it called
    src_dirname.
    """
    path = tmpdir.join(src_dirname).strpath
    os.mkdir(path)
    return path


@pytest.fixture
def src_dirname():
    return 'src'


@pytest.fixture
def schema_file(tmpdir, schema_filename, schema_content):
    """
    This fixture creates a tempdir and writes the schema.json file
    with the schema_content passed in via the fixture. Then it returns the
    path of the file. If artifact_content is a dict it will do a json dump,
    otherwise if it is just a string we'll write that directly.
    """
    if isinstance(schema_content, dict):
        schema_content = json.dumps(schema_content, indent=4)

    f = tmpdir.join(schema_filename)
    f.write(schema_content)
    return f.strpath


@pytest.fixture
def schema_filename():
    return 'schema.json'


@pytest.fixture
def artifact_file(tmpdir, artifact_content, artifact_filename,
                  artifact_file_created):
    """
    This fixture creates a tempdir and writes the artifact_filename file
    with the artifact_content passed in via the fixture. Then it returns the
    path of the file. If artifact_content is a dict it will do a json dump,
    otherwise if it is just a string we'll write that directly.
    """
    f = tmpdir.join(artifact_filename)
    if artifact_file_created:
        # Only write the artifact if we want to actually create it.
        if isinstance(artifact_content, dict):
            artifact_content = json.dumps(artifact_content, indent=4)
        f.write(artifact_content)
    return f.strpath


@pytest.fixture
def artifact_filename():
    return 'artifact.json'


@pytest.fixture
def artifact_file_created():
    return True


@pytest.fixture
def plugin_config_content(plugin_id, plugin_name, src_dir, schema_file,
                          language, manual_discovery, plugin_type):
    """
    This fixutre creates the dict expected in the properties yaml file the
    customer must provide for the build and compile commands.
    """
    config = {
        'version': '2.0.0',
        'hostTypes': ['UNIX'],
        'entryPoint': 'python_vfiles:vfiles',
        'defaultLocale': 'en-us',
        'rootSquashEnabled': True,
    }
    if id:
        config['id'] = plugin_id

    if plugin_name:
        config['name'] = plugin_name

    if plugin_type:
        config['pluginType'] = plugin_type

    if src_dir:
        config['srcDir'] = src_dir

    if schema_file:
        config['schemaFile'] = schema_file

    if language:
        config['language'] = language

    # Here we do is not None check because we will be passing in
    # booleans as a parameter in tests.
    if manual_discovery is not None:
        config['manualDiscovery'] = manual_discovery

    return config


@pytest.fixture
def plugin_entry_point_name():
    return 'vfiles'


@pytest.fixture
def plugin_module_content(plugin_entry_point_name):
    class Object(object):
        pass

    discovery = Object()
    discovery.repository_impl = True
    discovery.source_config_impl = True

    linked = Object()
    linked.pre_snapshot_impl = True
    linked.post_snapshot_impl = True
    linked.start_staging_impl = True
    linked.stop_staging_impl = False
    linked.status_impl = True
    linked.worker_impl = False
    linked.mount_specification_impl = True

    virtual = Object()
    virtual.configure_impl = True
    virtual.unconfigure_impl = False
    virtual.reconfigure_impl = True
    virtual.start_impl = True
    virtual.stop_impl = False
    virtual.pre_snapshot_impl = True
    virtual.post_snapshot_impl = True
    virtual.mount_specification_impl = True
    virtual.status_impl = False
    virtual.initialize_impl = False

    plugin_object = Object()
    plugin_object.discovery = discovery
    plugin_object.linked = linked
    plugin_object.virtual = virtual

    plugin_module = Object()
    setattr(plugin_module, plugin_entry_point_name, plugin_object)

    return plugin_module


@pytest.fixture
def plugin_manifest():
    manifest = {
        'type': 'PluginManifest',
        'hasRepositoryDiscovery': True,
        'hasSourceConfigDiscovery': True,
        'hasLinkedPreSnapshot': True,
        'hasLinkedPostSnapshot': True,
        'hasLinkedStartStaging': True,
        'hasLinkedStopStaging': False,
        'hasLinkedStatus': True,
        'hasLinkedWorker': False,
        'hasLinkedMountSpecification': True,
        'hasVirtualConfigure': True,
        'hasVirtualUnconfigure': False,
        'hasVirtualReconfigure': True,
        'hasVirtualStart': True,
        'hasVirtualStop': False,
        'hasVirtualPreSnapshot': True,
        'hasVirtualPostSnapshot': True,
        'hasVirtualMountSpecification': True,
        'hasVirtualStatus': False,
        'hasInitialize': False
    }
    return manifest


@pytest.fixture
def plugin_id():
    return '16bef554-9470-11e9-b2e3-8c8590d4a42c'


@pytest.fixture
def plugin_name():
    return 'python_vfiles'


@pytest.fixture
def language():
    return 'PYTHON27'


@pytest.fixture
def manual_discovery():
    return None


@pytest.fixture
def artifact_manual_discovery():
    return True


@pytest.fixture
def plugin_type():
    return util_classes.DIRECT_TYPE


@pytest.fixture
def schema_content(repository_definition, source_config_definition,
                   virtual_source_definition, linked_source_definition,
                   snapshot_definition, additional_definition):

    schema = {}

    if repository_definition:
        schema['repositoryDefinition'] = repository_definition

    if source_config_definition:
        schema['sourceConfigDefinition'] = source_config_definition

    if virtual_source_definition:
        schema['virtualSourceDefinition'] = virtual_source_definition

    if linked_source_definition:
        schema['linkedSourceDefinition'] = linked_source_definition

    if snapshot_definition:
        schema['snapshotDefinition'] = snapshot_definition

    if additional_definition:
        schema['additionalDefinition'] = additional_definition

    return schema


@pytest.fixture
def swagger_schema_content(schema_content, snapshot_parameters_definition):

    schema = schema_content
    if snapshot_parameters_definition:
        schema['snapshotParametersDefinition'] = snapshot_parameters_definition

    return schema


@pytest.fixture
def repository_definition():
    return {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string'
            }
        },
        'nameField': 'name',
        'identityFields': ['name']
    }


@pytest.fixture
def source_config_definition():
    return {
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
        'nameField': 'name',
        'identityFields': ['path']
    }


@pytest.fixture
def virtual_source_definition():
    return {
        'type': 'object',
        'additionalProperties': False,
        'properties': {
            'path': {
                'type': 'string'
            }
        }
    }


@pytest.fixture
def linked_source_definition():
    return {'type': 'object', 'additionalProperties': False, 'properties': {}}


@pytest.fixture
def snapshot_definition():
    return {
        'type': 'object',
        'additionalProperties': False,
        'properties': {
            'snapshot_name': {
                'type': 'string'
            }
        }
    }


@pytest.fixture
def snapshot_parameters_definition():
    return {
        'type': 'object',
        'additionalProperties': False,
        'properties': {
            'resync': {
                'type': 'boolean'
            }
        }
    }


@pytest.fixture
def additional_definition():
    return None


@pytest.fixture
def basic_artifact_content(engine_api, virtual_source_definition,
                           linked_source_definition, discovery_definition,
                           snapshot_definition):
    artifact = {
        'type': 'Plugin',
        'name': '16bef554-9470-11e9-b2e3-8c8590d4a42c',
        'prettyName': 'python_vfiles',
        'version': '2.0.0',
        'defaultLocale': 'en-us',
        'language': 'PYTHON27',
        'hostTypes': ['UNIX'],
        'entryPoint': 'python_vfiles:vfiles',
        'buildApi': package_util.get_build_api_version(),
        'engineApi': engine_api,
        'rootSquashEnabled': True,
        'sourceCode': 'UEsFBgAAAAAAAAAAAAAAAAAAAAAAAA==',
        'manifest': {}
    }
    if virtual_source_definition:
        artifact['virtualSourceDefinition'] = {
            'type': 'PluginVirtualSourceDefinition',
            'parameters': virtual_source_definition
        }

    if linked_source_definition:
        artifact['linkedSourceDefinition'] = {
            'type': 'PluginLinkedDirectSourceDefinition',
            'parameters': linked_source_definition
        }

    if discovery_definition:
        artifact['discoveryDefinition'] = discovery_definition

    if snapshot_definition:
        artifact['snapshotSchema'] = snapshot_definition

    return artifact


@pytest.fixture
def artifact_content(engine_api, virtual_source_definition,
                     linked_source_definition, discovery_definition,
                     snapshot_definition):
    """
    This fixture creates base artifact that was generated from build and
    used in upload. If any fields besides engine_api needs to be changed,
    add fixtures below and add the function name to be part of the input to
    this function.
    """
    artifact = {
        'type': 'Plugin',
        'name': '16bef554-9470-11e9-b2e3-8c8590d4a42c',
        'prettyName': 'python_vfiles',
        'version': '2.0.0',
        'defaultLocale': 'en-us',
        'language': 'PYTHON27',
        'hostTypes': ['UNIX'],
        'entryPoint': 'python_vfiles:vfiles',
        'buildApi': package_util.get_build_api_version(),
        'sourceCode': 'UEsFBgAAAAAAAAAAAAAAAAAAAAAAAA==',
        'rootSquashEnabled': True,
        'manifest': {}
    }

    if engine_api:
        artifact['engineApi'] = engine_api

    if virtual_source_definition:
        artifact['virtualSourceDefinition'] = {
            'type': 'PluginVirtualSourceDefinition',
            'parameters': virtual_source_definition,
        }

    if linked_source_definition:
        artifact['linkedSourceDefinition'] = {
            'type': 'PluginLinkedDirectSourceDefinition',
            'parameters': linked_source_definition,
        }

    if discovery_definition:
        artifact['discoveryDefinition'] = discovery_definition

    if snapshot_definition:
        artifact['snapshotSchema'] = snapshot_definition

    return artifact


@pytest.fixture
def engine_api():
    return {'type': 'APIVersion', 'major': 1, 'minor': 10, 'micro': 5}


@pytest.fixture
def discovery_definition(repository_definition, source_config_definition,
                         artifact_manual_discovery):
    discovery_definition = {'type': 'PluginDiscoveryDefinition'}

    if artifact_manual_discovery:
        discovery_definition[
            'manualSourceConfigDiscovery'] = artifact_manual_discovery

    if repository_definition:
        old_repository_def = copy.deepcopy(repository_definition)
        repo_id_fields = old_repository_def.pop('identityFields', None)
        repo_name_field = old_repository_def.pop('nameField', None)

        if repo_id_fields:
            discovery_definition['repositoryIdentityFields'] = repo_id_fields
        if repo_name_field:
            discovery_definition['repositoryNameField'] = repo_name_field
        discovery_definition['repositorySchema'] = old_repository_def

    if source_config_definition:
        old_source_config_def = copy.deepcopy(source_config_definition)
        scf_id_fields = old_source_config_def.pop('identityFields', None)
        scf_name_field = old_source_config_def.pop('nameField', None)

        if scf_id_fields:
            discovery_definition['sourceConfigIdentityFields'] = scf_id_fields
        if scf_name_field:
            discovery_definition['sourceConfigNameField'] = scf_name_field
        discovery_definition['sourceConfigSchema'] = old_source_config_def

    return discovery_definition


@pytest.fixture
def linked_source_def_type(plugin_type):
    if plugin_type == 'DIRECT':
        return 'PluginLinkedDirectSourceDefinition'
    else:
        return 'PluginLinkedStagedSourceDefinition'


@pytest.fixture
def codegen_gen_py_inputs(plugin_config_file, plugin_name, src_dir, tmpdir,
                          schema_content):
    class CodegenInput:
        def __init__(self, name, source_dir, plugin_content_dir, schema_dict):
            self.name = name
            self.source_dir = source_dir
            self.plugin_content_dir = plugin_content_dir
            self.schema_dict = schema_dict

    return CodegenInput(plugin_name, src_dir, tmpdir.strpath, schema_content)
