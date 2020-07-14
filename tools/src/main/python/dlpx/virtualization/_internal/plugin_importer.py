#
# Copyright (c) 2019, 2020 by Delphix. All rights reserved.
#
import importlib
import logging
import os
import sys
from collections import defaultdict, namedtuple
from multiprocessing import Process, Queue

import yaml
from dlpx.virtualization._internal import const, exceptions
from dlpx.virtualization.platform import import_util

logger = logging.getLogger(__name__)

PLUGIN_IMPORTER_YAML = os.path.join(const.PLUGIN_SCHEMAS_DIR,
                                    'plugin_importer.yaml')

validation_result = namedtuple('validation_result', ['plugin_manifest'])


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
    process to ensure it's isolated and does not pollute caller's runtime.
    On successful import, callers can get the manifest describing what
    methods are implemented in the plugin code. If import fails or has
    issues with validation of module content and entry points- will save
    errors/warnings in a dict that callers can access.
    """
    v_maps = load_validation_maps()
    required_methods_by_plugin_type = v_maps['REQUIRED_METHODS_BY_PLUGIN_TYPE']
    required_methods_description = v_maps['REQUIRED_METHODS_DESCRIPTION']

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
        self.__post_import_checks = [self.__check_for_required_methods]

    @property
    def result(self):
        return validation_result(plugin_manifest=self.__plugin_manifest)

    def validate_plugin_module(self):
        """
        Imports the plugin module, does post import validation.
        Returns:
            plugin manifest - dict describing methods implemented in the plugin
            is available to callers via the result property.
        NOTE:
            Importing module in the current context pollutes the runtime of
            the caller, in this case dvp. If the module being imported, for
            e.g. contains code that adds a handler to the root logger at
            import time, this can cause issues with logging in this code and
            callers of validator. To avoid such issues, perform the import in
            in a sub-process and on completion return the output.
        """
        logger.debug('Importing plugin module : %s', self.__plugin_module)
        self.__plugin_manifest, warnings = self.__internal_import()
        self.__run_checks(warnings)

    def __internal_import(self):
        """
        Imports the module in a sub-process to check for errors or issues.
        Also does an eval on the entry point.
        """
        plugin_manifest = {}
        warnings = defaultdict(list)
        try:
            plugin_manifest, warnings = (self.__import_in_subprocess(
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
        process = Process(target=_import_module_and_get_manifest,
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

    def __run_checks(self, warnings):
        """
        Performs checks of the plugin code that should take place after
        importing.
        """
        for check in self.__post_import_checks:
            check_warnings = check()
            if check_warnings and 'warning' in check_warnings:
                warnings['warning'].extend(check_warnings['warning'])

        if warnings:
            if 'exception' in warnings:
                raise exceptions.ValidationFailedError(warnings)
            if 'sdk exception' in warnings:
                sdk_exception_msg =\
                    exceptions.ValidationFailedError(warnings).message
                raise exceptions.SDKToolingError(sdk_exception_msg)

            if 'warning' in warnings:
                #
                # Use the ValidationFailedError type to get a formatted message
                # with number of warnings included in the message.
                #
                warning_msg = exceptions.ValidationFailedError(
                    warnings).message
                logger.warn(warning_msg)

    def __check_for_required_methods(self):
        """
        Checks for required methods in the manifest and adds warnings for any
        missing methods.
        """
        warnings = defaultdict(list)
        if not self.__plugin_manifest:
            return warnings
        for method_key, method_name in \
                PluginImporter.required_methods_by_plugin_type[
                self.__plugin_type].items():
            if self.__plugin_manifest[method_key] is False:
                warnings['warning'].append(
                    'Implementation missing '
                    'for required method {}. The Plugin Operation \'{}\' '
                    'will fail when executed.'.format(
                        method_name, PluginImporter.
                        required_methods_description[method_key]))
        return warnings


def _import_module_and_get_manifest(queue, src_dir, module, entry_point,
                                    plugin_type, validate):
    """
    Imports the plugin module, runs validations and returns the manifest.
    """
    module_content = None

    try:
        module_content = _import_helper(queue, src_dir, module)
    except exceptions.UserError:
        #
        # Exception here means there was an error importing the module and
        # queue is updated with the exception details inside _import_helper.
        #
        return

    manifest = get_manifest(src_dir, module, entry_point,
                            module_content, plugin_type,
                            validate, queue)
    queue.put({'manifest': manifest})


def get_manifest(src_dir, module, entry_point, module_content,
                 plugin_type, validate, queue):
    """
    Helper method to run validations and prepare the manifest.

    NOTE:
         This code is moved out into a separate method to help running
         unit tests on windows for validations. Since the behaviour of
         multiprocessing.Process module is different for windows and linux,
         unit testing validate_plugin_module method using mock has issues.

         More details at :
         https://rhodesmill.org/brandon/2010/python-multiprocessing-linux-windows/
    """
    #
    # Create an instance of plugin module with associated state to pass around
    # to the validation code.
    #
    plugin_module = import_util.PluginModule(src_dir, module, entry_point,
                                             plugin_type, module_content,
                                             PluginImporter.v_maps, validate)

    # Validate if the module imported fine and is the expected one.
    warnings = import_util.validate_import(plugin_module)
    _process_warnings(queue, warnings)

    # If the import itself had issues, no point validating further.
    if warnings and len(warnings) > 0:
        return

    # Run post import validations and consolidate issues.
    warnings = import_util.validate_post_import(plugin_module)
    _process_warnings(queue, warnings)

    return _prepare_manifest(entry_point, module_content)


def _import_helper(queue, src_dir, module):
    """Helper method to import the module and handle any import time
    exceptions.
    """
    module_content = None
    sys.path.append(src_dir)

    try:
        module_content = importlib.import_module(module)
    except (ImportError, TypeError) as err:
        queue.put({'exception': err})
    except Exception as err:
        #
        # We need to figure out if this is an error that was raised inside the
        # wrappers which would mean that it is a user error. Otherwise we
        # should still queue the error but specify that it's not a user error.
        #
        parent_class_list = [base.__name__ for base in err.__class__.__bases__]
        if 'PlatformError' in parent_class_list:
            # This is a user error
            error = exceptions.UserError(err.message)
            queue.put({'exception': error})
        else:
            #
            # Because we don't know if the output of the err is actually in the
            # message, we just cast the exception to a string and hope to get
            # the most information possible.
            #
            error = exceptions.SDKToolingError(str(err))
            queue.put({'sdk exception': error})
    finally:
        sys.path.remove(src_dir)

    if not module_content:
        raise exceptions.UserError("Plugin module content is None")

    return module_content


def _process_warnings(queue, warnings):
    for warning in warnings:
        queue.put({'exception': warning})


def _prepare_manifest(entry_point, module_content):
    """
    Creates a plugin manifest indicating which plugin operations have
    been implemented by a plugin developer. Plugin_module_content is a
    module object which must have plugin_entry_point_name as one of its
    attributes.
    Args:
        entry_point: name of entry point to the above plugin module
        module_content: plugin module content from import

    Returns:
        dict: dictionary that represents plugin's manifest
    """
    plugin_object = getattr(module_content, entry_point)

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
        bool(plugin_object.virtual.initialize_impl),
        'migrationIdList':
        plugin_object.upgrade.migration_id_list
    }

    return manifest
