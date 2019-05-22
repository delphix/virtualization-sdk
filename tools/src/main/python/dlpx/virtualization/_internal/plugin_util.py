#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import logging
import os

from dlpx.virtualization._internal import exceptions
from dlpx.virtualization._internal.plugin_validator import PluginValidator
from dlpx.virtualization._internal.schema_validator import SchemaValidator
from dlpx.virtualization._internal.util_classes import ValidationMode

logger = logging.getLogger(__name__)

STAGED_TYPE = 'STAGED'
DIRECT_TYPE = 'DIRECT'

PLUGIN_SCHEMAS_DIR = os.path.join(os.path.dirname(__file__),
                                  'validation_schemas')
PLUGIN_CONFIG_SCHEMA = os.path.join(PLUGIN_SCHEMAS_DIR,
                                    'plugin_config_schema.json')
PLUGIN_SCHEMA = os.path.join(PLUGIN_SCHEMAS_DIR, 'plugin_schema.json')


def read_and_validate_plugin_config_file(plugin_config, stop_build,
                                         run_all_validations):
    """
    Reads a plugin config file and validates the contents using a
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
    return validator.result


def get_plugin_manifest(plugin_config_file, plugin_config_content, stop_build):
    """
    Validates the given plugin config content using a pre-defined schema.
    Plugin config file name is used to get the absolute path of plugin source
    directory. Returns a manifest which indicates method implemented in the
    plugin module.
    """
    validation_mode = (ValidationMode.ERROR
                       if stop_build else ValidationMode.WARNING)
    validator = PluginValidator.from_config_content(plugin_config_file,
                                                    plugin_config_content,
                                                    PLUGIN_CONFIG_SCHEMA,
                                                    validation_mode)
    validator.validate()
    return validator.result


def read_and_validate_schema_file(schema_file, stop_build):
    """
    Reads a plugin schema file and validates the contents using a
    pre-defined schema. If stop_build is True, will report exception
    back, otherwise warnings.
    Returns:
        On successful validation, returns the schemas.
    """
    validation_mode = (ValidationMode.ERROR
                       if stop_build else ValidationMode.WARNING)
    validator = SchemaValidator(schema_file, PLUGIN_SCHEMA, validation_mode)
    validator.validate()
    return validator.result


def get_plugin_config_property(plugin_config_path, prop):
    """
    Returns the value for a specific property from the plugin config file.
    """
    result = read_and_validate_plugin_config_file(plugin_config_path, False,
                                                  False)
    return result.plugin_config_content[prop]


def get_schema_file_path(plugin_config, schema_file):
    """
    Get the absolute path if schemaFile is a relative path and
     validate that it is a valid file and that it exists.
    """
    if not os.path.isabs(schema_file):
        schema_file = os.path.join(os.path.dirname(plugin_config), schema_file)

    if not os.path.exists(schema_file):
        raise exceptions.PathDoesNotExistError(schema_file)
    if not os.path.isfile(schema_file):
        raise exceptions.PathTypeError(schema_file, 'file')
    return os.path.normpath(schema_file)
