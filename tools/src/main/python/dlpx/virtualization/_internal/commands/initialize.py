#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import logging
import os
import shutil
from collections import OrderedDict

import jinja2
import yaml

from dlpx.virtualization._internal import exceptions, file_util, plugin_util

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
INIT_FILE_ROOT = os.path.dirname(__file__)
PLUGIN_TEMPLATE_DIR = os.path.join(INIT_FILE_ROOT, 'plugin_template')
ENTRY_POINT_TEMPLATE_PATH = os.path.join(PLUGIN_TEMPLATE_DIR,
                                         'entry_point_template.py')
SCHEMA_TEMPLATE_PATH = os.path.join(PLUGIN_TEMPLATE_DIR,
                                    'schema_template.json')


def init(root, plugin_name, ingestion_strategy, pretty_name):
    """
    Creates a valid plugin in a given directory. The plugin created will be
    able to be built and uploaded immediately.

    This command is designed to help novice plugin developers. There are
    decisions made, such as what the entry point file looks like, in order to
    make it easier for authors to get started. The command is expected to be
    used by experienced developers, but they are not the primary audience.

    Args:
        root (str): The path of the plugin's root directory
        plugin_name (str): The name of the new plugin
        ingestion_strategy (str): The plugin type. Either DIRECT or STAGED
        pretty_name (str): The name of the plugin to display.
    """
    logger.info('Initializing directory: %s', root)
    logger.debug(
        'init parameters: %s', {
            'Root': root,
            'Plugin Name': plugin_name,
            'Ingestion Strategy': ingestion_strategy,
            'Pretty Name': pretty_name
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

    # If the pretty name isn't provided, use the plugin name
    pretty_name = pretty_name or plugin_name
    logger.debug("Using %r as the plugin's pretty name.", pretty_name)

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

        #
        # Create the plugin config file. The config file relies on input from
        # the user, so it's easier to deal with a dictionary than a file. This
        # must be done only after both the schema file and src dir have been
        # created since the paths need to exist.
        #
        logger.info('Writing config file at %r.', config_file_path)
        with open(config_file_path, 'w+') as f:
            config = _get_default_plugin_config(plugin_name,
                                                ingestion_strategy,
                                                pretty_name,
                                                DEFAULT_ENTRY_POINT,
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
            entry_point_content = _get_entry_point_file(plugin_name)
            f.write(entry_point_content)

    except Exception as e:
        logger.debug('Attempting to cleanup after failure.')
        file_util.delete_paths(DEFAULT_PLUGIN_CONFIG_FILE, DEFAULT_SCHEMA_FILE,
                               DEFAULT_SRC_DIRECTORY)
        raise exceptions.UserError(
            'Failed to initialize plugin directory {!r}: {}.'.format(root, e))


def _get_entry_point_file(plugin_name):
    env = jinja2.Environment(loader=jinja2.PackageLoader(
        __package__, 'plugin_template'),
                             autoescape=jinja2.select_autoescape(['py']))

    template = env.get_template('entry_point.py.template')
    return template.render(name=repr(plugin_name))


def _get_default_plugin_config(plugin_name, ingestion_strategy, pretty_name,
                               entry_point, src_dir_path, schema_file_path):
    """
    Returns a valid plugin configuration as an OrderedDict.

    Args:
         plugin_name (str): The name of the plugin this configuration is for.
        ingestion_strategy (str): Used as the plugin type.
            Either 'DIRECT' or 'STAGED'.
        pretty_name (str): The name of the plugin that will be used in the UI.
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
    config = OrderedDict([('name', plugin_name.encode('utf-8')),
                          ('prettyName', pretty_name.encode('utf-8')),
                          ('version', '0.1.0'), ('language', 'PYTHON27'),
                          ('hostTypes', ['UNIX']),
                          ('pluginType', ingestion_strategy.encode('utf-8')),
                          ('manualDiscovery', True),
                          ('entryPoint', entry_point.encode('utf-8')),
                          ('srcDir', src_dir_path.encode('utf-8')),
                          ('schemaFile', schema_file_path.encode('utf-8'))])

    # This should always return something valid
    plugin_util.validate_plugin_config_content(config)
    return config
