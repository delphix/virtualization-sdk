#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import json
import logging
import os

from dlpx.virtualization._internal import exceptions
from dlpx.virtualization._internal.plugin_validator import (PluginValidator,
                                                            ValidationMode)

logger = logging.getLogger(__name__)

EXPECTED_SCHEMAS = frozenset({
    'repositoryDefinition', 'sourceConfigDefinition',
    'virtualSourceDefinition', 'linkedSourceDefinition', 'snapshotDefinition'
})

LANGUAGE_DEFAULT = 'PYTHON27'

STAGED_TYPE = 'STAGED'
DIRECT_TYPE = 'DIRECT'

EXPECTED_FIELDS = frozenset({'identityFields', 'nameField'})
PLUGIN_SCHEMAS_DIR = os.path.join(os.path.dirname(__file__),
                                  'validation_schemas')
PLUGIN_CONFIG_SCHEMA = os.path.join(PLUGIN_SCHEMAS_DIR,
                                    'plugin_config_schema.json')


def read_and_validate_plugin_config_file(plugin_config, stop_build,
                                         run_all_validations):
    """Reads a plugin config file and validates the contents using a
    pre-defined schema. If stop_build is True, will report exception
    back, otherwise warnings.
    Returns:
        On successful validation, returns content of the plugin
        config.
    """
    validation_mode = (ValidationMode.ERROR
                       if stop_build else ValidationMode.WARNING)
    validator = PluginValidator(plugin_config, PLUGIN_CONFIG_SCHEMA,
                                validation_mode, run_all_validations)
    validator.validate()
    return validator.plugin_config_content


def validate_plugin_config_content(plugin_config_file, plugin_config_content,
                                   stop_build):
    """Validates the given plugin config content using a pre-defined schema.
    Plugin config file name is used to get the absolute path of plugin source
    directory.
    """
    validation_mode = (ValidationMode.ERROR
                       if stop_build else ValidationMode.WARNING)
    validator = PluginValidator.from_config_content(plugin_config_file,
                                                    plugin_config_content,
                                                    PLUGIN_CONFIG_SCHEMA,
                                                    validation_mode)
    validator.validate()
    return validator.plugin_module_content, validator.plugin_entry_point


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

    # Next validate that no unexpected schemas are there.
    if not all(schema in EXPECTED_SCHEMAS for schema in schemas):
        extra_fields = [
            key.encode('UTF8') for key in schemas
            if key not in EXPECTED_SCHEMAS
        ]
        raise exceptions.UserError(
            'The schemas file provided contains extra defined schemas. '
            'Extra schema definitions are {}'.format(extra_fields))

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
