#
# Copyright (c) 2019, 2020 by Delphix. All rights reserved.
#

import mock
import pytest

from dlpx.virtualization.api import libs_pb2
from dlpx.virtualization import libs
from dlpx.virtualization.libs.exceptions import (
    IncorrectArgumentTypeError, LibraryError, PluginScriptError)
from google.protobuf import json_format
from dlpx.virtualization.common._common_classes import (PasswordCredentials)


class TestLibsRunBash:
    @staticmethod
    def test_run_bash(remote_connection):
        expected_run_bash_response = libs_pb2.RunBashResponse()
        expected_run_bash_response.return_value.exit_code = 0
        expected_run_bash_response.return_value.stdout = 'stdout'
        expected_run_bash_response.return_value.stderr = 'stderr'

        expected_command = 'command'
        expected_variables = None
        expected_use_login_shell = False

        def mock_run_bash(actual_run_bash_request):
            assert actual_run_bash_request.command == expected_command
            assert (actual_run_bash_request.use_login_shell ==
                    expected_use_login_shell)

            actual_environment = (
                actual_run_bash_request.remote_connection.environment)
            assert (actual_environment.name ==
                    remote_connection.environment.name)
            assert (actual_environment.reference ==
                    remote_connection.environment.reference)
            return expected_run_bash_response

        with mock.patch('dlpx.virtualization._engine.libs.run_bash',
                        side_effect=mock_run_bash, create=True):
            actual_run_bash_result = libs.run_bash(
                remote_connection,
                expected_command,
                expected_variables,
                expected_use_login_shell)

        expected = expected_run_bash_response.return_value
        assert actual_run_bash_result.exit_code == expected.exit_code
        assert actual_run_bash_result.stdout == expected.stdout
        assert actual_run_bash_result.stderr == expected.stderr

    @staticmethod
    def test_run_bash_check_true_success_exitcode(remote_connection):
        expected_run_bash_response = libs_pb2.RunBashResponse()
        expected_run_bash_response.return_value.exit_code = 0
        expected_run_bash_response.return_value.stdout = "stdout"
        expected_run_bash_response.return_value.stderr = "stderr"

        expected_command = "command"
        expected_variables = None
        expected_use_login_shell = False

        def mock_run_bash(actual_run_bash_request):
            assert actual_run_bash_request.command == expected_command
            assert actual_run_bash_request.use_login_shell == expected_use_login_shell
            assert (
                    actual_run_bash_request.remote_connection.environment.name
                    == remote_connection.environment.name
            )
            assert (
                    actual_run_bash_request.remote_connection.environment.reference
                    == remote_connection.environment.reference
            )
            return expected_run_bash_response

        with mock.patch("dlpx.virtualization._engine.libs.run_bash",
                        side_effect=mock_run_bash, create=True):
            actual_run_bash_result = libs.run_bash(remote_connection,
                                                   expected_command,
                                                   expected_variables,
                                                   expected_use_login_shell,
                                                   check=True)

            assert actual_run_bash_result.exit_code == expected_run_bash_response.return_value.exit_code
            assert actual_run_bash_result.stdout == expected_run_bash_response.return_value.stdout
            assert actual_run_bash_result.stderr == expected_run_bash_response.return_value.stderr

    @staticmethod
    def test_run_bash_with_check_true_failed_exitcode(remote_connection):
        expected_message = (
            'The script failed with exit code 1.'
            ' stdout : stdout and  stderr : stderr'
        )
        response = libs_pb2.RunBashResponse()
        response.return_value.exit_code = 1
        response.return_value.stdout = "stdout"
        response.return_value.stderr = "stderr"

        with mock.patch("dlpx.virtualization._engine.libs.run_bash",
                        return_value=response, create=True):
            with pytest.raises(PluginScriptError) as info:
                response = libs.run_bash(remote_connection, "test_command",
                                         check=True)
            assert info.value.message == expected_message

    @staticmethod
    def test_run_bash_with_actionable_error(remote_connection):
        expected_id = 15
        expected_message = 'Some message'

        response = libs_pb2.RunBashResponse()
        response.error.actionable_error.id = expected_id
        response.error.actionable_error.message = expected_message

        with mock.patch('dlpx.virtualization._engine.libs.run_bash',
                        return_value=response, create=True):
            with pytest.raises(LibraryError) as err_info:
                libs.run_bash(remote_connection, 'command')

        assert err_info.value._id == expected_id
        assert err_info.value.message == expected_message

    @staticmethod
    def test_run_bash_with_nonactionable_error(remote_connection):
        response = libs_pb2.RunBashResponse()
        na_error = libs_pb2.NonActionableLibraryError()
        response.error.non_actionable_error.CopyFrom(na_error)

        with mock.patch('dlpx.virtualization._engine.libs.run_bash',
                        return_value=response, create=True):
            with pytest.raises(SystemExit):
                libs.run_bash(remote_connection, 'command')

    @staticmethod
    def test_run_bash_bad_remote_connection():
        # Set the connection be a string instead of a RemoteConnection.
        connection = 'BadRemoteConnection'
        command = 'command'
        variables = None
        use_login_shell = False

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_bash(connection, command, variables, use_login_shell)

        assert err_info.value.message == (
            "The function run_bash's argument 'remote_connection' was"
            " type 'str' but should be of"
            " class 'dlpx.virtualization.common._common_classes.RemoteConnection'.")

    @staticmethod
    def test_run_bash_bad_command(remote_connection):
        # Set the command be an int instead of a string.
        command = 10
        variables = None
        use_login_shell = False

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_bash(remote_connection, command, variables, use_login_shell)

        assert err_info.value.message == (
            "The function run_bash's argument 'command' was"
            " type 'int' but should be of type 'basestring'.")

    @staticmethod
    def test_run_bash_variables_not_dict(remote_connection):
        command = 'command'
        # Set the variables be a string instead of a dict.
        variables = 'not a dict'
        use_login_shell = False

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_bash(remote_connection, command, variables, use_login_shell)

        assert err_info.value.message == (
            "The function run_bash's argument 'variables' was"
            " type 'str' but should be of"
            " type 'dict of basestring:basestring' if defined.")

    @staticmethod
    def test_run_bash_bad_variables(remote_connection):
        command = 'command'
        #
        # Set the value inside the varibles dict to be an int instead of a
        # string.
        #
        variables = {'test0': 'yes', 'test1': 10}
        use_login_shell = False

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_bash(remote_connection, command, variables, use_login_shell)

        message = ("The function run_bash's argument 'variables' was"
                   " a dict of {{type 'str':type '{}', type 'str':type '{}'}}"
                   " but should be of"
                   " type 'dict of basestring:basestring' if defined.")
        assert (err_info.value.message == message.format('int', 'str') or
                err_info.value.message == message.format('str', 'int'))

    @staticmethod
    def test_run_bash_bad_use_login_shell(remote_connection):
        command = 'command'
        variables = None
        # Set the variables be a string instead of a bool.
        use_login_shell = 'False'

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_bash(remote_connection, command, variables, use_login_shell)

        assert err_info.value.message == (
            "The function run_bash's argument 'use_login_shell' was"
            " type 'str' but should be of type 'bool' if defined.")


class TestLibsRunSync:
    @staticmethod
    def test_run_sync(remote_connection):
        expected_run_sync_response = libs_pb2.RunSyncResponse()

        expected_source_directory = 'sourceDirectory'
        expected_rsync_user = 'rsyncUser'
        expected_exclude_paths = ['/path1', '/path2']
        expected_sym_links_to_follow = ['/path3', '/path4']

        def mock_run_sync(actual_run_sync_request):
            assert (actual_run_sync_request.source_directory
                    == expected_source_directory)

            actual_environment = (
                actual_run_sync_request.remote_connection.environment)
            assert (actual_environment.name ==
                    remote_connection.environment.name)
            assert (actual_environment.reference ==
                    remote_connection.environment.reference)
            assert actual_run_sync_request.rsync_user == expected_rsync_user
            assert (actual_run_sync_request.exclude_paths ==
                    expected_exclude_paths)
            assert (actual_run_sync_request.sym_links_to_follow ==
                    expected_sym_links_to_follow)

            return expected_run_sync_response

        with mock.patch('dlpx.virtualization._engine.libs.run_sync',
                        side_effect=mock_run_sync, create=True):
            actual_runsync_response = libs.run_sync(
                remote_connection,
                expected_source_directory,
                expected_rsync_user,
                expected_exclude_paths,
                expected_sym_links_to_follow)

        assert actual_runsync_response is None

    @staticmethod
    def test_run_sync_with_actionable_error(remote_connection):
        expected_id = 15
        expected_message = 'Some message'

        response = libs_pb2.RunSyncResponse()
        response.error.actionable_error.id = expected_id
        response.error.actionable_error.message = expected_message

        with mock.patch('dlpx.virtualization._engine.libs.run_sync',
                        return_value=response, create=True):
            with pytest.raises(LibraryError) as err_info:
                libs.run_sync(remote_connection, 'dir')

        assert err_info.value._id == expected_id
        assert err_info.value.message == expected_message

    @staticmethod
    def test_run_sync_with_nonactionable_error(remote_connection):
        response = libs_pb2.RunSyncResponse()
        na_error = libs_pb2.NonActionableLibraryError()
        response.error.non_actionable_error.CopyFrom(na_error)

        with mock.patch('dlpx.virtualization._engine.libs.run_sync',
                        return_value=response, create=True):
            with pytest.raises(SystemExit):
                libs.run_sync(remote_connection, "dir")

    @staticmethod
    def test_run_sync_bad_remote_connection():
        # Set the connection be a string instead of a RemoteConnection.
        connection = 'BadRemoteConnection'
        source_directory = 'sourceDirectory'
        rsync_user = 'rsyncUser'
        exclude_paths = ['/path1', '/path2']
        sym_links_to_follow = ['/path3', '/path4']

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_sync(
                connection,
                source_directory,
                rsync_user,
                exclude_paths,
                sym_links_to_follow)

        assert err_info.value.message == (
            "The function run_sync's argument 'remote_connection' was"
            " type 'str' but should be of"
            " class 'dlpx.virtualization.common._common_classes.RemoteConnection'.")

    @staticmethod
    def test_run_sync_bad_source_directory(remote_connection):
        # Set the source_directory be an int instead of a string.
        source_directory = 10
        rsync_user = 'rsyncUser'
        exclude_paths = ['/path1', '/path2']
        sym_links_to_follow = ['/path3', '/path4']

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_sync(
                remote_connection,
                source_directory,
                rsync_user,
                exclude_paths,
                sym_links_to_follow)

        assert err_info.value.message == (
            "The function run_sync's argument 'source_directory' was"
            " type 'int' but should be of type 'basestring'.")

    @staticmethod
    def test_run_sync_bad_rsync_user(remote_connection):
        source_directory = 'sourceDirectory'
        # Set the rsync_user be an int instead of a string.
        rsync_user = 10
        exclude_paths = ['/path1', '/path2']
        sym_links_to_follow = ['/path3', '/path4']

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_sync(
                remote_connection,
                source_directory,
                rsync_user,
                exclude_paths,
                sym_links_to_follow)

        assert err_info.value.message == (
            "The function run_sync's argument 'rsync_user' was"
            " type 'int' but should be of type 'basestring' if defined.")

    @staticmethod
    def test_run_sync_exclude_paths_not_list(remote_connection):
        source_directory = 'sourceDirectory'
        rsync_user = 'rsyncUser'
        # Set the exclude_paths be an string instead of a list.
        exclude_paths = '/path'
        sym_links_to_follow = ['/path3', '/path4']

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_sync(
                remote_connection,
                source_directory,
                rsync_user,
                exclude_paths,
                sym_links_to_follow)

        assert err_info.value.message == (
            "The function run_sync's argument 'exclude_paths' was"
            " type 'str' but should be of"
            " type 'list of basestring' if defined.")

    @staticmethod
    def test_run_sync_bad_exclude_paths(remote_connection):
        source_directory = 'sourceDirectory'
        rsync_user = 'rsyncUser'
        # Set the exclude_paths list to be int instead of a string.
        exclude_paths = ['/path1', 10]
        sym_links_to_follow = ['/path3', '/path4']

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_sync(
                remote_connection,
                source_directory,
                rsync_user,
                exclude_paths,
                sym_links_to_follow)

        assert err_info.value.message == (
            "The function run_sync's argument 'exclude_paths' was a list of"
            " [type 'str', type 'int'] but should be of"
            " type 'list of basestring' if defined.")

    @staticmethod
    def test_run_sync_sym_links_to_follow_not_list(remote_connection):
        source_directory = 'sourceDirectory'
        rsync_user = 'rsyncUser'
        exclude_paths = ['/path1', '/path2']
        # Set the sym_links_to_follow be an string instead of a list.
        sym_links_to_follow = '/path'

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_sync(
                remote_connection,
                source_directory,
                rsync_user,
                exclude_paths,
                sym_links_to_follow)

        assert err_info.value.message == (
            "The function run_sync's argument 'sym_links_to_follow' was"
            " type 'str' but should be of"
            " type 'list of basestring' if defined.")

    @staticmethod
    def test_run_sync_bad_sym_links_to_follow(remote_connection):
        source_directory = 'sourceDirectory'
        rsync_user = 'rsyncUser'
        exclude_paths = ['/path1', '/path2']
        # Set the sym_links_to_follow list to be int instead of a string.
        sym_links_to_follow = ['/path3', 10]

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_sync(
                remote_connection,
                source_directory,
                rsync_user,
                exclude_paths,
                sym_links_to_follow)

        assert err_info.value.message == (
            "The function run_sync's argument 'sym_links_to_follow' was"
            " a list of [type 'str', type 'int'] but should be of"
            " type 'list of basestring' if defined.")


class TestLibsRunPowershell:
    @staticmethod
    def test_run_powershell(remote_connection):
        expected_run_powershell_response = libs_pb2.RunPowerShellResponse()
        expected_run_powershell_response.return_value.exit_code = 0
        expected_run_powershell_response.return_value.stdout = 'stdout'
        expected_run_powershell_response.return_value.stderr = 'stderr'

        expected_command = 'command'
        expected_variables = None

        def mock_run_powershell(actual_run_powershell_request):
            assert actual_run_powershell_request.command == expected_command

            actual_environment = (
                actual_run_powershell_request.remote_connection.environment)
            assert (actual_environment.name ==
                    remote_connection.environment.name)
            assert (actual_environment.reference ==
                    remote_connection.environment.reference)
            return expected_run_powershell_response

        with mock.patch('dlpx.virtualization._engine.libs.run_powershell',
                        side_effect=mock_run_powershell, create=True):
            actual_run_powershell_result = libs.run_powershell(
                remote_connection,
                expected_command,
                expected_variables)

        expected = expected_run_powershell_response.return_value
        assert actual_run_powershell_result.exit_code == expected.exit_code
        assert actual_run_powershell_result.stdout == expected.stdout
        assert actual_run_powershell_result.stderr == expected.stderr

    @staticmethod
    def test_run_powershell_check_true_exitcode_success(remote_connection):
        expected_run_powershell_response = libs_pb2.RunPowerShellResponse()
        expected_run_powershell_response.return_value.exit_code = 0
        expected_run_powershell_response.return_value.stdout = "stdout"
        expected_run_powershell_response.return_value.stderr = "stderr"

        expected_command = "command"
        expected_variables = None

        def mock_run_powershell(actual_run_powershell_request):
            assert actual_run_powershell_request.command == expected_command
            assert (
                    actual_run_powershell_request.remote_connection.environment.name
                    == remote_connection.environment.name
            )
            assert (
                    actual_run_powershell_request.remote_connection.environment.reference
                    == remote_connection.environment.reference
            )
            return expected_run_powershell_response

        with mock.patch("dlpx.virtualization._engine.libs.run_powershell",
                        side_effect=mock_run_powershell, create=True):
            actual_run_powershell_result = libs.run_powershell(
                remote_connection,
                expected_command, expected_variables, check=True)

            assert actual_run_powershell_result.exit_code == expected_run_powershell_response.return_value.exit_code
            assert actual_run_powershell_result.stdout == expected_run_powershell_response.return_value.stdout
            assert actual_run_powershell_result.stderr == expected_run_powershell_response.return_value.stderr

    @staticmethod
    def test_run_powershell_check_true_exitcode_failed(remote_connection):
        expected_message = (
            'The script failed with exit code 1.'
            ' stdout : stdout and  stderr : stderr'
        )

        response = libs_pb2.RunPowerShellResponse()
        response.return_value.exit_code = 1
        response.return_value.stdout = "stdout"
        response.return_value.stderr = "stderr"

        with mock.patch("dlpx.virtualization._engine.libs.run_powershell",
                        return_value=response, create=True):
            with pytest.raises(PluginScriptError) as info:
                response = libs.run_powershell(remote_connection, "test_command",
                                               check=True)
            assert info.value.message == expected_message

    @staticmethod
    def test_run_powershell_with_actionable_error(remote_connection):
        expected_id = 15
        expected_message = 'Some message'

        response = libs_pb2.RunPowerShellResponse()
        response.error.actionable_error.id = expected_id
        response.error.actionable_error.message = expected_message

        with mock.patch('dlpx.virtualization._engine.libs.run_powershell',
                        return_value=response, create=True):
            with pytest.raises(LibraryError) as err_info:
                libs.run_powershell(remote_connection, 'command')

        assert err_info.value._id == expected_id
        assert err_info.value.message == expected_message

    @staticmethod
    def test_run_powershell_with_nonactionable_error(remote_connection):
        response = libs_pb2.RunPowerShellResponse()
        na_error = libs_pb2.NonActionableLibraryError()
        response.error.non_actionable_error.CopyFrom(na_error)

        with mock.patch('dlpx.virtualization._engine.libs.run_powershell',
                        return_value=response, create=True):
            with pytest.raises(SystemExit):
                libs.run_powershell(remote_connection, 'command')

    @staticmethod
    def test_run_powershell_bad_remote_connection():
        # Set the connection be a string instead of a RemoteConnection.
        connection = 'BadRemoteConnection'
        command = 'command'
        variables = None

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_powershell(connection, command, variables)

        assert err_info.value.message == (
            "The function run_powershell's argument 'remote_connection' was"
            " type 'str' but should be of"
            " class 'dlpx.virtualization.common._common_classes.RemoteConnection'.")

    @staticmethod
    def test_run_powershell_bad_command(remote_connection):
        # Set the command be an int instead of a string.
        command = 10
        variables = None

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_powershell(remote_connection, command, variables)

        assert err_info.value.message == (
            "The function run_powershell's argument 'command' was"
            " type 'int' but should be of type 'basestring'.")

    @staticmethod
    def test_run_powershell_variables_not_dict(remote_connection):
        command = 'command'
        # Set the variables be a string instead of a dict.
        variables = 'not a dict'

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_powershell(remote_connection, command, variables)

        assert err_info.value.message == (
            "The function run_powershell's argument 'variables' was"
            " type 'str' but should be of"
            " type 'dict of basestring:basestring' if defined.")

    @staticmethod
    def test_run_powershell_bad_variables(remote_connection):
        command = 'command'
        #
        # Set the value inside the varibles dict to be an int instead of a
        # string.
        #
        variables = {'test0': 'yes', 'test1': 10}

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_powershell(remote_connection, command, variables)

        message = ("The function run_powershell's argument 'variables' was"
                   " a dict of {{type 'str':type '{}', type 'str':type '{}'}}"
                   " but should be of"
                   " type 'dict of basestring:basestring' if defined.")
        assert (err_info.value.message == message.format('int', 'str') or
                err_info.value.message == message.format('str', 'int'))


class TestLibsRunExpect:
    @staticmethod
    def test_run_expect(remote_connection):
        expected_run_expect_response = libs_pb2.RunExpectResponse()
        expected_run_expect_response.return_value.exit_code = 0
        expected_run_expect_response.return_value.stdout = 'stdout'
        expected_run_expect_response.return_value.stderr = 'stderr'

        expected_command = 'command'
        expected_variables = None

        def mock_run_expect(actual_run_expect_request):
            assert actual_run_expect_request.command == expected_command

            actual_environment = (
                actual_run_expect_request.remote_connection.environment)
            assert (actual_environment.name ==
                    remote_connection.environment.name)
            assert (actual_environment.reference ==
                    remote_connection.environment.reference)
            return expected_run_expect_response

        with mock.patch('dlpx.virtualization._engine.libs.run_expect',
                        side_effect=mock_run_expect, create=True):
            actual_run_expect_result = libs.run_expect(
                remote_connection,
                expected_command,
                expected_variables)

        expected = expected_run_expect_response.return_value
        assert actual_run_expect_result.exit_code == expected.exit_code
        assert actual_run_expect_result.stdout == expected.stdout
        assert actual_run_expect_result.stderr == expected.stderr

    @staticmethod
    def test_run_expect_check_true_exitcode_success(remote_connection):
        expected_run_expect_response = libs_pb2.RunPowerShellResponse()
        expected_run_expect_response.return_value.exit_code = 0
        expected_run_expect_response.return_value.stdout = "stdout"
        expected_run_expect_response.return_value.stderr = "stderr"

        expected_command = "command"
        expected_variables = None

        def mock_run_expect(actual_run_expect_request):
            assert actual_run_expect_request.command == expected_command
            assert (
                    actual_run_expect_request.remote_connection.environment.name
                    == remote_connection.environment.name
            )
            assert (
                    actual_run_expect_request.remote_connection.environment.reference
                    == remote_connection.environment.reference
            )
            return expected_run_expect_response

        with mock.patch("dlpx.virtualization._engine.libs.run_expect",
                        side_effect=mock_run_expect, create=True):
            actual_run_expect_result = libs.run_expect(
                remote_connection,
                expected_command, expected_variables, check=True)

            assert actual_run_expect_result.exit_code == expected_run_expect_response.return_value.exit_code
            assert actual_run_expect_result.stdout == expected_run_expect_response.return_value.stdout
            assert actual_run_expect_result.stderr == expected_run_expect_response.return_value.stderr

    @staticmethod
    def test_run_expect_check_true_exitcode_failed(remote_connection):
        expected_message = (
            'The script failed with exit code 1.'
            ' stdout : stdout and  stderr : stderr'
        )

        response = libs_pb2.RunExpectResponse()
        response.return_value.exit_code = 1
        response.return_value.stdout = "stdout"
        response.return_value.stderr = "stderr"

        with mock.patch("dlpx.virtualization._engine.libs.run_expect",
                        return_value=response, create=True):
            with pytest.raises(PluginScriptError) as info:
                response = libs.run_expect(remote_connection, "test_command",
                                           check=True)
            assert info.value.message == expected_message

    @staticmethod
    def test_run_expect_with_actionable_error(remote_connection):
        expected_id = 15
        expected_message = 'Some message'

        response = libs_pb2.RunExpectResponse()
        response.error.actionable_error.id = expected_id
        response.error.actionable_error.message = expected_message

        with mock.patch('dlpx.virtualization._engine.libs.run_expect',
                        return_value=response, create=True):
            with pytest.raises(LibraryError) as err_info:
                libs.run_expect(remote_connection, 'command')

        assert err_info.value._id == expected_id
        assert err_info.value.message == expected_message

    @staticmethod
    def test_run_expect_with_nonactionable_error(remote_connection):
        response = libs_pb2.RunExpectResponse()
        na_error = libs_pb2.NonActionableLibraryError()
        response.error.non_actionable_error.CopyFrom(na_error)

        with mock.patch('dlpx.virtualization._engine.libs.run_expect',
                        return_value=response, create=True):
            with pytest.raises(SystemExit):
                libs.run_expect(remote_connection, "command")

    @staticmethod
    def test_run_expect_bad_remote_connection():
        # Set the connection be a string instead of a RemoteConnection.
        connection = 'BadRemoteConnection'
        command = 'command'
        variables = None

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_expect(connection, command, variables)

        assert err_info.value.message == (
            "The function run_expect's argument 'remote_connection' was"
            " type 'str' but should be of"
            " class 'dlpx.virtualization.common._common_classes.RemoteConnection'.")

    @staticmethod
    def test_run_expect_bad_command(remote_connection):
        # Set the command be an int instead of a string.
        command = 10
        variables = None

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_expect(remote_connection, command, variables)

        assert err_info.value.message == (
            "The function run_expect's argument 'command' was"
            " type 'int' but should be of type 'basestring'.")

    @staticmethod
    def test_run_expect_variables_not_dict(remote_connection):
        command = 'command'
        # Set the variables be a string instead of a dict.
        variables = 'not a dict'

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_expect(remote_connection, command, variables)

        assert err_info.value.message == (
            "The function run_expect's argument 'variables' was"
            " type 'str' but should be of"
            " type 'dict of basestring:basestring' if defined.")

    @staticmethod
    def test_run_expect_bad_variables(remote_connection):
        command = 'command'
        #
        # Set the value inside the varibles dict to be an int instead of a
        # string.
        #
        variables = {'test0': 'yes', 'test1': 10}

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.run_expect(remote_connection, command, variables)

        message = ("The function run_expect's argument 'variables' was"
                   " a dict of {{type 'str':type '{}', type 'str':type '{}'}}"
                   " but should be of"
                   " type 'dict of basestring:basestring' if defined.")
        assert (err_info.value.message == message.format('int', 'str') or
                err_info.value.message == message.format('str', 'int'))


class TestLibsRetrieveCredentials:
    @staticmethod
    def test_retrieve_password_credentials():
        expected_retrieve_credentials_response = libs_pb2.CredentialsResponse()
        expected_retrieve_credentials_response.return_value.username = 'some user'
        expected_retrieve_credentials_response.return_value.password = 'some password'

        expected_credentials_supplier = {'some supplier property': 'some supplier value'}

        def mock_retrieve_credentials(actual_retrieve_credentials_request):
            assert json_format.MessageToDict(actual_retrieve_credentials_request.credentials_supplier) == \
                   expected_credentials_supplier

            return expected_retrieve_credentials_response

        with mock.patch('dlpx.virtualization._engine.libs.retrieve_credentials',
                        side_effect=mock_retrieve_credentials, create=True):
            actual_retrieve_credentials_result = libs.retrieve_credentials(expected_credentials_supplier)

        expected = expected_retrieve_credentials_response.return_value
        assert actual_retrieve_credentials_result.username == expected.username
        assert actual_retrieve_credentials_result.password == expected.password

    @staticmethod
    def test_retrieve_keypair_credentials():
        expected_retrieve_credentials_response = libs_pb2.CredentialsResponse()
        expected_retrieve_credentials_response.return_value.username = 'some user'
        expected_retrieve_credentials_response.return_value.key_pair.private_key = 'some private key'
        expected_retrieve_credentials_response.return_value.key_pair.public_key = 'some public key'

        expected_credentials_supplier = {'some supplier property': 'some supplier value'}

        def mock_retrieve_credentials(actual_retrieve_credentials_request):
            assert json_format.MessageToDict(actual_retrieve_credentials_request.credentials_supplier) == \
                   expected_credentials_supplier

            return expected_retrieve_credentials_response

        with mock.patch('dlpx.virtualization._engine.libs.retrieve_credentials',
                        side_effect=mock_retrieve_credentials, create=True):
            actual_retrieve_credentials_result = libs.retrieve_credentials(expected_credentials_supplier)

        expected = expected_retrieve_credentials_response.return_value
        assert actual_retrieve_credentials_result.username == expected.username
        assert actual_retrieve_credentials_result.private_key == expected.key_pair.private_key
        assert actual_retrieve_credentials_result.public_key == expected.key_pair.public_key

    @staticmethod
    def test_retrieve_credentials_with_actionable_error():
        expected_id = 15
        expected_message = 'Some message'

        response = libs_pb2.CredentialsResponse()
        response.error.actionable_error.id = expected_id
        response.error.actionable_error.message = expected_message

        with mock.patch('dlpx.virtualization._engine.libs.retrieve_credentials',
                        return_value=response, create=True):
            with pytest.raises(LibraryError) as err_info:
                libs.retrieve_credentials({'some supplier property': 'some supplier value'})

        assert err_info.value._id == expected_id
        assert err_info.value.message == expected_message

    @staticmethod
    def test_retrieve_credentials_with_nonactionable_error():
        response = libs_pb2.CredentialsResponse()
        na_error = libs_pb2.NonActionableLibraryError()
        response.error.non_actionable_error.CopyFrom(na_error)

        with mock.patch('dlpx.virtualization._engine.libs.retrieve_credentials',
                        return_value=response, create=True):
            with pytest.raises(SystemExit):
                libs.retrieve_credentials({'some supplier property': 'some supplier value'})

    @staticmethod
    def test_retrieve_credentials_bad_supplier():
        # Set the supplier be an int instead of a dictionary.
        credentials_supplier = 10

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.retrieve_credentials(credentials_supplier)

        assert err_info.value.message == (
            "The function retrieve_credentials's argument 'credentials_supplier' was"
            " type 'int' but should be of type 'dict'.")


class TestLibsUpgradePassword:
    @staticmethod
    def test_upgrade_password():
        expected_password = 'some password'

        expected_credentials_supplier = {'type': 'NamedPasswordCredential', 'password': expected_password}
        expected_upgrade_password_response = libs_pb2.UpgradePasswordResponse()
        expected_upgrade_password_response.return_value.credentials_supplier.update(expected_credentials_supplier)

        def mock_upgrade_password(actual_upgrade_password_request):
            assert actual_upgrade_password_request.password == expected_password

            return expected_upgrade_password_response

        with mock.patch('dlpx.virtualization._engine.libs.upgrade_password',
                        side_effect=mock_upgrade_password, create=True):
            actual_upgrade_password_result = libs.upgrade_password(expected_password)

        assert actual_upgrade_password_result == expected_credentials_supplier

    @staticmethod
    def test_upgrade_password_with_username():
        expected_password = 'some password'
        expected_username = 'some user name'

        expected_credentials_supplier = {'type': 'NamedPasswordCredential', 'password': expected_password, 'username': expected_username}
        expected_upgrade_password_response = libs_pb2.UpgradePasswordResponse()
        expected_upgrade_password_response.return_value.credentials_supplier.update(expected_credentials_supplier)

        def mock_upgrade_password(actual_upgrade_password_request):
            assert actual_upgrade_password_request.password == expected_password
            assert actual_upgrade_password_request.username == expected_username

            return expected_upgrade_password_response

        with mock.patch('dlpx.virtualization._engine.libs.upgrade_password',
                        side_effect=mock_upgrade_password, create=True):
            actual_upgrade_password_result = libs.upgrade_password(expected_password, username=expected_username)

        assert actual_upgrade_password_result == expected_credentials_supplier

    @staticmethod
    def test_upgrade_password_invalid_password():
        expected_password = 10
        expected_username = 'some user name'

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.upgrade_password(expected_password, username=expected_username)

        assert err_info.value.message == (
            "The function upgrade_password's argument 'password' was"
            " type 'int' but should be of type 'basestring'.")

    @staticmethod
    def test_upgrade_password_invalid_username():
        expected_password = 'some password'
        expected_username = 10

        with pytest.raises(IncorrectArgumentTypeError) as err_info:
            libs.upgrade_password(expected_password, username=expected_username)

        assert err_info.value.message == (
            "The function upgrade_password's argument 'username' was"
            " type 'int' but should be of type 'basestring' if defined.")
