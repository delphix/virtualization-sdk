#
# Copyright (c) 2019, 2020 by Delphix. All rights reserved.
#

import enum
import logging
import os
from contextlib import contextmanager

from dlpx.virtualization._internal import const, exceptions, file_util
from dlpx.virtualization._internal.plugin_importer import PluginImporter
from dlpx.virtualization._internal.plugin_validator import PluginValidator
from dlpx.virtualization._internal.schema_validator import SchemaValidator

logger = logging.getLogger(__name__)


class ValidationMode(enum.Enum):
    """
    Defines the validation mode that validator uses.
    INFO - validator will give out info messages if validation fails.
    WARNING - validator will log a warning if validation fails.
    ERROR - validator will raise an exception if validation fails.
    """
    INFO = 1
    WARNING = 2
    ERROR = 3


@contextmanager
def validate_error_handler(plugin_file, validation_mode):
    try:
        yield
    except Exception as e:
        if validation_mode is ValidationMode.INFO:
            logger.info('Validation failed on plugin file %s : %s',
                        plugin_file, e)
        elif validation_mode is ValidationMode.WARNING:
            logger.warning('Validation failed on plugin file %s : %s',
                           plugin_file, e)
        else:
            raise e


def validate_plugin_config_file(plugin_config,
                                stop_build):
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

    validator = PluginValidator(plugin_config, const.PLUGIN_CONFIG_SCHEMA)

    with validate_error_handler(plugin_config, validation_mode):
        validator.validate_plugin_config()

    return validator.result


def get_plugin_manifest(plugin_config_file,
                        plugin_config_content,
                        stop_build):
    """
    Validates the given plugin config content using a pre-defined schema.
    Plugin config file name is used to get the absolute path of plugin source
    directory. Returns a manifest which indicates method implemented in the
    plugin module.
    """
    validation_mode = (ValidationMode.ERROR
                       if stop_build else ValidationMode.WARNING)
    src_dir = file_util.get_src_dir_path(plugin_config_file,
                                         plugin_config_content['srcDir'])
    entry_point_module, entry_point_object = PluginValidator.split_entry_point(
        plugin_config_content['entryPoint'])
    plugin_type = plugin_config_content['pluginType']

    importer = PluginImporter(src_dir, entry_point_module, entry_point_object,
                              plugin_type, True)

    with validate_error_handler(plugin_config_file, validation_mode):
        importer.validate_plugin_module()

    return importer.result


def validate_schema_file(schema_file, stop_build):
    """
    Reads a plugin schema file and validates the contents using a
    pre-defined schema. If stop_build is True, will report exception
    back, otherwise warnings.
    Returns:
        On successful validation, returns the schemas.
    """
    validation_mode = (ValidationMode.ERROR
                       if stop_build else ValidationMode.WARNING)
    validator = SchemaValidator(schema_file, const.PLUGIN_SCHEMA)

    with validate_error_handler(schema_file, validation_mode):
        validator.validate()

    return validator.result


def get_plugin_config_property(plugin_config_path, prop):
    """
    Returns the value for a specific property from the plugin config file.
    """
    result = validate_plugin_config_file(plugin_config_path, False)
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


def get_standardized_build_number(build_number):
    """
    Converts the build number the way back end expects it to be - without
    leading or trailing zeros in each part of the multi part build number that
    is separated by dots.
    """
    # Split on the period and convert to integer
    array = [int(i) for i in build_number.split('.')]

    # Next we want to trim all trailing zeros so ex: 5.3.0.0 == 5.3
    while array:
        if not array[-1]:
            # Remove the last element which is a zero from array
            array.pop()
        else:
            break

    return '.'.join(str(i) for i in array)
