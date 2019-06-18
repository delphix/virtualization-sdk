#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import importlib
import json
import os
import subprocess
import sys

import pytest
from dlpx.virtualization._internal import codegen


@pytest.fixture(scope='module')
def tmp_factory(tmp_path_factory):
    # Save the current system python path
    save_path = list(sys.path)
    # insert the temp directory into the
    sys.path.insert(0, str(tmp_path_factory.getbasetemp().resolve()))
    # return the path factory
    yield (tmp_path_factory)
    # Reset the python path at the end of the session
    sys.path = save_path


@pytest.fixture(scope='class')
def module(tmp_factory, schema_content):
    basedir = tmp_factory.getbasetemp().resolve()
    swagger_file = str(basedir.joinpath(codegen.SWAGGER_FILE_NAME))
    codegen._write_swagger_file('test', schema_content, str(basedir))
    tmpdir = tmp_factory.mktemp('template_test').resolve()
    # create the config file to point to the tmpdir
    config_dict = {'packageName': tmpdir.name}
    config_file = basedir.joinpath('codegen-config.json')
    config_file.write_bytes(json.dumps(config_dict, indent=2))
    execute_swagger_codegen(swagger_file, str(config_file), str(basedir))

    return importlib.import_module('.definitions', package=tmpdir.name)


def execute_swagger_codegen(swagger_file, config_file, output_dir):
    jar = os.path.join(os.path.dirname(codegen.__file__), codegen.SWAGGER_JAR)
    codegen_template = os.path.join(os.path.dirname(codegen.__file__),
                                    codegen.CODEGEN_TEMPLATE_DIR)

    # Create the process that runs the jar putting stdout / stderr into pipes.
    process_inputs = [
        'java', '-jar', jar, 'generate', '-DsupportPython2=true', '-i',
        swagger_file, '-l', 'python-flask', '-c', config_file, '-t',
        codegen_template, '--model-package', codegen.CODEGEN_MODULE, '-o',
        output_dir
    ]

    process = subprocess.Popen(process_inputs,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    # Get the pipes pointed so we have access to them.
    stdout, stderr = process.communicate()

    #
    # Wait for the process to end and take the results. If res then we know
    # something failed so fail the test.
    #
    if process.wait():
        assert False, 'stdout: {}, stderr: {}'.format(stdout, stderr)


class TestTemplateStringProperty:
    @staticmethod
    @pytest.fixture(scope='class')
    def schema_content():
        content = {
            'TestDefinition': {
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'stringProperty': {
                        'type': 'string',
                        'minLength': 5,
                        'maxLength': 10
                    },
                    'requiredStringProperty': {
                        'type': 'string',
                        'pattern': "^test.*"
                    }
                },
                'required': ['requiredStringProperty']
            }
        }
        return content

    @staticmethod
    def test_success(module):
        test_object = module.TestDefinition('test string')
        assert test_object.required_string_property == 'test string'
        assert not test_object.string_property

        test_dict = test_object.to_dict()
        assert test_dict == {
            'requiredStringProperty': 'test string',
            'stringProperty': None
        }
        from_dict_object = module.TestDefinition.from_dict(test_dict)
        assert test_object == from_dict_object

    @staticmethod
    def test_success_setter(module):
        test_object = module.TestDefinition('test string')
        test_object.string_property = 'set test'

        assert test_object.required_string_property == 'test string'
        assert test_object.string_property == 'set test'

        test_dict = test_object.to_dict()
        assert test_dict == {
            'requiredStringProperty': 'test string',
            'stringProperty': 'set test'
        }
        from_dict_object = module.TestDefinition.from_dict(test_dict)
        assert test_object == from_dict_object

    @staticmethod
    def test_unicode_success(module):
        test_object = module.TestDefinition(u'test\u2345\u2603')
        assert test_object.required_string_property == u'test\u2345\u2603'
        assert not test_object.string_property

        test_dict = test_object.to_dict()
        assert test_dict == {
            'requiredStringProperty': u'test\u2345\u2603',
            'stringProperty': None
        }
        from_dict_object = module.TestDefinition.from_dict(test_dict)
        assert test_object == from_dict_object

    @staticmethod
    def test_unicode_success_setter(module):
        # Even strings that have \u will parse as a string correctly
        test_object = module.TestDefinition('test string\u0369')
        test_object.string_property = u'\u2346\u2633\u9476\u0369\u2468\u1111'

        assert test_object.required_string_property == 'test string\u0369'
        assert (test_object.string_property ==
                u'\u2346\u2633\u9476\u0369\u2468\u1111')

        test_dict = test_object.to_dict()
        assert test_dict == {
            'requiredStringProperty': 'test string\u0369',
            'stringProperty': u'\u2346\u2633\u9476\u0369\u2468\u1111'
        }
        from_dict_object = module.TestDefinition.from_dict(test_dict)
        assert test_object == from_dict_object

    @staticmethod
    def test_required_param_missing(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition()

        message = err_info.value.message
        assert message == ("The required parameter 'required_string_property'"
                           " must not be 'None'.")

        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(string_property='test_string')

        message = err_info.value.message
        assert message == ("The required parameter 'required_string_property'"
                           " must not be 'None'.")

    @staticmethod
    def test_required_param_missing_setter(module):
        test_object = module.TestDefinition('test string')
        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_string_property = None

        message = err_info.value.message
        assert message == ("The required parameter 'required_string_property'"
                           " must not be 'None'.")

    @staticmethod
    def test_not_string(module):
        with pytest.raises(module.GeneratedClassesTypeError) as err_info:
            module.TestDefinition('test string', 10)

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'string_property' was"
            " type 'int' but should be of type 'basestring' if defined.")

    @staticmethod
    def test_not_string_setter(module):
        test_object = module.TestDefinition('test string')

        with pytest.raises(module.GeneratedClassesTypeError) as err_info:
            test_object.string_property = 10

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'string_property' was"
            " type 'int' but should be of type 'basestring' if defined.")

    @staticmethod
    def test_min_length(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition('test string', 'test')

        message = err_info.value.message
        assert message == ("Invalid value for 'string_property', length was 4"
                           " but must be greater than or equal to 5.")

    @staticmethod
    def test_min_length_setter(module):
        test_object = module.TestDefinition('test string')

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.string_property = 'test'

        message = err_info.value.message
        assert message == ("Invalid value for 'string_property', length was 4"
                           " but must be greater than or equal to 5.")

    @staticmethod
    def test_max_length(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition('test string', 'test too long of string')

        message = err_info.value.message
        assert message == ("Invalid value for 'string_property', length was 23"
                           " but must be less than or equal to 10.")

    @staticmethod
    def test_max_length_setter(module):
        test_object = module.TestDefinition('test string')

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.string_property = 'test too long of string'

        message = err_info.value.message
        assert message == ("Invalid value for 'string_property', length was 23"
                           " but must be less than or equal to 10.")

    @staticmethod
    def test_bad_pattern(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition('bad test string')

        message = err_info.value.message
        assert message == ("Invalid value for 'required_string_property',"
                           " was 'bad test string' but must follow the pattern"
                           " '^test.*'.")

    @staticmethod
    def test_bad_pattern_setter(module):
        test_object = module.TestDefinition('test string')

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_string_property = 'bad test string'

        message = err_info.value.message
        assert message == ("Invalid value for 'required_string_property',"
                           " was 'bad test string' but must follow the pattern"
                           " '^test.*'.")


class TestTemplateNumericProperty:
    @staticmethod
    @pytest.fixture(scope='class')
    def schema_content():
        content = {
            'TestDefinition': {
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'numberProperty': {
                        'type': 'number',
                        'minimum': 10.0,
                    },
                    'requiredNumberProperty': {
                        'type': 'number',
                        'minimum': 2.0,
                        'exclusiveMinimum': True
                    },
                    'integerProperty': {
                        'type': 'integer',
                        'maximum': 20
                    },
                    'requiredIntegerProperty': {
                        'type': 'integer',
                        'maximum': 100,
                        'exclusiveMaximum': True
                    }
                },
                'required':
                ['requiredNumberProperty', 'requiredIntegerProperty']
            }
        }
        return content

    @staticmethod
    def test_success(module):
        test_object = module.TestDefinition(200.5, None, -50)
        assert test_object.required_number_property == 200.5
        assert not test_object.number_property

        assert test_object.required_integer_property == -50
        assert not test_object.integer_property

        test_dict = test_object.to_dict()
        assert test_dict == {
            'requiredNumberProperty': 200.5,
            'numberProperty': None,
            'requiredIntegerProperty': -50,
            'integerProperty': None
        }
        from_dict_object = module.TestDefinition.from_dict(test_dict)
        assert test_object == from_dict_object

    @staticmethod
    def test_success_setter(module):
        test_object = module.TestDefinition(200.5, None, -50)
        test_object.number_property = 13.5
        test_object.integer_property = 18

        assert test_object.required_number_property == 200.5
        assert test_object.number_property == 13.5
        assert test_object.required_integer_property == -50
        assert test_object.integer_property == 18

        test_dict = test_object.to_dict()
        assert test_dict == {
            'requiredNumberProperty': 200.5,
            'numberProperty': 13.5,
            'requiredIntegerProperty': -50,
            'integerProperty': 18
        }
        from_dict_object = module.TestDefinition.from_dict(test_dict)
        assert test_object == from_dict_object

    @staticmethod
    def test_success_number_is_int(module):
        test_object = module.TestDefinition(200, 13, -50, 18)

        assert test_object.required_number_property == 200
        assert test_object.number_property == 13
        assert test_object.required_integer_property == -50
        assert test_object.integer_property == 18

    @staticmethod
    def test_int_passed_in_as_float(module):
        with pytest.raises(module.GeneratedClassesTypeError) as err_info:
            module.TestDefinition(200.5, 13.5, -50.5, 18.5)

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_integer_property' was"
            " type 'float' but should be of type 'int'.")

    @staticmethod
    def test_required_param_missing(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition()

        message = err_info.value.message
        assert message == ("The required parameter 'required_number_property'"
                           " must not be 'None'.")

        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(200.5)

        message = err_info.value.message
        assert message == ("The required parameter 'required_integer_property'"
                           " must not be 'None'.")

        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(None, 13.5, -50, 18)

        message = err_info.value.message
        assert message == ("The required parameter 'required_number_property'"
                           " must not be 'None'.")

        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(200.5, 13.5, None, 18)

        message = err_info.value.message
        assert message == ("The required parameter 'required_integer_property'"
                           " must not be 'None'.")

    @staticmethod
    def test_required_param_missing_setter(module):
        test_object = module.TestDefinition(200.5, None, -50)
        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_number_property = None

        message = err_info.value.message
        assert message == ("The required parameter 'required_number_property'"
                           " must not be 'None'.")

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_integer_property = None

        message = err_info.value.message
        assert message == ("The required parameter 'required_integer_property'"
                           " must not be 'None'.")

    @staticmethod
    def test_not_number(module):
        with pytest.raises(module.GeneratedClassesTypeError) as err_info:
            module.TestDefinition('string', None, -50)

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_number_property' was"
            " type 'str' but should be of type 'float'.")

        with pytest.raises(module.GeneratedClassesTypeError) as err_info:
            module.TestDefinition(200.5, None, 'string')

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_integer_property' was"
            " type 'str' but should be of type 'int'.")

    @staticmethod
    def test_not_number_setter(module):
        test_object = module.TestDefinition(200.5, None, -50)

        with pytest.raises(module.GeneratedClassesTypeError) as err_info:
            test_object.number_property = 'string'

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'number_property' was"
            " type 'str' but should be of type 'float' if defined.")

        with pytest.raises(module.GeneratedClassesTypeError) as err_info:
            test_object.integer_property = 'string'

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'integer_property' was"
            " type 'str' but should be of type 'int' if defined.")

    @staticmethod
    def test_minimum(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(200.5, 1.0, -50)

        message = err_info.value.message
        assert message == ("Invalid value for 'number_property', value was 1.0"
                           " but must be greater than or equal to 10.0.")

    @staticmethod
    def test_minimum_setter(module):
        test_object = module.TestDefinition(200.5, None, -50)

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.number_property = 1.0

        message = err_info.value.message
        assert message == ("Invalid value for 'number_property', value was 1.0"
                           " but must be greater than or equal to 10.0.")

    @staticmethod
    def test_maximum(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(200.5, 13.5, -50, 21)

        message = err_info.value.message
        assert message == ("Invalid value for 'integer_property', value was 21"
                           " but must be less than or equal to 20.")

    @staticmethod
    def test_maximum_setter(module):
        test_object = module.TestDefinition(200.5, None, -50, None)

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.integer_property = 21

        message = err_info.value.message
        assert message == ("Invalid value for 'integer_property', value was 21"
                           " but must be less than or equal to 20.")

    @staticmethod
    def test_exclusive_minimum(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(2.0, 13.5, -50)

        message = err_info.value.message
        assert message == ("Invalid value for 'required_number_property',"
                           " value was 2.0 but must be greater than 2.0.")

    @staticmethod
    def test_exclusive_minimum_setter(module):
        test_object = module.TestDefinition(200.5, None, -50)

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_number_property = 2.0

        message = err_info.value.message
        assert message == ("Invalid value for 'required_number_property',"
                           " value was 2.0 but must be greater than 2.0.")

    @staticmethod
    def test_exclusive_maximum(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(200.5, 13.5, 100)

        message = err_info.value.message
        assert message == ("Invalid value for 'required_integer_property',"
                           " value was 100 but must be less than 100.")

    @staticmethod
    def test_exclusive_maximum_setter(module):
        test_object = module.TestDefinition(200.5, None, -50)

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_integer_property = 100

        message = err_info.value.message
        assert message == ("Invalid value for 'required_integer_property',"
                           " value was 100 but must be less than 100.")


class TestTemplateObjectProperty:
    @staticmethod
    @pytest.fixture(scope='class')
    def schema_content():
        content = {
            'TestDefinition': {
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'requiredObjectProperty': {
                        'type': 'object',
                        "additionalProperties": False,
                    },
                    'booleanDictProperty': {
                        'type': 'object',
                        'additionalProperties': {
                            'type': 'boolean'
                        }
                    },
                    'numberDictProperty': {
                        'type': 'object',
                        'additionalProperties': {
                            'type': 'number'
                        }
                    },
                    'definedObjectProperty': {
                        'type': 'object',
                        'properties': {
                            'numberProperty': {
                                'type': 'number'
                            },
                            'stringProperty': {
                                'type': 'string'
                            },
                        },
                        'additionalProperties': False,
                        'required': ['numberProperty', 'stringProperty']
                    }
                },
                'required': ['requiredObjectProperty']
            }
        }
        return content

    @staticmethod
    def test_success(module):
        defined_object = module.TestDefinitionDefinedObjectProperty(
            number_property=1, string_property='str')
        test_object = module.TestDefinition(
            required_object_property={'key': defined_object},
            boolean_dict_property={'key': True},
            number_dict_property={
                'k0': 5.0,
                'k1': 3.14j
            },
            defined_object_property=defined_object)
        assert test_object.required_object_property == {'key': defined_object}
        assert test_object.boolean_dict_property == {'key': True}
        assert test_object.number_dict_property == {'k0': 5.0, 'k1': 3.14j}
        assert test_object.defined_object_property == defined_object

        test_dict = test_object.to_dict()
        assert test_dict == {
            'definedObjectProperty': {
                'numberProperty': 1,
                'stringProperty': 'str'
            },
            'numberDictProperty': {
                'k1': 3.14j,
                'k0': 5.0
            },
            'booleanDictProperty': {
                'key': True
            },
            'requiredObjectProperty': {
                'key': {
                    'numberProperty': 1,
                    'stringProperty': 'str'
                }
            }
        }
        from_dict_object = module.TestDefinition.from_dict(test_dict)
        assert test_object == from_dict_object

    @staticmethod
    def test_success_setter(module):
        defined_object = module.TestDefinitionDefinedObjectProperty(
            number_property=1, string_property='str')
        test_object = module.TestDefinition(required_object_property={})
        test_object.required_object_property = {'key': defined_object}
        test_object.boolean_dict_property = {'key': True}
        test_object.number_dict_property = {'k0': 5.0, 'k1': 3.14j}
        test_object.defined_object_property = defined_object

        assert test_object.required_object_property == {'key': defined_object}
        assert test_object.boolean_dict_property == {'key': True}
        assert test_object.number_dict_property == {'k0': 5.0, 'k1': 3.14j}
        assert test_object.defined_object_property == defined_object

        test_dict = test_object.to_dict()
        assert test_dict == {
            'definedObjectProperty': {
                'numberProperty': 1,
                'stringProperty': 'str'
            },
            'numberDictProperty': {
                'k1': 3.14j,
                'k0': 5.0
            },
            'booleanDictProperty': {
                'key': True
            },
            'requiredObjectProperty': {
                'key': {
                    'numberProperty': 1,
                    'stringProperty': 'str'
                }
            }
        }
        from_dict_object = module.TestDefinition.from_dict(test_dict)
        assert test_object == from_dict_object

    @staticmethod
    def test_required_param_missing(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition()

        message = err_info.value.message
        assert message == ("The required parameter 'required_object_property'"
                           " must not be 'None'.")

    @staticmethod
    def test_required_param_missing_setter(module):
        test_object = module.TestDefinition(
            required_object_property={'key': 'value'})

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_object_property = None

        message = err_info.value.message
        assert message == ("The required parameter 'required_object_property'"
                           " must not be 'None'.")

    @staticmethod
    def test_object_is_string(module):
        with pytest.raises(module.GeneratedClassesTypeError) as err_info:
            module.TestDefinition(required_object_property='not an object')

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_object_property' was type"
            " 'str' but should be of a dict with keys type 'basestring'.")

    @staticmethod
    def test_object_is_string_setter(module):
        test_object = module.TestDefinition(
            required_object_property={'key': 'value'})

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_object_property = 'not an object'

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_object_property' was type"
            " 'str' but should be of a dict with keys type 'basestring'.")

    @staticmethod
    def test_object_is_array(module):
        with pytest.raises(module.GeneratedClassesTypeError) as err_info:
            module.TestDefinition(
                required_object_property=['this', 'is', 'a', 'list'])

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_object_property' was type"
            " 'list' but should be of a dict with keys type 'basestring'.")

    @staticmethod
    def test_object_is_array_setter(module):
        test_object = module.TestDefinition(
            required_object_property={'key': 'value'})

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_object_property = ['this', 'is', 'a', 'list']

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_object_property' was type"
            " 'list' but should be of a dict with keys type 'basestring'.")

    @staticmethod
    def test_object_dict_with_bad_key_type(module):
        with pytest.raises(module.GeneratedClassesTypeError) as err_info:
            module.TestDefinition(required_object_property={
                'key': 'value',
                10: 11,
                True: 't'
            })

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_object_property' was a dict"
            " with keys of {type 'str', type 'int', type 'bool'} but should be"
            " of a dict with keys type 'basestring'.")

    @staticmethod
    def test_object_dict_with_bad_key_type_setter(module):
        test_object = module.TestDefinition(
            required_object_property={'key': 'value'})

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_object_property = {
                'key': 'value',
                10: 11,
                True: 't'
            }

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_object_property' was a dict"
            " with keys of {type 'str', type 'int', type 'bool'} but should be"
            " of a dict with keys type 'basestring'.")

    @staticmethod
    def test_semi_defined_dict_not_bool_value_type(module):
        with pytest.raises(module.GeneratedClassesTypeError) as err_info:
            module.TestDefinition(required_object_property={'key': 'value'},
                                  boolean_dict_property={'key': 'value'})

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'boolean_dict_property' was a"
            " dict of {type 'str':type 'str'} but should be of type 'dict of"
            " basestring:bool' if defined.")

    @staticmethod
    def test_semi_defined_dict_not_bool_value_type_setter(module):
        test_object = module.TestDefinition(
            required_object_property={'key': 'value'})

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.boolean_dict_property = {'key': 'value'}

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'boolean_dict_property' was a"
            " dict of {type 'str':type 'str'} but should be of type 'dict of"
            " basestring:bool' if defined.")

    @staticmethod
    def test_semi_defined_dict_not_number_value_type(module):
        with pytest.raises(module.GeneratedClassesTypeError) as err_info:
            module.TestDefinition(required_object_property={'key': 'value'},
                                  number_dict_property={'key': 'value'})

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'number_dict_property' was a"
            " dict of {type 'str':type 'str'} but should be of type 'dict of"
            " basestring:float' if defined.")

    @staticmethod
    def test_semi_defined_dict_not_number_value_type_setter(module):
        test_object = module.TestDefinition(
            required_object_property={'key': 'value'})

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.number_dict_property = {'key': 'value'}

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'number_dict_property' was a"
            " dict of {type 'str':type 'str'} but should be of type 'dict of"
            " basestring:float' if defined.")

    @staticmethod
    def test_internal_class_is_string(module):
        with pytest.raises(module.GeneratedClassesTypeError) as err_info:
            module.TestDefinition(required_object_property={'key': 'value'},
                                  defined_object_property='string')

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'defined_object_property' was type"
            " 'str' but should be of class"
            " '{}.TestDefinitionDefinedObjectProperty' if defined.".format(
                module.TestDefinitionDefinedObjectProperty.__module__))

    @staticmethod
    def test_internal_class_is_string_setter(module):
        test_object = module.TestDefinition(
            required_object_property={'key': 'value'})

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.defined_object_property = 'string'

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'defined_object_property' was type"
            " 'str' but should be of class"
            " '{}.TestDefinitionDefinedObjectProperty' if defined.".format(
                module.TestDefinitionDefinedObjectProperty.__module__))

    @staticmethod
    def test_internal_class_is_other_class(module):
        class TestOtherClass:
            pass

        with pytest.raises(module.GeneratedClassesTypeError) as err_info:
            module.TestDefinition(required_object_property={'key': 'value'},
                                  defined_object_property=TestOtherClass())

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'defined_object_property' was type"
            " 'instance' but should be of class"
            " '{}.TestDefinitionDefinedObjectProperty' if defined.".format(
                module.TestDefinitionDefinedObjectProperty.__module__))

    @staticmethod
    def test_internal_class_is_other_class_setter(module):
        class TestOtherClass:
            pass

        test_object = module.TestDefinition(
            required_object_property={'key': 'value'})

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.defined_object_property = TestOtherClass()

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'defined_object_property' was type"
            " 'instance' but should be of class"
            " '{}.TestDefinitionDefinedObjectProperty' if defined.".format(
                module.TestDefinitionDefinedObjectProperty.__module__))


class TestTemplateArrayProperty:
    @staticmethod
    @pytest.fixture(scope='class')
    def schema_content():
        content = {
            'TestDefinition': {
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'arrayProperty': {
                        'type': 'array'
                    },
                    'stringArrayProperty': {
                        'type': 'array',
                        'items': {
                            'type': 'string'
                        }
                    },
                    'requiredArrayProperty': {
                        'type': 'array',
                        'items': {
                            'type': 'number'
                        }
                    }
                },
                'required': ['requiredArrayProperty']
            }
        }
        return content

    @staticmethod
    def test_success(module):
        test_object = module.TestDefinition(
            array_property=['one', 2, True, [1, 2, 3]],
            string_array_property=['one', 'two', 'three'],
            required_array_property=[5.0, 1, -12])

        assert test_object.array_property == ['one', 2, True, [1, 2, 3]]
        assert test_object.string_array_property == ['one', 'two', 'three']
        assert test_object.required_array_property == [5.0, 1, -12]

        test_dict = test_object.to_dict()
        assert test_dict == {
            'requiredArrayProperty': [5.0, 1, -12],
            'arrayProperty': ['one', 2, True, [1, 2, 3]],
            'stringArrayProperty': ['one', 'two', 'three']
        }
        from_dict_object = module.TestDefinition.from_dict(test_dict)
        assert test_object == from_dict_object

    @staticmethod
    def test_success_setter(module):
        test_object = module.TestDefinition(required_array_property=[])
        test_object.array_property = ['one', 2, True, [1, 2, 3]]
        test_object.string_array_property = ['one', 'two', 'three']
        test_object.required_array_property = [5.0, 1, -12]

        assert test_object.array_property == ['one', 2, True, [1, 2, 3]]
        assert test_object.string_array_property == ['one', 'two', 'three']
        assert test_object.required_array_property == [5.0, 1, -12]

        test_dict = test_object.to_dict()
        assert test_dict == {
            'requiredArrayProperty': [5.0, 1, -12],
            'arrayProperty': ['one', 2, True, [1, 2, 3]],
            'stringArrayProperty': ['one', 'two', 'three']
        }
        from_dict_object = module.TestDefinition.from_dict(test_dict)
        assert test_object == from_dict_object

    @staticmethod
    def test_required_param_missing(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition()

        message = err_info.value.message
        assert message == ("The required parameter 'required_array_property'"
                           " must not be 'None'.")

    @staticmethod
    def test_required_param_missing_setter(module):
        test_object = module.TestDefinition(required_array_property=[])

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_array_property = None

        message = err_info.value.message
        assert message == ("The required parameter 'required_array_property'"
                           " must not be 'None'.")

    @staticmethod
    def test_array_is_string(module):
        with pytest.raises(module.GeneratedClassesTypeError) as err_info:
            module.TestDefinition(required_array_property='not an array')

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_array_property' was type"
            " 'str' but should be of type 'list of float'.")

    @staticmethod
    def test_array_is_string_setter(module):
        test_object = module.TestDefinition(required_array_property=[])

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_array_property = 'not an object'

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_array_property' was type"
            " 'str' but should be of type 'list of float'.")

    @staticmethod
    def test_array_is_object(module):
        with pytest.raises(module.GeneratedClassesTypeError) as err_info:
            module.TestDefinition(array_property={
                'this': 'is',
                'a': 'dict'
            },
                                  required_array_property=[])

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'array_property' was type"
            " 'dict' but should be of type 'list' if defined.")

    @staticmethod
    def test_array_is_object_setter(module):
        test_object = module.TestDefinition(required_array_property=[])

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.array_property = {'this': 'is', 'a': 'dict'}

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'array_property' was type"
            " 'dict' but should be of type 'list' if defined.")

    @staticmethod
    def test_number_array_wrong_elem_types(module):
        with pytest.raises(module.GeneratedClassesTypeError) as err_info:
            module.TestDefinition(required_array_property=['one', True])

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_array_property' was a list"
            " of [type 'str', type 'bool'] but should be of type 'list of"
            " float'.")

    @staticmethod
    def test_number_array_wrong_elem_types_setter(module):
        test_object = module.TestDefinition(required_array_property=[])

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_array_property = ['one', True]

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_array_property' was a list"
            " of [type 'str', type 'bool'] but should be of type 'list of"
            " float'.")

    @staticmethod
    def test_string_array_wrong_elem_types(module):
        with pytest.raises(module.GeneratedClassesTypeError) as err_info:
            module.TestDefinition(string_array_property=['one', 2, 3.0],
                                  required_array_property=[])

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'string_array_property' was a list of"
            " [type 'str', type 'int', type 'float'] but should be of type"
            " 'list of basestring' if defined.")

    @staticmethod
    def test_string_array_wrong_elem_types_setter(module):
        test_object = module.TestDefinition(required_array_property=[])

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.string_array_property = ['one', 2, 3.0]

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'string_array_property' was a list of"
            " [type 'str', type 'int', type 'float'] but should be of type"
            " 'list of basestring' if defined.")


class TestTemplateBooleanProperty:
    @staticmethod
    @pytest.fixture(scope='class')
    def schema_content():
        content = {
            'TestDefinition': {
                'type': 'object',
                'additionalProperties': False,
                'properties': {
                    'booleanProperty': {
                        'type': 'boolean'
                    },
                    'requiredBooleanProperty': {
                        'type': 'boolean'
                    },
                },
                'required': ['requiredBooleanProperty']
            }
        }
        return content

    @staticmethod
    def test_success(module):
        test_object = module.TestDefinition(boolean_property=True,
                                            required_boolean_property=False)

        assert test_object.boolean_property
        assert not test_object.required_boolean_property

        test_dict = test_object.to_dict()
        assert test_dict == {
            'booleanProperty': True,
            'requiredBooleanProperty': False
        }
        from_dict_object = module.TestDefinition.from_dict(test_dict)
        assert test_object == from_dict_object

    @staticmethod
    def test_success_setter(module):
        test_object = module.TestDefinition(required_boolean_property=True)
        test_object.boolean_property = True
        test_object.required_boolean_property = False

        assert test_object.boolean_property
        assert not test_object.required_boolean_property

        test_dict = test_object.to_dict()
        assert test_dict == {
            'booleanProperty': True,
            'requiredBooleanProperty': False
        }
        from_dict_object = module.TestDefinition.from_dict(test_dict)
        assert test_object == from_dict_object

    @staticmethod
    def test_required_param_missing(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition()

        message = err_info.value.message
        assert message == ("The required parameter 'required_boolean_property'"
                           " must not be 'None'.")

    @staticmethod
    def test_required_param_missing_setter(module):
        test_object = module.TestDefinition(required_boolean_property=False)

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_boolean_property = None

        message = err_info.value.message
        assert message == ("The required parameter 'required_boolean_property'"
                           " must not be 'None'.")

    @staticmethod
    def test_boolean_is_string(module):
        with pytest.raises(module.GeneratedClassesTypeError) as err_info:
            module.TestDefinition(required_boolean_property='not an array')

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_boolean_property' was type"
            " 'str' but should be of type 'bool'.")

    @staticmethod
    def test_boolean_is_string_setter(module):
        test_object = module.TestDefinition(required_boolean_property=False)

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_boolean_property = 'not an object'

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_boolean_property' was type"
            " 'str' but should be of type 'bool'.")


class TestTemplateEnumProperty:
    @staticmethod
    @pytest.fixture(scope='class')
    def schema_content():
        content = {
            'TestDefinition': {
                'type':
                'object',
                'additionalProperties':
                False,
                'properties': {
                    'requiredStringProperty': {
                        'type': 'string',
                        'enum': ['A', 'B', 'C']
                    },
                    'stringProperty': {
                        'type': 'string',
                        'enum': ['A', 'B', 'C']
                    },
                    'requiredObjectProperty': {
                        'type': 'object',
                        'additionalProperties': {
                            'type': 'string',
                            'enum': ['ONE', 'TWO', 'THREE']
                        }
                    },
                    'objectProperty': {
                        'type': 'object',
                        'additionalProperties': {
                            'type': 'string',
                            'enum': ['ONE', 'TWO', 'THREE']
                        }
                    },
                    'requiredArrayProperty': {
                        'type': 'array',
                        'items': {
                            'type': 'string',
                            'enum': ['DO', 'RE', 'MI']
                        }
                    },
                    'arrayProperty': {
                        'type': 'array',
                        'items': {
                            'type': 'string',
                            'enum': ['DO', 'RE', 'MI']
                        }
                    }
                },
                'required': [
                    'requiredStringProperty', 'requiredObjectProperty',
                    'requiredArrayProperty'
                ]
            }
        }
        return content

    @staticmethod
    def test_successs(module):
        test_object = module.TestDefinition(
            required_string_property='A',
            required_object_property={
                'ONE': 'uno',
                'TWO': 'dos'
            },
            required_array_property=['DO', 'RE', 'MI'])
        assert test_object.required_string_property == 'A'
        assert test_object.required_object_property == {
            'ONE': 'uno',
            'TWO': 'dos'
        }
        assert test_object.required_array_property == ['DO', 'RE', 'MI']

        test_dict = test_object.to_dict()
        assert test_dict == {
            'requiredStringProperty': 'A',
            'stringProperty': None,
            'requiredObjectProperty': {
                'TWO': 'dos',
                'ONE': 'uno'
            },
            'objectProperty': None,
            'requiredArrayProperty': ['DO', 'RE', 'MI'],
            'arrayProperty': None
        }
        from_dict_object = module.TestDefinition.from_dict(test_dict)
        assert test_object == from_dict_object

    @staticmethod
    def test_successs_setter(module):
        test_object = module.TestDefinition(required_string_property='B',
                                            required_object_property={},
                                            required_array_property=[])
        test_object.required_string_property = 'A'
        test_object.required_object_property = {'ONE': 'uno', 'TWO': 'dos'}
        test_object.required_array_property = ['DO', 'RE', 'MI']

        assert test_object.required_string_property == 'A'
        assert test_object.required_object_property == {
            'ONE': 'uno',
            'TWO': 'dos'
        }
        assert test_object.required_array_property == ['DO', 'RE', 'MI']

        test_dict = test_object.to_dict()
        assert test_dict == {
            'requiredStringProperty': 'A',
            'stringProperty': None,
            'requiredObjectProperty': {
                'TWO': 'dos',
                'ONE': 'uno'
            },
            'objectProperty': None,
            'requiredArrayProperty': ['DO', 'RE', 'MI'],
            'arrayProperty': None
        }
        from_dict_object = module.TestDefinition.from_dict(test_dict)
        assert test_object == from_dict_object

    @staticmethod
    def test_required_string_incorrect_enum(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(required_string_property='D',
                                  required_object_property={},
                                  required_array_property=[])

        message = err_info.value.message
        assert message == (
            "Invalid enum value D for 'required_string_property', must be one"
            " of [A, B, C].")

    @staticmethod
    def test_required_string_incorrect_enum_setter(module):
        test_object = module.TestDefinition(required_string_property='B',
                                            required_object_property={},
                                            required_array_property=[])

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_string_property = 'D'

        message = err_info.value.message
        assert message == (
            "Invalid enum value D for 'required_string_property', must be one"
            " of [A, B, C].")

    @staticmethod
    def test_required_string_not_string(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(required_string_property=1000,
                                  required_object_property={},
                                  required_array_property=[])

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_string_property' was type"
            " 'int' but should be of type 'basestring'.")

    @staticmethod
    def test_required_string_not_string_setter(module):
        test_object = module.TestDefinition(required_string_property='B',
                                            required_object_property={},
                                            required_array_property=[])

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_string_property = 1000

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_string_property' was type"
            " 'int' but should be of type 'basestring'.")

    @staticmethod
    def test_string_incorrect_enum(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(required_string_property='B',
                                  string_property='D',
                                  required_object_property={},
                                  required_array_property=[])

        message = err_info.value.message
        assert message == (
            "Invalid enum value D for 'string_property', must be one"
            " of [A, B, C] if defined.")

    @staticmethod
    def test_string_incorrect_enum_setter(module):
        test_object = module.TestDefinition(required_string_property='B',
                                            required_object_property={},
                                            required_array_property=[])

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.string_property = 'D'

        message = err_info.value.message
        assert message == ("Invalid enum value D for 'string_property', must"
                           " be one of [A, B, C] if defined.")

    @staticmethod
    def test_string_not_string(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(required_string_property='B',
                                  string_property=1000,
                                  required_object_property={},
                                  required_array_property=[])

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'string_property' was type 'int' but"
            " should be of type 'basestring' if defined.")

    @staticmethod
    def test_string_not_string_setter(module):
        test_object = module.TestDefinition(required_string_property='B',
                                            required_object_property={},
                                            required_array_property=[])

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.string_property = 1000

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'string_property' was type 'int' but"
            " should be of type 'basestring' if defined.")

    @staticmethod
    def test_required_object_incorrect_enum(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(required_string_property='B',
                                  required_object_property={'FOUR': 'cuatro'},
                                  required_array_property=[])

        message = err_info.value.message
        assert message == (
            "Invalid keys in 'required_object_property'. Was [FOUR] but"
            " must be a subset of [ONE, TWO, THREE].")

    @staticmethod
    def test_required_object_incorrect_enum_setter(module):
        test_object = module.TestDefinition(required_string_property='B',
                                            required_object_property={},
                                            required_array_property=[])

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_object_property = {'FOUR': 'cuatro'}

        message = err_info.value.message
        assert message == (
            "Invalid keys in 'required_object_property'. Was [FOUR] but"
            " must be a subset of [ONE, TWO, THREE].")

    @staticmethod
    def test_required_object_not_object(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(required_string_property='B',
                                  required_object_property='FOUR',
                                  required_array_property=[])

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_object_property' was type"
            " 'str' but should be of a dict with keys type 'basestring'.")

    @staticmethod
    def test_required_object_not_object_setter(module):
        test_object = module.TestDefinition(required_string_property='B',
                                            required_object_property={},
                                            required_array_property=[])

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_object_property = 'FOUR'

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_object_property' was type"
            " 'str' but should be of a dict with keys type 'basestring'.")

    @staticmethod
    def test_object_incorrect_enum(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(required_string_property='B',
                                  required_object_property={},
                                  object_property={'FOUR': 'cuatro'},
                                  required_array_property=[])

        message = err_info.value.message
        assert message == (
            "Invalid keys in 'object_property'. Was [FOUR] but"
            " must be a subset of [ONE, TWO, THREE] if defined.")

    @staticmethod
    def test_object_incorrect_enum_setter(module):
        test_object = module.TestDefinition(required_string_property='B',
                                            required_object_property={},
                                            required_array_property=[])

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.object_property = {'FOUR': 'cuatro'}

        message = err_info.value.message
        assert message == (
            "Invalid keys in 'object_property'. Was [FOUR] but"
            " must be a subset of [ONE, TWO, THREE] if defined.")

    @staticmethod
    def test_object_not_object(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(required_string_property='B',
                                  required_object_property={},
                                  object_property='THREE',
                                  required_array_property=[])

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'object_property' was type 'str' but"
            " should be of a dict with keys type 'basestring' if defined.")

    @staticmethod
    def test_object_not_object_setter(module):
        test_object = module.TestDefinition(required_string_property='B',
                                            required_object_property={},
                                            required_array_property=[])

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.object_property = 'THREE'

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'object_property' was type 'str' but"
            " should be of a dict with keys type 'basestring' if defined.")

    @staticmethod
    def test_required_array_incorrect_enum(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(required_string_property='B',
                                  required_object_property={},
                                  required_array_property=['FA', 'SO'])

        message = err_info.value.message
        assert message == (
            "Invalid values for 'required_array_property'. Was [FA, SO]"
            " but must be a subset of [DO, RE, MI].")

    @staticmethod
    def test_required_array_incorrect_enum_setter(module):
        test_object = module.TestDefinition(required_string_property='B',
                                            required_object_property={},
                                            required_array_property=[])

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_array_property = ['FA', 'SO']

        message = err_info.value.message
        assert message == (
            "Invalid values for 'required_array_property'. Was [FA, SO]"
            " but must be a subset of [DO, RE, MI].")

    @staticmethod
    def test_required_array_not_array(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(required_string_property='B',
                                  required_object_property={},
                                  required_array_property='MI')

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_array_property' was type"
            " 'str' but should be of type 'list of basestring'.")

    @staticmethod
    def test_required_array_not_array_setter(module):
        test_object = module.TestDefinition(required_string_property='B',
                                            required_object_property={},
                                            required_array_property=[])

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.required_array_property = 'MI'

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'required_array_property' was type"
            " 'str' but should be of type 'list of basestring'.")

    @staticmethod
    def test_array_incorrect_enum(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(required_string_property='B',
                                  required_object_property={},
                                  required_array_property=[],
                                  array_property=['FA', 'SO'])

        message = err_info.value.message
        assert message == ("Invalid values for 'array_property'. Was [FA, SO]"
                           " but must be a subset of [DO, RE, MI] if defined.")

    @staticmethod
    def test_array_incorrect_enum_setter(module):
        test_object = module.TestDefinition(required_string_property='B',
                                            required_object_property={},
                                            required_array_property=[])

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.array_property = ['FA', 'SO']

        message = err_info.value.message
        assert message == ("Invalid values for 'array_property'. Was [FA, SO]"
                           " but must be a subset of [DO, RE, MI] if defined.")

    @staticmethod
    def test_array_not_array(module):
        with pytest.raises(module.GeneratedClassesError) as err_info:
            module.TestDefinition(required_string_property='B',
                                  required_object_property={},
                                  required_array_property=[],
                                  array_property='MI')

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'array_property' was type 'str' but"
            " should be of type 'list of basestring' if defined.")

    @staticmethod
    def test_array_not_array_setter(module):
        test_object = module.TestDefinition(required_string_property='B',
                                            required_object_property={},
                                            required_array_property=[])

        with pytest.raises(module.GeneratedClassesError) as err_info:
            test_object.array_property = 'MI'

        message = err_info.value.message
        assert message == (
            "TestDefinition's parameter 'array_property' was type 'str' but"
            " should be of type 'list of basestring' if defined.")
