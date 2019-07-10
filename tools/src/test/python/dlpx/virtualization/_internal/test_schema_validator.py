#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import json
import os

import pytest
from dlpx.virtualization._internal import exceptions, util_classes
from dlpx.virtualization._internal.schema_validator import SchemaValidator
from dlpx.virtualization._internal.util_classes import ValidationMode


class TestSchemaValidator:
    @staticmethod
    def test_bad_meta_schema(schema_file, tmpdir, schema_filename):
        meta_schema = '{}\nNOT JSON'.format(json.dumps({'random': 'json'}))
        f = tmpdir.join(schema_filename)
        f.write(meta_schema)
        with pytest.raises(exceptions.UserError) as err_info:
            validator = SchemaValidator(schema_file, f, ValidationMode.ERROR)
            validator.validate()

        message = err_info.value.message
        assert ('Failed to load schemas because {!r} is not a valid json file.'
                ' Error: Extra data: line 2 column 1 - line 2 column 9'
                ' (char 19 - 27)'.format(schema_file)) in message

    @staticmethod
    def test_bad_schema_file(schema_file):
        os.remove(schema_file)
        with pytest.raises(exceptions.UserError) as err_info:
            validator = SchemaValidator(schema_file,
                                        util_classes.PLUGIN_SCHEMA,
                                        ValidationMode.ERROR)
            validator.validate()

        message = err_info.value.message
        assert message == ("Unable to load schemas from '{}'"
                           "\nError code: 2. Error message: No such file or"
                           " directory".format(schema_file))

    @staticmethod
    def test_valid_schema(schema_file):
        validator = SchemaValidator(schema_file, util_classes.PLUGIN_SCHEMA,
                                    ValidationMode.ERROR)
        validator.validate()

    @staticmethod
    @pytest.mark.parametrize('source_config_definition',
                             [{
                                 'required': ['name', 'path'],
                                 'additionalProperties': False,
                                 'properties': {
                                     'name': {
                                         'type': 'string'
                                     },
                                     'path': {
                                         'type': 'string'
                                     }
                                 },
                                 'nameField': 'name',
                                 'identityFields': ['name']
                             }])
    def test_missing_root_type(schema_file):
        #
        # type is not a required field per the JSON/OpenAPI spec. So
        # this test will not raise validation errors even though type
        # is not specified and will pass.
        #
        validator = SchemaValidator(schema_file, util_classes.PLUGIN_SCHEMA,
                                    ValidationMode.ERROR)
        validator.validate()

    @staticmethod
    @pytest.mark.parametrize('source_config_definition',
                             [{
                                 'type': 4,
                                 'required': ['name', 'path'],
                                 'additionalProperties': False,
                                 'properties': {
                                     'name': {
                                         'type': 'string'
                                     },
                                     'path': {
                                         'type': 'string'
                                     }
                                 },
                                 'nameField': 'name',
                                 'identityFields': ['name']
                             }])
    def test_bad_root_type_num(schema_file):
        with pytest.raises(exceptions.SchemaValidationError) as err_info:
            validator = SchemaValidator(schema_file,
                                        util_classes.PLUGIN_SCHEMA,
                                        ValidationMode.ERROR)
            validator.validate()

        message = err_info.value.message
        assert "4 is not valid under any of the given schemas" in message

    @staticmethod
    @pytest.mark.parametrize('source_config_definition',
                             [{
                                 'type': 'x',
                                 'required': ['name', 'path'],
                                 'additionalProperties': False,
                                 'properties': {
                                     'name': {
                                         'type': 'string'
                                     },
                                     'path': {
                                         'type': 'string'
                                     }
                                 },
                                 'nameField': 'name',
                                 'identityFields': ['name']
                             }])
    def test_bad_root_type(schema_file):
        with pytest.raises(exceptions.SchemaValidationError) as err_info:
            validator = SchemaValidator(schema_file,
                                        util_classes.PLUGIN_SCHEMA,
                                        ValidationMode.ERROR)
            validator.validate()

        message = err_info.value.message
        assert "'x' is not valid under any of the given schemas" in message

    @staticmethod
    @pytest.mark.parametrize('source_config_definition',
                             [{
                                 'type': 'object',
                                 'required': ['name', 'path'],
                                 'additionalProperties': False,
                                 'properties': {
                                     'name': {
                                         'type': 'string'
                                     },
                                     'path': {
                                         'type': 'string'
                                     }
                                 },
                                 'nameField': 'name'
                             }])
    def test_missing_identity_fields(schema_file):
        with pytest.raises(exceptions.SchemaValidationError) as err_info:
            validator = SchemaValidator(schema_file,
                                        util_classes.PLUGIN_SCHEMA,
                                        ValidationMode.ERROR)
            validator.validate()

        message = err_info.value.message
        assert "'identityFields' is a required property" in message

    @staticmethod
    @pytest.mark.parametrize('source_config_definition',
                             [{
                                 'type': 'object',
                                 'required': ['name', 'path'],
                                 'additionalProperties': False,
                                 'properties': {
                                     'name': {
                                         'type': 'string'
                                     },
                                     'path': {
                                         'type': 'string'
                                     }
                                 },
                                 'identityFields': ['name']
                             }])
    def test_missing_name_field(schema_file):
        with pytest.raises(exceptions.SchemaValidationError) as err_info:
            validator = SchemaValidator(schema_file,
                                        util_classes.PLUGIN_SCHEMA,
                                        ValidationMode.ERROR)
            validator.validate()

        message = err_info.value.message
        assert "'nameField' is a required property" in message

    @staticmethod
    @pytest.mark.parametrize('source_config_definition',
                             [{
                                 'type': 'object',
                                 'required': ['name', 'path'],
                                 'additionalProperties': False,
                                 'properties': {
                                     'name': {},
                                     'path': {
                                         'type': 'string'
                                     }
                                 },
                                 'nameField': 'name',
                                 'identityFields': ['name']
                             }])
    def test_missing_sub_type(schema_file):
        #
        # type is not a required field per the JSON/OpenAPI spec. So
        # this test will not raise validation errors even though type
        # is not specified and will pass.
        #
        validator = SchemaValidator(schema_file, util_classes.PLUGIN_SCHEMA,
                                    ValidationMode.ERROR)
        validator.validate()

    @staticmethod
    @pytest.mark.parametrize('source_config_definition',
                             [{
                                 'type': 'object',
                                 'required': ['name', 'path'],
                                 'additionalProperties': False,
                                 'properties': {
                                     'name': {
                                         'type': 'x'
                                     },
                                     'path': {
                                         'type': 'string'
                                     }
                                 },
                                 'nameField': 'name',
                                 'identityFields': ['name']
                             }])
    def test_bad_sub_type(schema_file):
        with pytest.raises(exceptions.SchemaValidationError) as err_info:
            validator = SchemaValidator(schema_file,
                                        util_classes.PLUGIN_SCHEMA,
                                        ValidationMode.ERROR)
            validator.validate()

        message = err_info.value.message
        assert "'x' is not valid under any of the given schemas" in message

    @staticmethod
    @pytest.mark.parametrize('source_config_definition',
                             [{
                                 'type': 'object',
                                 'required': ['name', 'path'],
                                 'additionalProperties': False,
                                 'properties': {
                                     'name': {
                                         'type': 4
                                     },
                                     'path': {
                                         'type': 'string'
                                     }
                                 },
                                 'nameField': 'name',
                                 'identityFields': ['name']
                             }])
    def test_bad_sub_type_num(schema_file):
        with pytest.raises(exceptions.SchemaValidationError) as err_info:
            validator = SchemaValidator(schema_file,
                                        util_classes.PLUGIN_SCHEMA,
                                        ValidationMode.ERROR)
            validator.validate()

        message = err_info.value.message
        assert "4 is not valid under any of the given schemas" in message

    @staticmethod
    @pytest.mark.parametrize('source_config_definition',
                             [{
                                 'type': 'object',
                                 'required': ['path1'],
                                 'additionalProperties': False,
                                 'properties': {
                                     'name': {
                                         'type': 'string'
                                     }
                                 },
                                 'nameField': 'name',
                                 'identityFields': ['name']
                             }])
    def test_missing_required_field(schema_file):
        #
        # This test will fail since required fields validation does not work
        # for some cases. Once PYT-382 is fixed, re-enable this test.
        #
        pytest.skip("required fields validation is not working yet")
        with pytest.raises(exceptions.SchemaValidationError) as err_info:
            validator = SchemaValidator(schema_file,
                                        util_classes.PLUGIN_SCHEMA,
                                        ValidationMode.ERROR)
            validator.validate()

        message = err_info.value.message
        assert "'type' is a required property." in message

    @staticmethod
    @pytest.mark.parametrize('source_config_definition',
                             [{
                                 'type': 'x',
                                 'required': ['name', 'path'],
                                 'additionalProperties': False,
                                 'properties': {
                                     'name': {
                                         'type': 'string'
                                     },
                                     'path': {
                                         'type': 'string'
                                     }
                                 },
                                 'nameField': 'name'
                             }])
    def test_multiple_validation_errors(schema_file):
        with pytest.raises(exceptions.SchemaValidationError) as err_info:
            validator = SchemaValidator(schema_file,
                                        util_classes.PLUGIN_SCHEMA,
                                        ValidationMode.ERROR)
            validator.validate()

        message = err_info.value.message
        assert "'x' is not valid under any of the given schemas" in message
        assert "'identityFields' is a required property" in message

    @staticmethod
    @pytest.mark.parametrize('validation_mode',
                             [ValidationMode.INFO, ValidationMode.WARNING])
    @pytest.mark.parametrize('source_config_definition',
                             [{
                                 'type': 'object',
                                 'required': ['name', 'path'],
                                 'additionalProperties': False,
                                 'properties': {
                                     'name': {
                                         'type': 'x'
                                     },
                                     'path': {
                                         'type': 'string'
                                     }
                                 },
                                 'nameField': 'name',
                                 'identityFields': ['name']
                             }])
    def test_bad_sub_type_info_warn_mode(schema_file, validation_mode):
        err_info = None
        try:
            validator = SchemaValidator(schema_file,
                                        util_classes.PLUGIN_SCHEMA,
                                        validation_mode)
            validator.validate()
        except Exception as e:
            err_info = e

        assert err_info is None
