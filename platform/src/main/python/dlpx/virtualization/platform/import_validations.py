#
# Copyright (c) 2020 by Delphix. All rights reserved.
#
import inspect

from dlpx.virtualization.platform import exceptions
from dlpx.virtualization.platform.import_util import (import_check,
                                                      post_import_check)


@import_check(ordinal=1)
def validate_module_content(plugin_module):
    # This should never happen and if it does, flag an error.
    if plugin_module.module_content is None:
        raise exceptions.IncorrectPluginCodeError(
            'Plugin module content is None.')


@import_check(ordinal=2)
def validate_entry_point(plugin_module):
    #
    # Schema validation on plugin config file would have ensured entry is a
    # string and should never be none - so raise an error if it does.
    #
    if plugin_module.entry_point is None:
        raise exceptions.IncorrectPluginCodeError(
            'Plugin entry point object is None.')

    if not hasattr(plugin_module.module_content, plugin_module.entry_point):
        raise exceptions.UserError(
            'Entry point \'{}:{}\' does not exist. \'{}\' is not a symbol'
            ' in module \'{}\'.'.format(plugin_module.module,
                                        plugin_module.entry_point,
                                        plugin_module.entry_point,
                                        plugin_module.module))


@import_check(ordinal=3)
def validate_plugin_object(plugin_module):
    plugin_object = getattr(plugin_module.module_content,
                            plugin_module.entry_point, None)

    if plugin_object is None:
        raise exceptions.UserError('Plugin object retrieved from the entry'
                                   ' point {} is None'.format(
                                       plugin_module.entry_point))


@post_import_check(ordinal=1)
def validate_named_args(plugin_module):
    """
    Does named argument validation based on the plugin type.
    """
    warnings = []

    if plugin_module.validate_args:

        #
        # Validated methods args against expected args and return any
        # resulting warnings to the caller to process.
        # These warnings should be treated as an exception to make
        # sure build fails.
        #

        plugin_object = getattr(plugin_module.module_content,
                                plugin_module.entry_point)

        # Iterate over attributes objects of the Plugin object
        for plugin_attrib in plugin_object.__dict__.values():
            #
            # For each plugin attribute object, its __dict__.keys will give
            # us the name of the plugin implemntation method name. That name
            # is useful in looking up named arguments expected and what is
            # actually in the plugin code. And plugin_op_type can be, for e.g.
            # LinkedOperations, DiscoveryOperations, VirtualOperations
            #
            plugin_op_type = plugin_attrib.__class__.__name__

            # UpgradeOperations are validated differently, so ignore.
            if plugin_op_type == 'UpgradeOperations':
                continue

            for op_name_key, op_name in plugin_attrib.__dict__.items():
                if op_name is None:
                    continue
                actual_args = inspect.getargspec(op_name)
                warnings.extend(
                    _check_args(method_name=op_name.__name__,
                                expected_args=_lookup_expected_args(
                                    plugin_module, plugin_op_type,
                                    op_name_key),
                                actual_args=actual_args.args))

    return warnings


@post_import_check(ordinal=2)
def check_upgrade_operations(plugin_module):
    """
    Does named argument validation on UpgradeOperations.
    """
    warnings = []

    if plugin_module.validate_args:

        #
        # Validated methods args against expected args and return any
        # resulting warnings to the caller to process.
        # These warnings should be treated as an exception to make
        # sure build fails.
        #

        plugin_object = getattr(plugin_module.module_content,
                                plugin_module.entry_point)

        # Iterate over attributes objects of the Plugin object
        for plugin_attrib in plugin_object.__dict__.values():
            #
            # For each plugin attribute object, its __dict__.keys will give
            # us the name of the plugin implemntation method name. That name
            # is useful in looking up named arguments expected and what is
            # actually in the plugin code. And plugin_op_type can be, for e.g.
            # LinkedOperations, DiscoveryOperations, VirtualOperations
            #
            plugin_op_type = plugin_attrib.__class__.__name__

            if plugin_op_type != 'UpgradeOperations':
                continue

            warnings.extend(
                _check_upgrade_args(plugin_attrib,
                                    plugin_module.expected_upgrade_args))

    return warnings


def _check_upgrade_args(upgrade_operations, expected_upgrade_args):
    """
    This function does named argument validation of all migration functions by
    first looping through each of the migration helpers (platform_migrations
    and lua_migrations) then looping through all those attributes.
    Any attributes that are not dictionaries that map migration_id ->
    upgrade_function are skipped. We then loop through every key/value pair
    of each of the dictionaries and validate that the argument in the defined
    function has the expected name.
    """
    warnings = []

    for migration_helper in vars(upgrade_operations).values():
        # Next we must loop through each of the attributes (Should be just two)
        for attribute_name, attribute in vars(migration_helper).items():
            if attribute_name not in expected_upgrade_args.keys():
                # Skip if not in one of the operation dictionaries.
                continue
            #
            # If the attribute_name was in the expected upgrade dicts then we
            # know it is a dict containing migration id -> upgrade function
            # that we can iterate on.
            #
            for migration_func in attribute.values():
                actual = inspect.getargspec(migration_func).args
                expected = expected_upgrade_args[attribute_name]
                warnings.extend(
                    _check_args(method_name=migration_func.__name__,
                                expected_args=expected,
                                actual_args=actual))

    return warnings


def _check_args(method_name, expected_args, actual_args):
    warnings = []

    if len(expected_args) != len(actual_args):
        warnings.append('Number of arguments do not match in method {}.'
                        ' Expected: {}, Found: {}.'.format(
                            method_name, list(expected_args), actual_args))

    if not all(arg in expected_args for arg in actual_args):
        warnings.append('Named argument mismatch in method {}.'
                        ' Expected: {}, Found: {}.'.format(
                            method_name, list(expected_args), actual_args))

    return warnings


def _lookup_expected_args(plugin_module, plugin_op_type, plugin_op_name):
    if plugin_module.plugin_type == 'DIRECT':
        return plugin_module.expected_direct_args_by_op[plugin_op_type][
            plugin_op_name]
    else:
        return plugin_module.expected_staged_args_by_op[plugin_op_type][
            plugin_op_name]
