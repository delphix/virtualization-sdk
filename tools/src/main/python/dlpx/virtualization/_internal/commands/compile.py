#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import logging
import os

from dlpx.virtualization._internal import codegen, plugin_util

logger = logging.getLogger(__name__)
UNKNOWN_ERR = 'UNKNOWN_ERR'

GENERATED_MODULE = 'generated'


def compile(plugin_config):
    """The implementation of compile.

    Takes in a plugin config path reads it for information to determine what
    schemas to generate and where to put it. Run this to be able to write
    the plugin with defined schemas.

    Args:
        plugin_config (str): The path to the plugin config to be used to
        determine what schemas to compile and generate to what path location.

    """

    # Read content of the plugin config  file provided and perform validations
    logger.info('Reading plugin config file %s', plugin_config)
    plugin_config_content = plugin_util.read_plugin_config_file(plugin_config)
    logger.debug('plugin config file content is : %s', plugin_config_content)
    plugin_util.validate_plugin_config_content(plugin_config_content)
    # Read schemas from the file provided in the config and validate them
    logger.info('Reading schemas from %s', plugin_config_content['schemaFile'])
    schemas = plugin_util.read_schema_file(plugin_config_content['schemaFile'])
    logger.debug('schemas found: %s', schemas)
    plugin_util.validate_schemas(schemas)

    # Save the needed fields from the yaml file.
    plugin_config_dir = os.path.dirname(plugin_config)
    name = plugin_config_content['prettyName']
    source_dir = plugin_config_content['srcDir']

    codegen.generate_python(name, source_dir, plugin_config_dir, schemas,
                            GENERATED_MODULE)
