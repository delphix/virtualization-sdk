#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import logging
import os
import shutil
import uuid
from collections import OrderedDict

import jinja2
import yaml
from dlpx.virtualization._internal import (codegen, exceptions, file_util,
                                           plugin_util, util_classes)

logger = logging.getLogger(__name__)

# Defaults for plugin files, properties, and symbols.
DEFAULT_PLUGIN_CONFIG_FILE = 'plugin_config.yml'
DEFAULT_SCHEMA_FILE = 'schema.json'
DEFAULT_SRC_DIRECTORY = 'src'
DEFAULT_ENTRY_POINT_FILE = 'plugin_runner.py'
DEFAULT_ENTRY_POINT_SYMBOL = 'plugin'
DEFAULT_ENTRY_POINT = '{}:{}'.format(DEFAULT_ENTRY_POINT_FILE[:-3],
                                     DEFAULT_ENTRY_POINT_SYMBOL)

# Internal constants for the template directory.
ENTRY_POINT_TEMPLATE_NAME = 'entry_point.py.template'
DIRECT_OPERATIONS_TEMPLATE_NAME = 'direct_operations.py.template'
STAGED_OPERATIONS_TEMPLATE_NAME = 'staged_operations.py.template'
INIT_FILE_ROOT = os.path.dirname(__file__)
PLUGIN_TEMPLATE_DIR = os.path.join(INIT_FILE_ROOT, 'plugin_template')
SCHEMA_TEMPLATE_PATH = os.path.join(PLUGIN_TEMPLATE_DIR,
                                    'schema_template.json')


def init(root, ingestion_strategy, name):
    """
    Creates a valid plugin in a given directory. The plugin created will be
    able to be built and uploaded immediately.

    This command is designed to help novice plugin developers. There are
    decisions made, such as what the entry point file looks like, in order to
    make it easier for authors to get started. The command is expected to be
    used by experienced developers, but they are not the primary audience.

    Args:
        root (str): The path of the plugin's root directory
        ingestion_strategy (str): The plugin type. Either DIRECT or STAGED
        name (str): The name of the plugin to display.
    """
    logger.info('Initializing directory: %s', root)
    logger.debug('init parameters: %s', {
        'Root': root,
        'Ingestion Strategy': ingestion_strategy,
        'Name': name
    })

    # Files paths based on 'root' to be used throughout
    src_dir_path = os.path.join(root, DEFAULT_SRC_DIRECTORY)
    config_file_path = os.path.join(root, DEFAULT_PLUGIN_CONFIG_FILE)
    schema_file_path = os.path.join(root, DEFAULT_SCHEMA_FILE)
    entry_point_file_path = os.path.join(src_dir_path,
                                         DEFAULT_ENTRY_POINT_FILE)

    # Make sure nothing is overwritten
    file_util.validate_paths_do_not_exist(config_file_path, schema_file_path,
                                          src_dir_path)

    # Make an UUID for the plugin
    plugin_id = str(uuid.uuid4())
    logger.debug("Using % r as the plugin id.", plugin_id)

    # if name is not provided the name will be equal to plugin_id.
    if not name:
        name = plugin_id

    #
    # Some magic to get the yaml module to maintain the order when dumping
    # an OrderedDict
    #
    yaml.add_representer(
        OrderedDict, lambda dumper, data: dumper.represent_mapping(
            'tag:yaml.org,2002:map', data.items()))

    logger.debug("Using %r as the plugin's entry point.", DEFAULT_ENTRY_POINT)
    try:
        #
        # Create the source directory. We've already validated that this
        # directory doesn't exist.
        #
        logger.info('Creating source directory at %r.', src_dir_path)
        os.mkdir(src_dir_path)

        #
        # Copy the schema file template into the root directory. The schema
        # file is static and doesn't depend on any input so it can just be
        # copied. By copying we can also avoid dealing with ordering issues.
        #
        logger.info('Writing schema file at %r.', schema_file_path)
        shutil.copyfile(SCHEMA_TEMPLATE_PATH, schema_file_path)

        # Read and valida the schema file
        result = plugin_util.read_and_validate_schema_file(
            schema_file_path, False)

        # Generate the definitions based on the schema file
        codegen.generate_python(name, src_dir_path,
                                os.path.dirname(config_file_path),
                                result.plugin_schemas)

        #
        # Create the plugin config file. The config file relies on input from
        # the user, so it's easier to deal with a dictionary than a file. This
        # must be done only after both the schema file and src dir have been
        # created since the paths need to exist.
        #
        logger.info('Writing config file at %r.', config_file_path)
        with open(config_file_path, 'w+') as f:
            config = _get_default_plugin_config(plugin_id, ingestion_strategy,
                                                name, DEFAULT_ENTRY_POINT,
                                                DEFAULT_SRC_DIRECTORY,
                                                DEFAULT_SCHEMA_FILE)
            yaml.dump(config, f, default_flow_style=False)

        #
        # Copy the entry point template into the root directory. The entry
        # point file is static and doesn't depend on any input so it can just
        # be copied.
        #
        logger.info('Writing entry file at %r.', entry_point_file_path)
        with open(entry_point_file_path, 'w+') as f:
            entry_point_content = _get_entry_point_contents(
                plugin_id, ingestion_strategy)
            f.write(entry_point_content)

    except Exception as e:
        logger.debug('Attempting to cleanup after failure. %s', e)
        file_util.delete_paths(config_file_path, schema_file_path,
                               src_dir_path)
        raise exceptions.UserError(
            'Failed to initialize plugin directory {!r}: {}.'.format(root, e))


def _get_entry_point_contents(plugin_name, ingestion_strategy):
    """
    Creates a valid, complete entry point file from the template with the
    given parameters that is escaped correctly and ready to be written.

    Args:
        plugin_name (str): The name of the plugin to use for the entry point.
            This should not be escaped.
    Returns:
        str: The contents of a valid entry point file.
    """
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(PLUGIN_TEMPLATE_DIR), autoescape=False)

    template = env.get_template(ENTRY_POINT_TEMPLATE_NAME)

    if ingestion_strategy == util_classes.DIRECT_TYPE:
        linked_operations = env.get_template(
            DIRECT_OPERATIONS_TEMPLATE_NAME).render()
    elif ingestion_strategy == util_classes.STAGED_TYPE:
        linked_operations = env.get_template(
            STAGED_OPERATIONS_TEMPLATE_NAME).render()
    else:
        raise RuntimeError('Got unrecognized ingestion strategy: {!r}'.format(
            ingestion_strategy))

    # Call 'repr' to put the string in quotes and escape quotes.
    return template.render(name=repr(plugin_name),
                           linked_operations=linked_operations)


def _get_default_plugin_config(plugin_id, ingestion_strategy, name,
                               entry_point, src_dir_path, schema_file_path):
    """
    Returns a valid plugin configuration as an OrderedDict.

    Args:
        plugin_id (str): The unique id of the plugin this configuration is for.
        ingestion_strategy (str): Used as the plugin type.
            Either 'DIRECT' or 'STAGED'.
        name (str): The name of the plugin that will be used in the UI.
        entry_point (str): The full entry point for the plugin, including both
            the module and symbol.
        src_dir_path (str): The path to the source directory of the plugin.
        schema_file_path (str): The path to the schema file of the plugin.
    Returns:
        OrderedDict: A valid plugin configuration roughly ordered from most
            interesting to a new plugin author to least interesting.
    """
    # Ensure values are type 'str'. If they are type unicode yaml prints
    # them with '!!python/unicode' prepended to the value.
    config = OrderedDict([('id', plugin_id.encode('utf-8')),
                          ('name', name.encode('utf-8')), ('version', '0.1.0'),
                          ('language', 'PYTHON27'), ('hostTypes', ['UNIX']),
                          ('pluginType', ingestion_strategy.encode('utf-8')),
                          ('entryPoint', entry_point.encode('utf-8')),
                          ('srcDir', src_dir_path.encode('utf-8')),
                          ('schemaFile', schema_file_path.encode('utf-8'))])

    return config
