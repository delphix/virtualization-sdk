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


def read_plugin_config_file(plugin_config):
    try:
        with open(plugin_config, 'rb') as f:
            try:
                return yaml.load(f)
            except yaml.YAMLError, exc:
                if hasattr(exc, 'problem_mark'):
                    mark = exc.problem_mark
                    raise exceptions.UserError(
                        'Command failed because the plugin config file '
                        'provided as input {!r} was not valid yaml. '
                        'Verify the file contents. '
                        'Error position: {}:{}'.format(
                            plugin_config, mark.line + 1, mark.column + 1))
    except IOError as err:
        raise exceptions.UserError(
            'Unable to read config file {!r}'
            '\nError code: {}. Error message: {}'.format(
                plugin_config, err.errno, os.strerror(err.errno)))


def read_schema_file(schema_file):
    try:
        with open(schema_file, 'r') as f:
            try:
                return json.load(f)
            except ValueError as exc:
                raise exceptions.UserError(
                    'Failed to load schemas because {!r} is not a '
                    'valid json file. Error is : {}'.format(
                        schema_file, str(exc)))
    except IOError as err:
        raise exceptions.UserError(
            'Unable to load schemas from {!r} Error code: {}. '
            'Error message: {}'.format(schema_file, err.errno,
                                       os.strerror(err.errno)))


def validate_plugin_config_content(plugin_config_content):
    if not all(name in plugin_config_content
               for name in EXPECTED_KEYS_IN_PLUGIN_CONFIG):
        missing_fields = [
            key for key in EXPECTED_KEYS_IN_PLUGIN_CONFIG
            if key not in plugin_config_content
        ]
        raise exceptions.UserError(
            'The plugin config file provided is missing some required fields.'
            ' Missing fields are {}'.format(missing_fields))
    if plugin_config_content['language'] != LANGUAGE_DEFAULT:
        raise exceptions.UserError(
            'Invalid language {} found in plugin config file. '
            'Please specify {} as the language in plugin config file'
            ' as it is the only supported option now.'.format(
                plugin_config_content['language'], LANGUAGE_DEFAULT))


def validate_schemas(schemas):
    if not all(schema in schemas for schema in EXPECTED_SCHEMAS):
        missing_fields = [
            key for key in EXPECTED_SCHEMAS if key not in schemas
        ]
        raise exceptions.UserError(
            'The schemas file provided is missing some required schemas. '
            'Missing schema definitions are {}'.format(missing_fields))

    if not all(field in schemas['sourceConfigDefinition']
               for field in EXPECTED_FIELDS):
        missing_fields = [
            key for key in EXPECTED_FIELDS
            if key not in schemas['sourceConfigDefinition']
        ]
        raise exceptions.UserError(
            'The schemas file provided is missing some required fields'
            ' in sourceConfigDefinition schema. Verify that {} are in the'
            ' sourceConfigDefinition'.format(missing_fields))

    if not all(field in schemas['repositoryDefinition']
               for field in EXPECTED_FIELDS):
        missing_fields = [
            key for key in EXPECTED_FIELDS
            if key not in schemas['repositoryDefinition']
        ]
        raise exceptions.UserError(
            'The schemas file provided is missing some required fields'
            ' in repositoryDefinition schema. Verify that {} are in the'
            ' repositoryDefinition'.format(missing_fields))
