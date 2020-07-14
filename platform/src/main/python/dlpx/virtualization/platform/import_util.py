#
# Copyright (c) 2020 by Delphix. All rights reserved.
#
import inspect

from dlpx.virtualization.platform import exceptions

_IMPORT_CHECKS = {}
_POST_IMPORT_CHECKS = {}


class PluginModule:
    """
    Import helper class for the plugin. An instance of this class helps to pass
    state of imported module and relevant info to all the validation methods.
    """
    def __init__(self,
                 src_dir,
                 module,
                 entry_point,
                 plugin_type,
                 module_content,
                 v_maps,
                 validate_args=False):
        self.__src_dir = src_dir
        self.__module = module
        self.__entry_point = entry_point
        self.__type = plugin_type
        self.__module_content = module_content
        self.__expected_direct_args_by_op =\
            v_maps['EXPECTED_DIRECT_ARGS_BY_OP']
        self.__expected_staged_args_by_op =\
            v_maps['EXPECTED_STAGED_ARGS_BY_OP']
        self.__expected_upgrade_args = v_maps['EXPECTED_UPGRADE_ARGS']
        self.__validate_args = validate_args

    @property
    def src_dir(self):
        return self.__src_dir

    @property
    def module(self):
        return self.__module

    @property
    def entry_point(self):
        return self.__entry_point

    @property
    def plugin_type(self):
        return self.__type

    @property
    def module_content(self):
        return self.__module_content

    @property
    def expected_direct_args_by_op(self):
        return self.__expected_direct_args_by_op

    @property
    def expected_staged_args_by_op(self):
        return self.__expected_staged_args_by_op

    @property
    def expected_upgrade_args(self):
        return self.__expected_upgrade_args

    @property
    def validate_args(self):
        return self.__validate_args


def import_check(ordinal):
    """
    This is the import check decorator. Ordinal here signifies the order in
    which the checks are executed.
    """
    def import_check_decorator(f):
        assert inspect.isfunction(f)
        assert ordinal not in _IMPORT_CHECKS

        _IMPORT_CHECKS[ordinal] = f

        return f

    return import_check_decorator


def post_import_check(ordinal):
    """
    This is the post import check decorator. Ordinal here signifies the order
    in which the checks are executed.
    """
    def post_import_check_decorator(f):
        assert inspect.isfunction(f)
        assert ordinal not in _POST_IMPORT_CHECKS

        _POST_IMPORT_CHECKS[ordinal] = f

        return f

    return post_import_check_decorator


def validate_import(plugin_module):
    """
    Runs validations on the module imported and checks if import was fine
    and imported content is valid or not.
    NOTE: Dependency checks are not handled well. A failure in one validation
    should not impact the next one if each validation defines its dependencies
    well. For now, any exception from one is considered failure of all
    validations. This can be enhanced to define dependencies well.
    """
    for key in sorted(_IMPORT_CHECKS.keys()):
        try:
            _IMPORT_CHECKS[key](plugin_module)
        except exceptions.IncorrectPluginCodeError as plugin_err:
            return [plugin_err.message]
        except exceptions.UserError as user_err:
            return [user_err.message]
    return []


def validate_post_import(plugin_module):
    """
    Runs post import validations on the module content.
    """
    warnings = []

    #
    # warnings.extend is used below since each import check returns a list of
    # warnings.
    #
    for key in sorted(_POST_IMPORT_CHECKS.keys()):
        warnings.extend(_POST_IMPORT_CHECKS[key](plugin_module))
    return warnings
