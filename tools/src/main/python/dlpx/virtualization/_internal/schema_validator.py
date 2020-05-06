#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import json
import logging
import os
from collections import namedtuple

from dlpx.virtualization._internal import exceptions
from jsonschema import Draft7Validator

logger = logging.getLogger(__name__)

validation_result = namedtuple('validation_result', ['plugin_schemas'])


class SchemaValidator:
    """
    Reads a plugin schema file and validates the contents using a
    pre-defined schema.
    Returns:
        On successful validation, callers can get the content of the plugin
        schemas. If validation fails or has issues - will report exception
        back.
    """
    def __init__(self, schema_file, plugin_meta_schema, schemas=None):
        self.__schema_file = schema_file
        self.__plugin_meta_schema = plugin_meta_schema
        self.__plugin_schemas = schemas

    @property
    def result(self):
        return validation_result(plugin_schemas=self.__plugin_schemas)

    def validate(self):
        """
        Reads a plugin schema file and validates the contents using a
        pre-defined schema.
        """
        logger.info('Reading plugin schema file %s', self.__schema_file)

        if self.__plugin_schemas is None:
            self.__plugin_schemas = self.__read_schema_file()

        logger.debug('Validating plugin schema file content : %s',
                     self.__plugin_schemas)
        self.__validate_schemas()

    def __read_schema_file(self):
        """
        Reads a plugin schema file and raises UserError if there is an issue
        reading the file.
        """
        try:
            with open(self.__schema_file, 'r') as f:
                try:
                    return json.load(f)
                except ValueError as err:
                    raise exceptions.UserError(
                        'Failed to load schemas because \'{}\' is not a '
                        'valid json file. Error: {}'.format(
                            self.__schema_file, err))
        except (IOError, OSError) as err:
            raise exceptions.UserError(
                'Unable to load schemas from \'{}\''
                '\nError code: {}. Error message: {}'.format(
                    self.__schema_file, err.errno, os.strerror(err.errno)))

    def __validate_schemas(self):
        """
        Validates the given plugin schemas are valid.
        Raises:
            UserError: If the schemas are not valid.
        """
        plugin_meta_schema = {}
        try:
            with open(self.__plugin_meta_schema, 'r') as f:
                try:
                    plugin_meta_schema = json.load(f)
                except ValueError as err:
                    raise exceptions.UserError(
                        'Failed to load schemas because \'{}\' is not a '
                        'valid json file. Error: {}'.format(
                            self.__plugin_meta_schema, err))

        except (IOError, OSError) as err:
            raise exceptions.UserError(
                'Unable to read plugin schema file \'{}\''
                '\nError code: {}. Error message: {}'.format(
                    self.__plugin_meta_schema, err.errno,
                    os.strerror(err.errno)))

        # Validate the plugin schema against the meta schema
        v = Draft7Validator(plugin_meta_schema)

        #
        # This will do lazy validation so that we can consolidate all the
        # validation errors and report everything wrong with the schema.
        #
        validation_errors = sorted(v.iter_errors(self.__plugin_schemas),
                                   key=lambda e: e.path)

        if validation_errors:
            raise exceptions.SchemaValidationError(self.__schema_file,
                                                   validation_errors)
