#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import json
import os

import yaml

from dlpx.virtualization._internal import exceptions

EXPECTED_KEYS_IN_PLUGIN_CONFIG = frozenset({
    'name', 'prettyName', 'version', 'hostTypes', 'entryPoint', 'srcDir',
    'schemaFile', 'manualDiscovery', 'pluginType', 'language'
})

EXPECTED_SCHEMAS = frozenset({
    'repositoryDefinition', 'sourceConfigDefinition',
    'virtualSourceDefinition', 'linkedSourceDefinition', 'snapshotDefinition'
})

EXPECTED_FIELDS = frozenset({'identityFields', 'nameField'})

LANGUAGE_DEFAULT = 'PYTHON27'

STAGED_TYPE = 'STAGED'
DIRECT_TYPE = 'DIRECT'


def read_plugin_config_file(plugin_config):
    try:
        with open(plugin_config, 'rb') as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError as err:
                if hasattr(err, 'problem_mark'):
                    mark = err.problem_mark
                    raise exceptions.UserError(
                        'Command failed because the plugin config file '
                        'provided as input {!r} was not valid yaml. '
                        'Verify the file contents. '
                        'Error position: {}:{}'.format(plugin_config,
                                                       mark.line + 1,
                                                       mark.column + 1))
    except IOError as err:
        raise exceptions.UserError(
            'Unable to read plugin config file {!r}'
            '\nError code: {}. Error message: {}'.format(
                plugin_config, err.errno, os.strerror(err.errno)))


def read_schema_file(schema_file):
    try:
        with open(schema_file, 'r') as f:
            try:
                return json.load(f)
            except ValueError as err:
                raise exceptions.UserError(
                    'Failed to load schemas because {!r} is not a '
                    'valid json file. Error: {}'.format(schema_file, str(err)))
    except IOError as err:
        raise exceptions.UserError(
            'Unable to load schemas from {!r}'
            '\nError code: {}. Error message: {}'.format(
                schema_file, err.errno, os.strerror(err.errno)))


def validate_plugin_config_content(plugin_config_content):
    """
    Validates the given plugin configuration is valid.

    The plugin configuration should include:
    name            the plugin name
    prettyName      the plugin's displayed name
    version         the plugin version
    hostTypes       the list of supported hostTypes (UNIX and/or WINDOWS)
    entryPoint      the entry point of the plugin defined by the decorator
    srcDir          the directory that the source code is writen in
    schemaFile:     the file containing defined schemas in the plugin
    manualDiscovery whether or not manual discovery is supported
    pluginType      whether the plugin is DIRECT or STAGED
    language        language of the source code (ex: PYTHON27 for python2.7)

    Args:
        plugin_config_content (dict): A dictionary representing a plugin
          configuration file.
    Raises:
        UserError: If the configuration is not valid.
        PathNotAbsoluteError: If the src and schema paths are not absolute.
    """
    # First validate that all the expected keys are in the plugin config.
    if not all(name in plugin_config_content
               for name in EXPECTED_KEYS_IN_PLUGIN_CONFIG):
        missing_fields = [
            key for key in EXPECTED_KEYS_IN_PLUGIN_CONFIG
            if key not in plugin_config_content
        ]
        raise exceptions.UserError(
            'The plugin config file provided is missing some required fields.'
            ' Missing fields are {}'.format(missing_fields))

    # Then validate that the language was set to the right language
    if plugin_config_content['language'] != LANGUAGE_DEFAULT:
        raise exceptions.UserError(
            'Invalid language {} found in plugin config file. '
            'Please specify {} as the language in plugin config file'
            ' as it is the only supported option now.'.format(
                plugin_config_content['language'], LANGUAGE_DEFAULT))


def get_src_dir_path(plugin_config, src_dir):
    """Get the absolute path if the srcDir provided is relative path and
    validate that srcDir is a valid directory and that it exists.
    """
    if not os.path.isabs(src_dir):
        src_dir = os.path.join(os.path.dirname(plugin_config), src_dir)

    if not os.path.exists(src_dir):
        raise exceptions.PathDoesNotExistError(src_dir)
    if not os.path.isdir(src_dir):
        raise exceptions.PathTypeError(src_dir, 'directory')
    return src_dir


def get_schema_file_path(plugin_config, schema_file):
    """Get the absolute path if schemaFile is a relative path and
     validate that it is a valid file and that it exists.
    """
    if not os.path.isabs(schema_file):
        schema_file = os.path.join(os.path.dirname(plugin_config), schema_file)

    if not os.path.exists(schema_file):
        raise exceptions.PathDoesNotExistError(schema_file)
    if not os.path.isfile(schema_file):
        raise exceptions.PathTypeError(schema_file, 'file')
    return schema_file


def validate_schemas(schemas):
    # First validate that all schemas needed are there.
    if not all(schema in schemas for schema in EXPECTED_SCHEMAS):
        missing_fields = [
            key for key in EXPECTED_SCHEMAS if key not in schemas
        ]
        raise exceptions.UserError(
            'The schemas file provided is missing some required schemas. '
            'Missing schema definitions are {}'.format(missing_fields))

    # Then validate that the expected fields are in the definitions.
    if not all(field in schemas['sourceConfigDefinition']
               for field in EXPECTED_FIELDS):
        missing_fields = [
            key for key in EXPECTED_FIELDS
            if key not in schemas['sourceConfigDefinition']
        ]
        raise exceptions.SchemaMissingRequiredFieldError(
            'sourceConfigDefinition', missing_fields)

    if not all(field in schemas['repositoryDefinition']
               for field in EXPECTED_FIELDS):
        missing_fields = [
            key for key in EXPECTED_FIELDS
            if key not in schemas['repositoryDefinition']
        ]
        raise exceptions.SchemaMissingRequiredFieldError(
            'repositoryDefinition', missing_fields)
