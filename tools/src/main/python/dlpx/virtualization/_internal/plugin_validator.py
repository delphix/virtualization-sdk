#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import json
import logging
import os
from collections import defaultdict, namedtuple

import yaml
from dlpx.virtualization._internal import exceptions
from dlpx.virtualization._internal.codegen import CODEGEN_PACKAGE
from flake8.api import legacy as flake8
from jsonschema import Draft7Validator

logger = logging.getLogger(__name__)

validation_result = namedtuple('validation_result', ['plugin_config_content'])


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
        self.__pre_import_checks = [
            self.__validate_plugin_config_content,
            self.__validate_plugin_entry_point,
            self.__check_for_undefined_names,
            self.__check_for_lua_name_and_min_version
        ]

    @property
    def result(self):
        return validation_result(
            plugin_config_content=self.__plugin_config_content)

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
        pre-defined schema.
        """
        if self.__plugin_config_content is None:
            self.__plugin_config_content = self.__read_plugin_config_file()

        logger.debug('Validating plugin config file content : %s',
                     self.__plugin_config_content)
        self.__run_checks()

    def __read_plugin_config_file(self):
        """
        Reads a plugin config file and raises UserError if there is an issue
        reading the file.
        """
        logger.info('Reading plugin config file %s', self.__plugin_config)
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

    def __run_checks(self):
        """
        Runs validations on the plugin config content and raise exceptions
        if any.
        """
        #
        # All the pre-import checks need to happen in sequence. So no point
        # validating further if a check fails.
        #
        for check in self.__pre_import_checks:
            check()

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

    def __validate_plugin_entry_point(self):
        """
        Validates the plugin entry point by parsing the entry
        point to get module and entry point.
        """
        # Get the module and entry point name to import
        entry_point_module, entry_point_object = self.split_entry_point(
            self.__plugin_config_content['entryPoint'])

        if not entry_point_module:
            raise exceptions.UserError('Plugin module is invalid')

        if not entry_point_object:
            raise exceptions.UserError('Plugin object is invalid')

    def __check_for_undefined_names(self):
        """
        Checks the plugin module for undefined names. This catches
        missing imports, references to nonexistent variables, etc.

        ..note::
            We are using the legacy flake8 api, because there is currently
            no public, stable api for flake8 >= 3.0.0

            For more info, see
            https://flake8.pycqa.org/en/latest/user/python-api.html
        """
        warnings = defaultdict(list)
        src_dir = self.__plugin_config_content['srcDir']
        exclude_dir = os.path.sep.join([src_dir, CODEGEN_PACKAGE])
        style_guide = flake8.get_style_guide(select=["F821"],
                                             exclude=[exclude_dir],
                                             quiet=1)
        style_guide.check_files(paths=[src_dir])
        file_checkers = style_guide._application.file_checker_manager.checkers

        for checker in file_checkers:
            for result in checker.results:
                # From the api code, result is a tuple defined as: error =
                # (error_code, line_number, column, text, physical_line)
                if result[0] == 'F821':
                    msg = "{} on line {} in {}".format(result[3], result[1],
                                                       checker.filename)
                    warnings['exception'].append(exceptions.UserError(msg))

        if warnings and len(warnings) > 0:
            raise exceptions.ValidationFailedError(warnings)

    def __check_for_lua_name_and_min_version(self):
        """
        Check if both lua name and minimum lua version are present if either
        property is set.
        """
        warnings = defaultdict(list)

        if (self.__plugin_config_content.get('luaName') and not
           self.__plugin_config_content.get('minimumLuaVersion')):
            msg = ('Failed to process property "luaName" without '
                   '"minimumLuaVersion" set in the plugin config.')
            warnings['exception'].append(exceptions.UserError(msg))

        if (self.__plugin_config_content.get('minimumLuaVersion') and not
           self.__plugin_config_content.get('luaName')):
            msg = ('Failed to process property "minimumLuaVersion" without '
                   '"luaName" set in the plugin config.')
            warnings['exception'].append(exceptions.UserError(msg))

        if warnings and len(warnings) > 0:
            raise exceptions.ValidationFailedError(warnings)

    @staticmethod
    def split_entry_point(entry_point):
        entry_point_strings = entry_point.split(':')
        return entry_point_strings[0], entry_point_strings[1]
