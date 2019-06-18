import datetime
import pydoc
import re

import six


def convert_type(type_string):
    """Coverts the typing version of the type to the basic python type (list or
        dict)

    :param type_string:
    :type type_string: str
    :return: type
    """
    if type_string.startswith('List'):
        return list
    elif type_string.startswith('Dict'):
        return dict
    else:
        raise ValueError('The converted types should only be Dict or List')


def get_contained_type(type_string):
    """get the type contained in the List/Dict. If it's a Dict we want to
    return the value's type since the key has to be str.

    :param type_string:
    :type type_string: str
    :return: type
    """
    patterns = [r'List\[(\w+)\]', r'Dict\[\w+, (\w+)\]']
    for pattern in patterns:
        match = re.search(pattern, type_string)
        if match and match.group(1) != 'ERRORUNKNOWN':
            # Convert the type to basestring here.
            if match.group(1) == 'str':
                return basestring
            return pydoc.locate(match.group(1))
    return None


def deserialize_model(data, klass):
    """Deserializes list or dict to model.

    :param data: dict, list.
    :type data: dict | list
    :param klass: class literal.
    :return: model object.
    """
    instance = klass(validate=False)

    if not instance.swagger_types:
        return data

    for attr, attr_type in six.iteritems(instance.swagger_types):
        if (data is not None and instance.attribute_map[attr] in data
                and isinstance(data, dict)):
            value = data[instance.attribute_map[attr]]
            setattr(instance, attr, _deserialize(value, attr_type))

    return instance


def _deserialize(data, klass):
    """Deserializes dict, list, str into an object.

    :param data: dict, list or str.
    :param klass: class literal, or string of class name.

    :return: object.
    """
    if data is None:
        return None

    if issubclass(klass, (int, float, long, complex, basestring, bool)):
        return _deserialize_primitive(data, klass)
    elif klass == datetime.date:
        return deserialize_date(data)
    elif klass == datetime.datetime:
        return deserialize_datetime(data)
    elif klass == list:
        return _deserialize_list(data)
    elif klass == dict or klass == object:
        return _deserialize_dict(data)
    else:
        return deserialize_model(data, klass)


def _deserialize_primitive(data, klass):
    """Deserializes to primitive type.

    :param data: data to deserialize.
    :param klass: class literal.

    :return: int, float, long, complex, basestring, bool.
    :rtype: int | float | long | complex | basestring | bool
    """
    try:
        value = klass(data)
    except UnicodeEncodeError:
        if isinstance(data, str):
            #
            # Ignore errors even if the string is not proper UTF-8 or has
            # broken marker bytes. The builtin  unicode function can do this.
            #
            value = unicode(data, 'utf-8', errors='ignore')
        else:
            # Assume the value object has proper __unicode__() method.
            value = unicode(data)
    except TypeError:
        value = data
    return value


def deserialize_date(string):
    """Deserializes string to date.

    :param string: str.
    :type string: str
    :return: date.
    :rtype: date
    """
    try:
        from dateutil.parser import parse
        return parse(string).date()
    except ImportError:
        return string


def deserialize_datetime(string):
    """Deserializes string to datetime.

    The string should be in iso8601 datetime format.

    :param string: str.
    :type string: str
    :return: datetime.
    :rtype: datetime
    """
    try:
        from dateutil.parser import parse
        return parse(string)
    except ImportError:
        return string


def _deserialize_list(data):
    """Deserializes a list and its elements.

    :param data: list to deserialize.
    :type data: list

    :return: deserialized list.
    :rtype: list
    """
    return [_deserialize(sub_data, type(sub_data)) for sub_data in data]


def _deserialize_dict(data):
    """Deserializes a dict and its elements.

    :param data: dict to deserialize.
    :type data: dict

    :return: deserialized dict.
    :rtype: dict
    """
    return {k: _deserialize(v, type(v)) for k, v in six.iteritems(data)}
