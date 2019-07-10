#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
import importlib
import inspect
import logging
import os
import sys
from collections import defaultdict
from multiprocessing import Process, Queue

import yaml
from dlpx.virtualization._internal import exceptions, util_classes
from dlpx.virtualization._internal.codegen import CODEGEN_PACKAGE
from dlpx.virtualization._internal.util_classes import MessageUtils
from flake8.api import legacy as flake8

logger = logging.getLogger(__name__)

PLUGIN_IMPORTER_YAML = os.path.join(util_classes.PLUGIN_SCHEMAS_DIR,
                                    'plugin_importer.yaml')


def load_validation_maps():
    """
    Reads a plugin config file and raises UserError if there is an issue
    reading the file.
    """
    with open(PLUGIN_IMPORTER_YAML, 'rb') as f:
        return yaml.safe_load(f)


class PluginImporter:
    """
    Import helper class for the plugin. Imports the plugin module in a sub
    process to ensure its isolated and does not pollute caller's runtime.
    On successful import, callers can get the manifest describing what
    methods are implemented in the plugin code. If import fails or has
    issues with validation of module content and entry points- will save
    errors/warnings in a dict that callers can access.
    """
    validation_maps = load_validation_maps()
    expected_staged_args_by_op = validation_maps['EXPECTED_STAGED_ARGS_BY_OP']
    expected_direct_args_by_op = validation_maps['EXPECTED_DIRECT_ARGS_BY_OP']
    required_methods_by_plugin_type = \
        validation_maps['REQUIRED_METHODS_BY_PLUGIN_TYPE']
    required_methods_description = \
        validation_maps['REQUIRED_METHODS_DESCRIPTION']

    def __init__(self,
                 src_dir,
                 module,
                 entry_point,
                 plugin_type,
                 validate=False):
        self.__src_dir = src_dir
        self.__plugin_module = module
        self.__plugin_entry_point = entry_point
        self.__plugin_type = plugin_type
        self.__validate = validate

    def import_plugin(self):
        """
        Imports the plugin module, does basic validation.
        Returns:
            plugin manifest - dict describing methods implemented in the plugin
        Note:
            warnings - dict containing a list of errors or warnings can be
            obtained by the caller via warnings property.
        """
        logger.debug('Importing plugin module : %s', self.__plugin_module)

        self.__pre_import_checks()
        plugin_manifest, warnings = self.__import_plugin()
        self.__post_import_checks(plugin_manifest, warnings)

        return plugin_manifest, warnings

    def __pre_import_checks(self):
        """
        Performs checks of the plugin code that should take place prior to
        importing.
        """
        warnings = PluginImporter.__check_for_undefined_names(self.__src_dir)
        PluginImporter.__report_warnings_and_exceptions(warnings)

    def __import_plugin(self):
        """
        Imports the module to check for errors or issues. Also does an eval on
        the entry point.
        """
        plugin_manifest = {}
        warnings = defaultdict(list)
        try:
            plugin_manifest, warnings = (PluginImporter.__import_in_subprocess(
                self.__src_dir, self.__plugin_module,
                self.__plugin_entry_point, self.__plugin_type,
                self.__validate))
        except ImportError as err:
            exception_msg = ('Unable to load module \'{}\' specified in '
                             'pluginEntryPoint \'{}\' from path \'{}\' '
                             'Error message: {}'.format(
                                 self.__plugin_module,
                                 self.__plugin_entry_point, self.__src_dir,
                                 err))
            warnings['exception'].append(exception_msg)

        return plugin_manifest, warnings

    def __post_import_checks(self, plugin_manifest, warnings):
        """
        Performs checks of the plugin code that should take place after
        importing.
        """
        check_warnings = self.__check_for_required_methods(
            plugin_manifest, self.__plugin_type)

        if check_warnings and 'warning' in check_warnings:
            warnings['warning'].extend(check_warnings['warning'])

        self.__report_warnings_and_exceptions(warnings)

    @staticmethod
    def __check_for_required_methods(plugin_manifest, plugin_type):
        """
        Checks for required methods in the manifest and adds warnings for any
        missing methods.
        """
        warnings = defaultdict(list)
        if not plugin_manifest:
            return warnings
        for method_key, method_name in \
                PluginImporter.required_methods_by_plugin_type[
                plugin_type].items():
            if plugin_manifest[method_key] is False:
                warnings['warning'].append(
                    'Implementation missing '
                    'for required method {}. The Plugin Operation \'{}\' '
                    'will fail when executed.'.format(
                        method_name, PluginImporter.
                        required_methods_description[method_key]))
        return warnings

    @staticmethod
    def __import_in_subprocess(src_dir, module, entry_point, plugin_type,
                               validate):
        """
        Imports the given python module in a sub process.
        NOTE:
            Importing module in the current context pollutes the runtime of
            the caller, in this case dvp. If the module being imported, for
            e.g. contains code that adds a handler to the root logger at
            import time, this can cause issues with logging in this code and
            callers of importer. To avoid such issues, perform the import in
            in a sub-process and on completion return the output.
        """
        queue = Queue()
        process = Process(target=_get_manifest,
                          args=(queue, src_dir, module, entry_point,
                                plugin_type, validate))
        process.start()
        process.join()
        manifest, warnings = PluginImporter.__parse_queue(queue)
        return manifest, warnings

    @staticmethod
    def __parse_queue(queue):
        manifest = {}
        warnings = defaultdict(list)
        while not queue.empty():
            q_item = queue.get()
            if 'manifest' in q_item:
                manifest = q_item['manifest']
            else:
                key = list(q_item.keys())[0]
                warnings[key].append(q_item[key])

        return manifest, warnings

    @staticmethod
    def __check_for_undefined_names(src_dir):
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

        return warnings

    @staticmethod
    def __report_warnings_and_exceptions(warnings):
        """
        Prints the warnings and errors that were found in the plugin code, if
        the warnings dictionary contains the 'exception' key.
        """
        if warnings and 'exception' in warnings:
            exception_msg = MessageUtils.exception_msg(warnings)
            exception_msg += '\n{}'.format(MessageUtils.warning_msg(warnings))
            raise exceptions.UserError(
                '{}\n{} Warning(s). {} Error(s).'.format(
                    exception_msg, len(warnings['warning']),
                    len(warnings['exception'])))


def _get_manifest(queue, src_dir, module, entry_point, plugin_type, validate):
    manifest = {}
    sys.path.append(src_dir)
    try:
        module_content = importlib.import_module(module)
        manifest = _validate_and_get_manifest(module, module_content,
                                              entry_point)

        if validate:
            #
            # Validated methods args against expected args and add any
            # resulting warnings to the queue for caller to process.
            # These warnings should be treated as an exception to make
            # sure build fails.
            #
            warnings = _validate_named_args(module_content, entry_point,
                                            plugin_type)
            if warnings:
                map(lambda warning: queue.put({'exception': warning}),
                    warnings)
    except ImportError as err:
        queue.put({'exception': err})
    except exceptions.UserError as user_err:
        queue.put({'exception': user_err})
    except RuntimeError as rt_err:
        queue.put({'exception': rt_err})
    finally:
        sys.path.remove(src_dir)

    queue.put({'manifest': manifest})


def _validate_and_get_manifest(module, module_content, entry_point):
    """
    Creates a plugin manifest indicating which plugin operations have
    been implemented by a plugin developer. Plugin_module_content is a
    module object which must have plugin_entry_point_name as one of its
    attributes.
    Args:
        module: name of the module imported
        module_content: plugin module content from import
        entry_point: name of entry point to the above plugin module

    Returns:
        dict: dictionary that represents plugin's manifest
    """
    # This should never happen and if it does, flag a run time error.
    if module_content is None:
        raise RuntimeError('Plugin module content is None.')

    #
    # Schema validation on plugin config file would have ensured entry
    # is a string and should never happen its none - so raise a run time
    # error if it does.
    #
    if entry_point is None:
        raise RuntimeError('Plugin entry point object is None.')

    if not hasattr(module_content, entry_point):
        raise exceptions.UserError(
            'Entry point \'{}:{}\' does not exist. \'{}\' is not a symbol'
            ' in module \'{}\'.'.format(module, entry_point, entry_point,
                                        module))
    plugin_object = getattr(module_content, entry_point)

    if plugin_object is None:
        raise exceptions.UserError('Plugin object retrieved from the entry'
                                   ' point {} is None'.format(entry_point))

    # Check which methods on the plugin object have been implemented.
    manifest = {
        'type':
        'PluginManifest',
        'hasRepositoryDiscovery':
        bool(plugin_object.discovery.repository_impl),
        'hasSourceConfigDiscovery':
        bool(plugin_object.discovery.source_config_impl),
        'hasLinkedPreSnapshot':
        bool(plugin_object.linked.pre_snapshot_impl),
        'hasLinkedPostSnapshot':
        bool(plugin_object.linked.post_snapshot_impl),
        'hasLinkedStartStaging':
        bool(plugin_object.linked.start_staging_impl),
        'hasLinkedStopStaging':
        bool(plugin_object.linked.stop_staging_impl),
        'hasLinkedStatus':
        bool(plugin_object.linked.status_impl),
        'hasLinkedWorker':
        bool(plugin_object.linked.worker_impl),
        'hasLinkedMountSpecification':
        bool(plugin_object.linked.mount_specification_impl),
        'hasVirtualConfigure':
        bool(plugin_object.virtual.configure_impl),
        'hasVirtualUnconfigure':
        bool(plugin_object.virtual.unconfigure_impl),
        'hasVirtualReconfigure':
        bool(plugin_object.virtual.reconfigure_impl),
        'hasVirtualStart':
        bool(plugin_object.virtual.start_impl),
        'hasVirtualStop':
        bool(plugin_object.virtual.stop_impl),
        'hasVirtualPreSnapshot':
        bool(plugin_object.virtual.pre_snapshot_impl),
        'hasVirtualPostSnapshot':
        bool(plugin_object.virtual.post_snapshot_impl),
        'hasVirtualMountSpecification':
        bool(plugin_object.virtual.mount_specification_impl),
        'hasVirtualStatus':
        bool(plugin_object.virtual.status_impl),
        'hasInitialize':
        bool(plugin_object.virtual.initialize_impl)
    }

    return manifest


def _validate_named_args(module_content, entry_point, plugin_type):
    """
    Does named argument validation based on the plugin type.
    """
    warnings = []

    plugin_object = getattr(module_content, entry_point)

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
        for op_name_key, op_name in plugin_attrib.__dict__.items():
            if op_name is None:
                continue
            actual_args = inspect.getargspec(op_name)
            warnings.extend(
                _check_args(method_name=op_name.__name__,
                            expected_args=_lookup_expected_args(
                                plugin_type, plugin_op_type, op_name_key),
                            actual_args=actual_args.args))

    return warnings


def _check_args(method_name, expected_args, actual_args):
    warnings = []

    if len(expected_args) != len(actual_args):
        warnings.append('Number of arguments do not match in method {}.'
                        ' Expected: {}, Found: {}.'.format(
                            method_name, list(expected_args),
                            str(actual_args)))

    if not all(arg in expected_args for arg in actual_args):
        warnings.append('Named argument mismatch in method {}.'
                        ' Expected: {}, Found: {}.'.format(
                            method_name, list(expected_args),
                            str(actual_args)))

    return warnings


def _lookup_expected_args(plugin_type, plugin_op_type, plugin_op_name):
    if plugin_type == util_classes.DIRECT_TYPE:
        return PluginImporter.expected_direct_args_by_op[plugin_op_type][
            plugin_op_name]
    else:
        return PluginImporter.expected_staged_args_by_op[plugin_op_type][
            plugin_op_name]
