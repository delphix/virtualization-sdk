#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import json
import logging
import os
from collections import namedtuple

import yaml
from dlpx.virtualization._internal import (exceptions, file_util,
                                           plugin_importer)
from jsonschema import Draft7Validator

logger = logging.getLogger(__name__)

validation_result = namedtuple('validation_result',
                               ['plugin_config_content', 'plugin_manifest'])


class PluginValidator:
    """
    Reads a plugin config file and validates the contents using a
    pre-defined schema.
    Returns:
        On successful validation, callers can get the content of the plugin
        config, content of the python module specified in in the
        pluginEntryPoint and also name of the plugin entry point in the
        module. If validation fails or has issues - will report exception
        back.
    """
    def __init__(self,
                 plugin_config,
                 plugin_config_schema,
                 plugin_config_content=None):
        self.__plugin_config = plugin_config
        self.__plugin_config_schema = plugin_config_schema
        self.__plugin_config_content = plugin_config_content
        self.__plugin_manifest = None

    @property
    def result(self):
        return validation_result(
            plugin_config_content=self.__plugin_config_content,
            plugin_manifest=self.__plugin_manifest)

    @classmethod
    def from_config_content(cls, plugin_config_file, plugin_config_content,
                            plugin_config_schema):
        """
        Instantiates the validator with given plugin config content.
        plugin_config_file path is not read but used to get the absolute
        path of plugin source directory.
        Returns:
            PluginValidator
        """
        return cls(plugin_config_file, plugin_config_schema,
                   plugin_config_content)

    def validate_plugin_config(self):
        """
        Reads a plugin config file and validates the contents using a
        pre-defined schema. If validation is successful, tries to import
        the plugin module and validates the entry point specified.
        """
        logger.info('Reading plugin config file %s', self.__plugin_config)

        if self.__plugin_config_content is None:
            self.__plugin_config_content = self.__read_plugin_config_file()

        logger.debug('Validating plugin config file content : %s',
                     self.__plugin_config_content)
        self.__validate_plugin_config_content()

    def validate_plugin_module(self):
        """
        Tries to import the plugin module and validates the entry point
        specified.
        """
        self.validate_plugin_config()

        src_dir = file_util.get_src_dir_path(
            self.__plugin_config, self.__plugin_config_content['srcDir'])

        logger.debug('Validating plugin entry point : %s',
                     self.__plugin_config_content['entryPoint'])
        self.__validate_plugin_entry_point(src_dir)

    def __read_plugin_config_file(self):
        """
        Reads a plugin config file and raises UserError if there is an issue
        reading the file.
        """
        try:
            with open(self.__plugin_config, 'rb') as f:
                try:
                    return yaml.safe_load(f)
                except yaml.YAMLError as err:
                    if hasattr(err, 'problem_mark'):
                        mark = err.problem_mark
                        raise exceptions.UserError(
                            'Command failed because the plugin config file '
                            'provided as input \'{}\' was not valid yaml. '
                            'Verify the file contents. '
                            'Error position: {}:{}'.format(
                                self.__plugin_config, mark.line + 1,
                                mark.column + 1))
        except (IOError, OSError) as err:
            raise exceptions.UserError(
                'Unable to read plugin config file \'{}\''
                '\nError code: {}. Error message: {}'.format(
                    self.__plugin_config, err.errno, os.strerror(err.errno)))

    def __validate_plugin_config_content(self):
        """
        Validates the given plugin configuration is valid.

        The plugin configuration should include:
        id              the plugin id
        name            the plugin's displayed name
        version         the plugin version
        hostTypes       the list of supported hostTypes (UNIX and/or WINDOWS)
        entryPoint      the entry point of the plugin defined by the decorator
        srcDir          the directory that the source code is writen in
        schemaFile:     the file containing defined schemas in the plugin
        manualDiscovery whether or not manual discovery is supported
        pluginType      whether the plugin is DIRECT or STAGED
        language        language of the source code(ex: PYTHON27 for python2.7)

        Args:
            plugin_config_content (dict): A dictionary representing a plugin
              configuration file.
        Raises:
            UserError: If the configuration is not valid.
            PathNotAbsoluteError: If the src and schema paths are not absolute.
        """
        # First validate that all the expected keys are in the plugin config.
        plugin_schema = {}
        try:
            with open(self.__plugin_config_schema, 'r') as f:
                try:
                    plugin_schema = json.load(f)
                except ValueError as err:
                    raise exceptions.UserError(
                        'Failed to load schemas because {} is not a '
                        'valid json file. Error: {}'.format(
                            self.__plugin_config_schema, err))

        except (IOError, OSError) as err:
            raise exceptions.UserError(
                'Unable to read plugin config schema file {}'
                '\nError code: {}. Error message: {}'.format(
                    self.__plugin_config_schema, err.errno,
                    os.strerror(err.errno)))

        # Convert plugin config content to json
        plugin_config_json = json.loads(
            json.dumps(self.__plugin_config_content))

        # Validate the plugin config against the schema
        v = Draft7Validator(plugin_schema)

        #
        # This will do lazy validation so that we can consolidate all the
        # validation errors and report everything wrong with the schema.
        #
        validation_errors = sorted(v.iter_errors(plugin_config_json), key=str)

        if validation_errors:
            raise exceptions.SchemaValidationError(self.__plugin_config,
                                                   validation_errors)

    def __validate_plugin_entry_point(self, src_dir):
        """
        Validates the plugin entry point by parsing the entry
        point to get module and entry point. Imports the module
        to check for errors or issues. Also does an eval on the
        entry point.
        """
        entry_point_field = self.__plugin_config_content['entryPoint']
        entry_point_strings = entry_point_field.split(':')

        # Get the module and entry point name to import
        entry_point_module = entry_point_strings[0]
        entry_point_object = entry_point_strings[1]
        plugin_type = self.__plugin_config_content['pluginType']

        try:
            self.__plugin_manifest = (self.__import_plugin(
                src_dir, entry_point_module, entry_point_object, plugin_type))
        except ImportError as err:
            raise exceptions.UserError(
                'Unable to load module \'{}\' specified in '
                'pluginEntryPoint \'{}\' from path \'{}\'. '
                'Error message: {}'.format(entry_point_module,
                                           entry_point_object, src_dir, err))

        logger.debug("Got manifest %s", self.__plugin_manifest)

    @staticmethod
    def __import_plugin(src_dir, entry_point_module, entry_point_object,
                        plugin_type):
        """
        Imports the given python module, does some validations ans returns the
        manifest describing implemented plugin operations.
        """
        importer = plugin_importer.PluginImporter(src_dir, entry_point_module,
                                                  entry_point_object,
                                                  plugin_type, True)
        manifest = importer.import_plugin()

        return manifest
