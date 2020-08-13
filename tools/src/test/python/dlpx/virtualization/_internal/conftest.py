#
# Copyright (c) 2019, 2020 by Delphix. All rights reserved.
#

import configparser
import copy
import json
import os

import yaml
from dlpx.virtualization._internal import cli, click_util, const, package_util

import pytest

#
# conftest.py is used to share fixtures among multiple tests files. pytest will
# automatically get discovered in the test class if the figure name is used
# as the input variable. The idea of fixtures is to define certain object
# configs and allow them to get used in different tests but also being allowed
# to set certain parts defined in other fixtures. Read more at:
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
    if plugin_config_content:
        f.write(plugin_config_content)
    return f.strpath


@pytest.fixture
def plugin_config_filename():
    return 'plugin_config.yml'


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
def dvp_config_file(tmpdir, dvp_config_properties):
    _write_dvp_config_file(tmpdir, dvp_config_properties=dvp_config_properties)


@pytest.fixture
def dev_config_file(tmpdir, dev_config_properties):
    _write_dvp_config_file(tmpdir, dev_config_properties=dev_config_properties)


@pytest.fixture
def empty_config_file(tmpdir):
    _write_dvp_config_file(tmpdir)


def _write_dvp_config_file(tmpdir,
                           dvp_config_properties=None,
                           dev_config_properties=None):
    dvp_dir = tmpdir.join(click_util.CONFIG_DIR_NAME).strpath
    os.mkdir(dvp_dir)
    dvp_config_filepath = os.path.join(dvp_dir, click_util.CONFIG_FILE_NAME)
    parser = configparser.ConfigParser()
    if dvp_config_properties:
        parser['default'] = dvp_config_properties

    if dev_config_properties:
        parser['dev'] = dev_config_properties

    with open(dvp_config_filepath, 'wb') as config_file:
        parser.write(config_file)

    #
    # Add temp_dir to list of config files the ConfigFileProcessor will
    # check to ensure the fixture is cleaned up after the test completes.
    #
    click_util.ConfigFileProcessor.config_files = []
    click_util.ConfigFileProcessor.config_files.append(dvp_config_filepath)

    #
    # Context settings are initialized before the pytest fixture object
    # is created, so read the config file before the command is invoked
    #
    cli.CONTEXT_SETTINGS['obj'] = {}
    cli.CONTEXT_SETTINGS['obj'] = click_util.ConfigFileProcessor.read_config()

    reload(cli)


@pytest.fixture
def dvp_config_properties():
    return {
        'engine': 'engine.delphix.com',
        'user': 'user',
        'password': 'password'
    }


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
def plugin_config_content(plugin_id, plugin_name, external_version, language,
                          host_types, plugin_type, entry_point, src_dir,
                          schema_file, manual_discovery, build_number,
                          extended_start_stop_hooks, lua_name,
                          minimum_lua_version):
    """
    This fixture creates the dict expected in the properties yaml file the
    customer must provide for the build and compile commands.
    """
    config = {
        'defaultLocale': 'en-us',
        'rootSquashEnabled': True,
    }

    if plugin_id:
        config['id'] = plugin_id

    if plugin_name:
        config['name'] = plugin_name

    if external_version:
        config['externalVersion'] = external_version

    if language:
        config['language'] = language

    if host_types:
        config['hostTypes'] = host_types

    if plugin_type:
        config['pluginType'] = plugin_type

    if entry_point:
        config['entryPoint'] = entry_point

    if src_dir:
        config['srcDir'] = src_dir

    if schema_file:
        config['schemaFile'] = schema_file

    # Here we do an 'is not None' check because we will be passing in
    # booleans as a parameter in tests.
    if manual_discovery is not None:
        config['manualDiscovery'] = manual_discovery

    if build_number:
        config['buildNumber'] = build_number

    if lua_name:
        config['luaName'] = lua_name

    if extended_start_stop_hooks:
        config['extendedStartStopHooks'] = extended_start_stop_hooks

    if minimum_lua_version:
        config['minimumLuaVersion'] = minimum_lua_version

    return config


@pytest.fixture
def plugin_id():
    return '16bef554-9470-11e9-b2e3-8c8590d4a42c'


@pytest.fixture
def plugin_name():
    return 'python_vfiles'


@pytest.fixture
def external_version():
    return '2.0.0'


@pytest.fixture
def language():
    return 'PYTHON27'


@pytest.fixture
def host_types():
    return ['UNIX']


@pytest.fixture
def plugin_type():
    return const.DIRECT_TYPE


@pytest.fixture
def entry_point(entry_point_module, entry_point_object):
    return '{}:{}'.format(entry_point_module, entry_point_object)


@pytest.fixture
def entry_point_module():
    return 'python_vfiles'


@pytest.fixture
def entry_point_object():
    return 'vfiles'


@pytest.fixture
def manual_discovery():
    return None


@pytest.fixture
def build_number():
    return '2.0.0'


@pytest.fixture
def extended_start_stop_hooks():
    return False


@pytest.fixture
def lua_name():
    return 'lua-toolkit-1'


@pytest.fixture
def minimum_lua_version():
    return "2.3"


@pytest.fixture
def artifact_manual_discovery():
    return True


@pytest.fixture
def plugin_module_content(entry_point_object, discovery_operation,
                          linked_operation, virtual_operation,
                          upgrade_operation):
    class Object(object):
        pass

    plugin_object = Object()
    plugin_object.discovery = discovery_operation
    plugin_object.linked = linked_operation
    plugin_object.virtual = virtual_operation
    plugin_object.upgrade = upgrade_operation

    plugin_module = Object()
    setattr(plugin_module, entry_point_object, plugin_object)

    return plugin_module


@pytest.fixture
def discovery_operation():
    class DiscoveryOperations(object):
        pass

    discovery = DiscoveryOperations()

    def repository_discovery(source_connection):
        return None

    def source_config_discovery(source_connection, repository):
        return None

    discovery.repository_impl = repository_discovery
    discovery.source_config_impl = source_config_discovery

    return discovery


@pytest.fixture
def linked_operation():
    class LinkedOperations(object):
        pass

    linked = LinkedOperations()

    def pre_snapshot(direct_source, repository, source_config):
        pass

    def post_snapshot(direct_source, repository, source_config):
        return None

    linked.pre_snapshot_impl = pre_snapshot
    linked.post_snapshot_impl = post_snapshot
    linked.start_staging_impl = None
    linked.stop_staging_impl = None
    linked.status_impl = None
    linked.worker_impl = None
    linked.mount_specification_impl = None

    return linked


@pytest.fixture
def virtual_operation():
    class VirtualOperations(object):
        pass

    virtual = VirtualOperations()

    def configure(virtual_source, repository, snapshot):
        return None

    def reconfigure(virtual_source, repository, source_config, snapshot):
        pass

    def start(virtual_source, repository, source_config):
        pass

    def pre_snapshot(virtual_source, repository, source_config):
        pass

    def post_snapshot(virtual_source, repository, source_config):
        return None

    def mount_specification(virtual_source, repository):
        return None

    virtual.configure_impl = configure
    virtual.unconfigure_impl = None
    virtual.reconfigure_impl = reconfigure
    virtual.start_impl = start
    virtual.stop_impl = None
    virtual.pre_snapshot_impl = pre_snapshot
    virtual.post_snapshot_impl = post_snapshot
    virtual.mount_specification_impl = mount_specification
    virtual.status_impl = None
    virtual.initialize_impl = None

    return virtual


@pytest.fixture
def upgrade_operation():
    class UpgradeOperation(object):
        pass

    upgrade = UpgradeOperation()
    upgrade.migration_id_list = []
    upgrade.repository_id_to_impl = {}
    upgrade.source_config_id_to_impl = {}
    upgrade.linked_source_id_to_impl = {}
    upgrade.virtual_source_id_to_impl = {}
    upgrade.snapshot_id_to_impl = {}

    return upgrade


@pytest.fixture
def plugin_manifest(upgrade_operation):
    manifest = {
        'type': 'PluginManifest',
        'hasRepositoryDiscovery': True,
        'hasSourceConfigDiscovery': True,
        'hasLinkedPreSnapshot': True,
        'hasLinkedPostSnapshot': True,
        'hasLinkedStartStaging': False,
        'hasLinkedStopStaging': False,
        'hasLinkedStatus': False,
        'hasLinkedWorker': False,
        'hasLinkedMountSpecification': False,
        'hasVirtualConfigure': True,
        'hasVirtualUnconfigure': False,
        'hasVirtualReconfigure': True,
        'hasVirtualStart': True,
        'hasVirtualStop': False,
        'hasVirtualPreSnapshot': True,
        'hasVirtualPostSnapshot': True,
        'hasVirtualMountSpecification': True,
        'hasVirtualStatus': False,
        'hasInitialize': False,
        'migrationIdList': upgrade_operation.migration_id_list
    }
    return manifest


@pytest.fixture
def schema_content(repository_definition, source_config_definition,
                   virtual_source_definition, linked_source_definition,
                   snapshot_definition, snapshot_parameters_definition,
                   additional_definition):

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

    if snapshot_parameters_definition:
        schema['snapshotParametersDefinition'] = snapshot_parameters_definition

    if additional_definition:
        schema['additionalDefinition'] = additional_definition

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
        'additionalProperties': True,
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
def linked_source_definition_with_refs():
    return {
        'type': 'object',
        'additionalProperties': True,
        'properties': {
            'path': {
                'type': 'string'
            },
            'credentials': {
                '$ref': 'https://delphix.com/platform/api#credentialsSupplier'
            },
            'credentialsContainer': {
                'type': 'object',
                'properties': {
                    'nestedCredentials': {
                        '$ref': 'https://delphix.com/platform/api#credentialsSupplier'
                    },
                }
            },
            'credentialsArray': {
                'type': 'array',
                'items': [
                    {'$ref': 'https://delphix.com/platform/api#credentialsSupplier'}
                ]
            }
        }
    }


@pytest.fixture
def linked_source_definition_with_opaque_refs():
    return {
        'type': 'object',
        'additionalProperties': True,
        'properties': {
            'path': {
                'type': 'string'
            },
            'credentials': {
                'type': 'object'
            },
            'credentialsContainer': {
                'type': 'object',
                'properties': {
                    'nestedCredentials': {
                        'type': 'object'
                    },
                }
            },
            'credentialsArray': {
                'type': 'array',
                'items': [
                    {'type': 'object'}
                ]
            }
        }
    }


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
def artifact_content(engine_api, virtual_source_definition,
                     linked_source_definition, discovery_definition,
                     snapshot_definition, snapshot_parameters_definition):
    """
    This fixture creates base artifact that was generated from build and
    used in upload. If any fields besides engine_api needs to be changed,
    add fixtures below and add the function name to be part of the input to
    this function.
    """
    artifact = {
        'type': 'Plugin',
        'pluginId': '16bef554-9470-11e9-b2e3-8c8590d4a42c',
        'name': 'python_vfiles',
        'externalVersion': '2.0.0',
        'defaultLocale': 'en-us',
        'language': 'PYTHON27',
        'hostTypes': ['UNIX'],
        'entryPoint': 'python_vfiles:vfiles',
        'buildApi': package_util.get_build_api_version(),
        'sourceCode': 'UEsFBgAAAAAAAAAAAAAAAAAAAAAAAA==',
        'rootSquashEnabled': True,
        'buildNumber': '2',
        'luaName': 'lua-toolkit-1',
        'extendedStartStopHooks': False,
        'minimumLuaVersion': '2.3',
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

    if snapshot_parameters_definition:
        artifact['snapshotParametersDefinition'] = (
            snapshot_parameters_definition)

    if snapshot_parameters_definition:
        artifact['snapshotParametersDefinition'] = {
            'type': 'PluginSnapshotParametersDefinition',
            'schema': snapshot_parameters_definition,
        }

    return artifact


@pytest.fixture
def engine_api():
    return {'type': 'APIVersion', 'major': 1, 'minor': 11, 'micro': 6}


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
