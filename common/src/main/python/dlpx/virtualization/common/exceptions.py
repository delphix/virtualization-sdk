#
# Copyright (c) 2019 by Delphix. All rights reserved.
#


class PlatformError(Exception):
    """This error should be converted and thrown as a Delphix Fatal exception
    if it gets converted through protobuf.

    Some Platform specific errors (operations not implemented errors,
    specifically) should have been validated already and points to a Delphix
    Engine bug.

    Args:
        message (str): A user-readable message describing the exception.

    Attributes:
        message (str): A user-readable message describing the exception.
    """

    @property
    def message(self):
        return self.args[0]

    def __init__(self, message):
        super(PlatformError, self).__init__(message)


class PluginRuntimeError(Exception):
    """Plugin-catchable exception

    Some Plugin specific errors (type errors, etc.) need to be fixed via the
    plugin code. Potentially actionable by plugin code.

    This exception will be thrown whenever a Platform call fails due to such an
    actionable error.

    Args:
        message (str): A user-readable message describing the exception.

    Attributes:
        message (str): A user-readable message describing the exception.
    """

    @property
    def message(self):
        return self.args[0]

    def __init__(self, message):
        super(PluginRuntimeError, self).__init__(message)

    @staticmethod
    def get_actual_and_expected_type(actual_type, expected_type):
        """ Takes in the the actual and expected types and generates a tuple of
        two strings that are then used to generate the output message.

        Args:
            actual_type (Type, List[Type], Set[Type],
                        or Set[Tuple[Type, Type]]):
            type(s) that was actually passed in for the parameter. This will
            either take the type and make it a str or join the types as a
            string and put it in brackets.
            expected_type (Type, List[Type], List[Type1, Type2], or
            Dict[Type, Type]):
            The type of the parameter that was expected. Or if this is a
            container then we either assume there is one element in it and that
            type is the expected type of the container, or if the list contains
            multiple types, then multiple types are expected.
            ie: if expected_type = [str] then the returned expected string with
            be something like "type 'list of str'"

        Returns:
            tuple (str, str): the actual and expected strings used for the
            types.
        """
        def _remove_angle_brackets(type_string):
            return type_string.replace('<', '').replace('>', '')

        def _get_type_name(type_object):
            if type_object.__module__ != '__builtin__':
                type_name = '{}.{}'.format(
                    type_object.__module__, type_object.__name__)
            else:
                type_name = type_object.__name__
            return type_name

        if isinstance(expected_type, list):
            """
            If expected_type length is greater than 1, we can
            expect 2 cases. Either the list has all the same types
            (violating the assumption that there is one element in the
            list, and that type is the expected type of the container)
            or the list has types that are unique to each other, meaning that
            multiple types were expected, any one of which are allowed.
            """
            if len(expected_type) != 1 and len(set(expected_type)) == 1:
                raise PlatformError('The thrown TypeError should have had a'
                                    ' list of size 1 as the expected_type')
            if len(expected_type) > 1:
                for index in range(0, len(expected_type)):
                    expected_type[index] = _get_type_name(expected_type[index])
                    expected_type[index] = _remove_angle_brackets(str(expected_type[index]))

                expected = "any one of the following types: '{}'".format(expected_type)
            else:
                single_type = expected_type[0]
                type_name = _get_type_name(single_type)

                expected = "type 'list of {}'".format(type_name)
        elif isinstance(expected_type, dict):
            if len(expected_type) != 1:
                raise PlatformError('The thrown TypeError should have had a'
                                    ' dict of size 1 as the expected_type')

            key_type = expected_type.keys()[0]
            value_type = expected_type.values()[0]

            key_type_name = _get_type_name(key_type)
            value_type_name = _get_type_name(value_type)

            expected = "type 'dict of {}:{}'".format(
                key_type_name, value_type_name)

        else:
            expected = _remove_angle_brackets(str(expected_type))

        if isinstance(actual_type, list):
            actual = 'a list of [{}]'.format(
                ', '.join(_remove_angle_brackets(str(single_type))
                          for single_type in actual_type))
        elif isinstance(actual_type, set):
            #
            # If it's a set, validate that it is a set of tuples. We couldn't
            # just pass in a dict because keys have to be unique. and we don't
            # need that for the types.
            #
            if (not all(isinstance(type_tuple, tuple)
                        for type_tuple in actual_type)):
                raise PlatformError('The thrown TypeError should have had a'
                                    ' set of tuples to represent a dict')
            actual = 'a dict of {{{}}}'.format(', '.join(['{0}:{1}'.format(
                    _remove_angle_brackets(str(k)),
                _remove_angle_brackets(str(v))) for k, v in actual_type]))
        else:
            actual = _remove_angle_brackets(str(actual_type))

        return actual, expected


class IncorrectTypeError(PluginRuntimeError):
    """IncorrectTypeError gets thrown when defined plugin class's parameter
     has an incorrect type.

    Args:
        object (class): the class object being initialized
        parameter_name (str): The name of the param being passed in
        actual type (Type or List[Type]): type(s) that was actually passed in
            for the parameter
        expected_type (Type): The type of the parameter that is expected.
        required (bool): If the parameter is required (doesn't have a default)

    Attributes:
        message (str): A user-readable message describing the exception.
    """

    def __init__(
        self,
        object_type,
        parameter_name,
        actual_type,
        expected_type,
        required=True):
        actual, expected = self.get_actual_and_expected_type(
            actual_type, expected_type)

        message = ("{}'s parameter '{}' was {} but should be of {}{}.".format(
            object_type.__name__,
            parameter_name,
            actual,
            expected,
            (' if defined', '')[required]))
        super(IncorrectTypeError, self).__init__(message)