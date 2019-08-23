#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import os

import click.testing as click_testing
import mock
import pytest
import yaml
from dlpx.virtualization._internal import cli, exceptions, util_classes


class TestCli:
    @staticmethod
    def test_default_verbosity():
        runner = click_testing.CliRunner()

        result = runner.invoke(cli.delphix_sdk)

        assert result.exit_code == 0, 'Output: {}'.format(result.output)

    @staticmethod
    def test_verbose():
        runner = click_testing.CliRunner()

        # Run with --help or else click will complain there isn't a command
        result = runner.invoke(cli.delphix_sdk, ['-v', '--help'])

        assert result.exit_code == 0, 'Output: {}'.format(result.output)

    @staticmethod
    def test_too_verbose():
        runner = click_testing.CliRunner()

        result = runner.invoke(cli.delphix_sdk, '-vvvv')

        assert result.exit_code != 0, 'Output: {}'.format(result.output)

    @staticmethod
    def test_quiet():
        runner = click_testing.CliRunner()

        # Run with -h or else click will complain there isn't a command
        result = runner.invoke(cli.delphix_sdk, ['-q', '--help'])

        assert result.exit_code == 0, 'Output: {}'.format(result.output)

    @staticmethod
    def test_too_quiet():
        runner = click_testing.CliRunner()

        result = runner.invoke(cli.delphix_sdk, ['-qqqq'])

        assert result.exit_code != 0, 'Output: {}'.format(result.output)

    @staticmethod
    def test_quiet_verbose_mutually_exclusive():
        runner = click_testing.CliRunner()

        result = runner.invoke(cli.delphix_sdk, ['-qv'])

        assert result.exit_code != 0, 'Output: {}'.format(result.output)

    @staticmethod
    def test_version():
        runner = click_testing.CliRunner()

        result = runner.invoke(cli.delphix_sdk, ['--version'])

        assert result.exit_code == 0, 'Output: {}'.format(result.output)

    @staticmethod
    def test_h_flag():
        runner = click_testing.CliRunner()

        result = runner.invoke(cli.delphix_sdk, ['-h'])

        assert result.exit_code == 0, 'Output: {}'.format(result.output)

        # A proxy to test the help message was actually printed
        assert 'Usage:' in result.output, 'Output: {}'.format(result.output)

    @staticmethod
    @pytest.mark.parametrize('verbose,quiet,expected', [(0, 0, 30), (1, 0, 20),
                                                        (2, 0, 10), (3, 0, 0),
                                                        (0, 1, 40), (0, 2, 50),
                                                        (0, 3, 60)])
    def test_get_console_logging_level(verbose, quiet, expected):
        assert cli.get_console_logging_level(verbose, quiet) == expected

    @staticmethod
    def test_get_console_logging_level_both_non_zero():
        with pytest.raises(AssertionError):
            cli.get_console_logging_level(1, 1)

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.initialize.init')
    def test_command_user_error(mock_init, plugin_name):
        runner = click_testing.CliRunner()

        mock_init.side_effect = exceptions.UserError("codegen_error")
        result = runner.invoke(cli.delphix_sdk, ['init', '-n', plugin_name])

        assert result.exit_code == 1
        assert result.output == 'codegen_error\n'

        # 'DIRECT' and os.getcwd() are the expected defaults
        mock_init.assert_called_once_with(os.getcwd(),
                                          util_classes.DIRECT_TYPE,
                                          plugin_name,
                                          util_classes.UNIX_HOST_TYPE)

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.initialize.init')
    def test_command_non_user_error(mock_init, plugin_name):
        runner = click_testing.CliRunner()

        mock_init.side_effect = Exception("internal_error")
        result = runner.invoke(cli.delphix_sdk, ['init', '-n', plugin_name])

        assert result.exit_code == 2
        assert 'Internal error, please contact Delphix.\n' in result.output

        # 'DIRECT' and os.getcwd() are the expected defaults
        mock_init.assert_called_once_with(os.getcwd(),
                                          util_classes.DIRECT_TYPE,
                                          plugin_name,
                                          util_classes.UNIX_HOST_TYPE)


class TestInitCli:
    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.initialize.init')
    def test_default_params(mock_init, plugin_name):
        runner = click_testing.CliRunner()

        result = runner.invoke(cli.delphix_sdk, ['init', '-n', plugin_name])

        assert result.exit_code == 0, 'Output: {}'.format(result.output)

        # 'DIRECT' and os.getcwd() are the expected defaults
        mock_init.assert_called_once_with(os.getcwd(),
                                          util_classes.DIRECT_TYPE,
                                          plugin_name,
                                          util_classes.UNIX_HOST_TYPE)

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.initialize.init')
    def test_non_default_params(mock_init, plugin_name):
        runner = click_testing.CliRunner()

        result = runner.invoke(cli.delphix_sdk, [
            'init', '-s', util_classes.STAGED_TYPE, '-r', '.', '-n',
            plugin_name
        ])

        assert result.exit_code == 0, 'Output: {}'.format(result.output)
        mock_init.assert_called_once_with(os.getcwd(),
                                          util_classes.STAGED_TYPE,
                                          plugin_name,
                                          util_classes.UNIX_HOST_TYPE)

    @staticmethod
    def test_invalid_ingestion_strategy(plugin_name):
        runner = click_testing.CliRunner()

        result = runner.invoke(
            cli.delphix_sdk,
            ['init', '-n', plugin_name, '-s', 'FAKE_STRATEGY'])

        assert result.exit_code != 0

    @staticmethod
    def test_name_required():
        runner = click_testing.CliRunner()

        result = runner.invoke(cli.delphix_sdk, ['init'])

        assert result.exit_code != 0

    @staticmethod
    def test_multiple_host_types():
        runner = click_testing.CliRunner()

        result = runner.invoke(cli.delphix_sdk, [
            'init', '-t', '{},{}'.format(util_classes.UNIX_HOST_TYPE,
                                         util_classes.WINDOWS_HOST_TYPE)
        ])

        assert result.exit_code != 0
        assert "invalid choice" in result.output

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.initialize.init')
    def test_windows_host_type(mock_init, plugin_name):
        runner = click_testing.CliRunner()

        result = runner.invoke(
            cli.delphix_sdk,
            ['init', '-n', plugin_name, '-t', util_classes.WINDOWS_HOST_TYPE])
        assert result.exit_code == 0, 'Output: {}'.format(result.output)
        mock_init.assert_called_once_with(os.getcwd(),
                                          util_classes.DIRECT_TYPE,
                                          plugin_name,
                                          util_classes.WINDOWS_HOST_TYPE)

    @staticmethod
    def test_invalid_host_type():
        runner = click_testing.CliRunner()

        result = runner.invoke(cli.delphix_sdk, ['init', '-t', 'UNI'])

        assert result.exit_code != 0
        assert "invalid choice" in result.output


class TestBuildCli:
    @staticmethod
    @pytest.fixture
    def artifact_file_created():
        #
        # For all build tests since we're creating the file, it should not be
        # created via the fixtures.
        #
        return False

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.build.build')
    def test_default_plugin_file_success(mock_build, plugin_config_filename,
                                         plugin_config_content, artifact_file):

        runner = click_testing.CliRunner()
        # Change the runner's working dir to test the default works
        with runner.isolated_filesystem():
            with open(plugin_config_filename, 'w') as f:
                f.write(
                    yaml.dump(plugin_config_content, default_flow_style=False))

            plugin_config_file = os.path.realpath(f.name)
            result = runner.invoke(cli.delphix_sdk,
                                   ['build', '-a', artifact_file])

            assert result.exit_code == 0, 'Output: {}'.format(result.output)
            mock_build.assert_called_once_with(plugin_config_file,
                                               artifact_file, False, False)

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.build.build')
    def test_generate_only_success(mock_build, plugin_config_filename,
                                   plugin_config_content):

        runner = click_testing.CliRunner()
        # Change the runner's working dir to test the default works
        with runner.isolated_filesystem():
            with open(plugin_config_filename, 'w') as f:
                f.write(
                    yaml.dump(plugin_config_content, default_flow_style=False))

            plugin_config_file = os.path.realpath(f.name)
            result = runner.invoke(cli.delphix_sdk, ['build', '-g'])

            assert result.exit_code == 0, 'Output: {}'.format(result.output)
            mock_build.assert_called_once_with(plugin_config_file, None, True,
                                               False)

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.build.build')
    def test_valid_params(mock_build, plugin_config_file, artifact_file):
        runner = click_testing.CliRunner()
        result = runner.invoke(
            cli.delphix_sdk,
            ['build', '-c', plugin_config_file, '-a', artifact_file])

        assert result.exit_code == 0, 'Output: {}'.format(result.output)
        mock_build.assert_called_once_with(plugin_config_file, artifact_file,
                                           False, False)

    @staticmethod
    @pytest.mark.parametrize('plugin_config_filename', ['plugin.yml'])
    @mock.patch('dlpx.virtualization._internal.commands.build.build')
    def test_valid_params_new_name(mock_build, plugin_config_file,
                                   artifact_filename):
        runner = click_testing.CliRunner()
        result = runner.invoke(cli.delphix_sdk,
                               ['build', '-c', plugin_config_file])

        assert result.exit_code == 0, 'Output: {}'.format(result.output)
        mock_build.assert_called_once_with(
            plugin_config_file, os.path.join(os.getcwd(), artifact_filename),
            False, False)

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.build.build')
    def test_skip_id_validation(mock_build, plugin_config_file, artifact_file):
        runner = click_testing.CliRunner()

        result = runner.invoke(cli.delphix_sdk, [
            'build', '-c', plugin_config_file, '-a', artifact_file,
            '--skip-id-validation'
        ])

        assert result.exit_code == 0, 'Output: {}'.format(result.output)
        mock_build.assert_called_once_with(plugin_config_file, artifact_file,
                                           False, True)

    @staticmethod
    @pytest.mark.parametrize('plugin_config_file',
                             ['/not/a/real/file/plugin_config.yml'])
    def test_file_not_exist(plugin_config_file):
        runner = click_testing.CliRunner()
        result = runner.invoke(cli.delphix_sdk,
                               ['build', '-c', plugin_config_file])

        assert result.exit_code == 2
        assert result.output == (u'Usage: delphix-sdk build [OPTIONS]'
                                 u'\nTry "delphix-sdk build -h" for help.'
                                 u'\n'
                                 u'\nError: Invalid value for "-c" /'
                                 u' "--plugin-config": File'
                                 u' "/not/a/real/file/plugin_config.yml"'
                                 u' does not exist.'
                                 u'\n')

    @staticmethod
    def test_option_a_and_g_set(plugin_config_file, artifact_file):
        runner = click_testing.CliRunner()
        result = runner.invoke(
            cli.delphix_sdk,
            ['build', '-c', plugin_config_file, '-a', artifact_file, '-g'])

        assert result.exit_code == 2
        assert result.output == (u'Error: "upload_artifact" is'
                                 u' mutually exclusive with argument(s)'
                                 u' "generate_only".'
                                 u'\n')

    @staticmethod
    def test_option_g_and_a_set(plugin_config_file, artifact_file):
        runner = click_testing.CliRunner()
        result = runner.invoke(
            cli.delphix_sdk,
            ['build', '-c', plugin_config_file, '-g', '-a', artifact_file])

        assert result.exit_code == 2
        assert result.output == (u'Error: "generate_only" is'
                                 u' mutually exclusive with argument(s)'
                                 u' "upload_artifact".'
                                 u'\n')


class TestUploadCli:
    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.upload.upload')
    def test_default_params(mock_upload, artifact_file):
        engine = 'engine'
        user = 'admin'
        password = 'password'

        cwd = os.getcwd()
        try:
            os.chdir(os.path.dirname(artifact_file))
            runner = click_testing.CliRunner()
            result = runner.invoke(
                cli.delphix_sdk,
                ['upload', '-e', engine, '-u', user, '--password', password])
        finally:
            os.chdir(cwd)

        assert result.exit_code == 0, 'Output: {}'.format(result.output)
        mock_upload.assert_called_once_with(engine, user, artifact_file,
                                            password)

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.upload.upload')
    def test_valid_params(mock_upload, artifact_file):
        engine = 'engine'
        user = 'admin'
        password = 'password'

        runner = click_testing.CliRunner()
        result = runner.invoke(cli.delphix_sdk, [
            'upload', '-e', engine, '-u', user, '-a', artifact_file,
            '--password', password
        ])

        assert result.exit_code == 0, 'Output: {}'.format(result.output)
        mock_upload.assert_called_once_with(engine, user, artifact_file,
                                            password)

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.upload.upload')
    def test_bad_password(mock_upload, artifact_file):
        engine = 'engine'
        user = 'admin'
        password = 'delphix2'
        mock_upload.side_effect = exceptions.HttpError(
            401, {
                'type': 'APIError',
                'details': 'Invalid username or password.',
                'action': 'Try with a different set of credentials.',
                'id': 'exception.webservices.login.failed'
            })

        runner = click_testing.CliRunner()
        result = runner.invoke(cli.delphix_sdk, [
            'upload', '-e', engine, '-u', user, '-a', artifact_file,
            '--password', password
        ])

        assert result.exit_code == 1
        assert result.output == (
            'API request failed with HTTP Status 401'
            '\nDetails: Invalid username or password.'
            '\nAction: Try with a different set of credentials.'
            '\n')
        mock_upload.assert_called_once_with(engine, user, artifact_file,
                                            password)

    @staticmethod
    @pytest.mark.parametrize('artifact_file',
                             ['/not/a/real/file/artifact.json'])
    def test_file_not_exist(artifact_file):
        # No mock is needed because we should never call the upload function.
        engine = 'engine'
        user = 'admin'
        password = 'delphix'

        runner = click_testing.CliRunner()
        result = runner.invoke(cli.delphix_sdk, [
            'upload', '-e', engine, '-u', user, '-a', artifact_file,
            '--password', password
        ])

        assert result.exit_code == 2
        assert result.output == (u'Usage: delphix-sdk upload [OPTIONS]'
                                 u'\nTry "delphix-sdk upload -h" for help.'
                                 u'\n'
                                 u'\nError: Invalid value for "-a" /'
                                 u' "--upload-artifact": File'
                                 u' "/not/a/real/file/artifact.json"'
                                 u' does not exist.'
                                 u'\n')

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.upload.upload')
    @pytest.mark.usefixtures('dvp_config_file')
    def test_with_config_file_success(mock_upload, artifact_file,
                                      dvp_config_properties):
        engine = dvp_config_properties['engine']
        user = dvp_config_properties['user']
        password = dvp_config_properties['password']
        cwd = os.getcwd()

        try:
            os.chdir(os.path.dirname(artifact_file))
            runner = click_testing.CliRunner()
            result = runner.invoke(cli.delphix_sdk, ['upload'])
        finally:
            os.chdir(cwd)

        assert result.exit_code == 0, 'Output: {}'.format(result.output)
        mock_upload.assert_called_once_with(engine, user, artifact_file,
                                            password)

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.upload.upload')
    @pytest.mark.usefixtures('dvp_config_file')
    def test_with_config_file_override(mock_upload, artifact_file,
                                       dvp_config_properties):
        engine = dvp_config_properties['engine']
        user = 'fake_admin'
        password = dvp_config_properties['password']
        cwd = os.getcwd()

        try:
            os.chdir(os.path.dirname(artifact_file))
            runner = click_testing.CliRunner()
            result = runner.invoke(cli.delphix_sdk, ['upload', '-u', user])
        finally:
            os.chdir(cwd)

        assert result.exit_code == 0, 'Output: {}'.format(result.output)
        mock_upload.assert_called_once_with(engine, user, artifact_file,
                                            password)

    @staticmethod
    @pytest.mark.parametrize('dvp_config_properties', [{
        'user': 'user',
        'password': 'password'
    }])
    @pytest.mark.usefixtures('dvp_config_file')
    def test_with_config_file_fail(artifact_file):
        cwd = os.getcwd()

        try:
            os.chdir(os.path.dirname(artifact_file))
            runner = click_testing.CliRunner()
            result = runner.invoke(cli.delphix_sdk, ['upload'])
        finally:
            os.chdir(cwd)

        assert result.exit_code == 2
        assert result.output == (u'Usage: delphix-sdk upload [OPTIONS]\n'
                                 u'\n'
                                 u'Error: Invalid value for "-e" / '
                                 u'"--engine": Option is required '
                                 u'and must be specified via the command line.'
                                 u'\n')


class TestDownloadCli:
    @staticmethod
    @mock.patch(
        'dlpx.virtualization._internal.commands.download_logs.download_logs')
    def test_default_params(mock_download_logs, plugin_config_file):
        engine = 'engine'
        user = 'admin'
        password = 'password'
        directory = os.getcwd()

        try:
            os.chdir(os.path.dirname(plugin_config_file))
            runner = click_testing.CliRunner()
            result = runner.invoke(cli.delphix_sdk, [
                'download-logs', '-e', engine, '-u', user, '--password',
                password
            ])
        finally:
            os.chdir(directory)

        assert result.exit_code == 0, 'Output: {}'.format(result.output)
        mock_download_logs.assert_called_once_with(engine, plugin_config_file,
                                                   user, password, directory)

    @staticmethod
    @mock.patch(
        'dlpx.virtualization._internal.commands.download_logs.download_logs')
    def test_valid_params(mock_download_logs, plugin_config_file):
        engine = 'engine'
        user = 'admin'
        password = 'password'
        directory = os.getcwd()

        runner = click_testing.CliRunner()
        result = runner.invoke(cli.delphix_sdk, [
            'download-logs', '-e', engine, '-c', plugin_config_file, '-u',
            user, '-d', directory, '--password', password
        ])

        assert result.exit_code == 0, 'Output: {}'.format(result.output)
        mock_download_logs.assert_called_once_with(engine, plugin_config_file,
                                                   user, password, directory)

    @staticmethod
    def test_missing_params():
        user = 'admin'
        password = 'password'
        directory = os.getcwd()

        runner = click_testing.CliRunner()
        result = runner.invoke(cli.delphix_sdk, [
            'download-logs', '-u', user, '-d', directory, '--password',
            password
        ])

        assert result.exit_code == 2
        assert result.output == (
            u'Usage: delphix-sdk download-logs [OPTIONS]\n'
            u'\n'
            u'Error: Invalid value for "-e" / '
            u'"--engine": Option is required '
            u'and must be specified via the command line.'
            u'\n')

    @staticmethod
    @mock.patch(
        'dlpx.virtualization._internal.commands.download_logs.download_logs')
    def test_bad_password(mock_download_logs, plugin_config_file):
        engine = 'engine'
        user = 'admin'
        password = 'delphix2'
        directory = os.getcwd()
        mock_download_logs.side_effect = exceptions.HttpError(
            401, {
                'type': 'APIError',
                'details': 'Invalid username or password.',
                'action': 'Try with a different set of credentials.',
                'id': 'exception.webservices.login.failed'
            })

        runner = click_testing.CliRunner()
        result = runner.invoke(cli.delphix_sdk, [
            'download-logs', '-e', engine, '-c', plugin_config_file, '-u',
            user, '--password', password, '-d', directory
        ])

        assert result.exit_code == 1
        assert result.output == (
            'API request failed with HTTP Status 401'
            '\nDetails: Invalid username or password.'
            '\nAction: Try with a different set of credentials.'
            '\n')
        mock_download_logs.assert_called_once_with(engine, plugin_config_file,
                                                   user, password, directory)

    @staticmethod
    @pytest.mark.parametrize('directory', ['/not/a/real/directory'])
    def test_directory_not_exist(directory):
        # No mock is needed because we should never call the upload function.
        engine = 'engine'
        user = 'admin'
        password = 'delphix'

        runner = click_testing.CliRunner()
        result = runner.invoke(cli.delphix_sdk, [
            'download-logs', '-e', engine, '-u', user, '--password', password,
            '-d', directory
        ])

        assert result.exit_code == 2
        assert result.output == (
            u'Usage: delphix-sdk download-logs [OPTIONS]'
            u'\nTry "delphix-sdk download-logs -h" for help.'
            u'\n'
            u'\nError: Invalid value for "-d" /'
            u' "--directory": Directory'
            u' "/not/a/real/directory"'
            u' does not exist.'
            u'\n')

    @staticmethod
    @pytest.mark.parametrize('plugin_config_file',
                             ['/not/a/real/file/plugin_config.yml'])
    def test_file_not_exist(plugin_config_file):
        engine = 'engine'
        user = 'admin'
        password = 'delphix'
        directory = os.getcwd()

        runner = click_testing.CliRunner()
        result = runner.invoke(cli.delphix_sdk, [
            'download-logs', '-e', engine, '-c', plugin_config_file, '-u',
            user, '--password', password, '-d', directory
        ])

        assert result.exit_code == 2
        assert result.output == (
            u'Usage: delphix-sdk download-logs [OPTIONS]'
            u'\nTry "delphix-sdk download-logs -h" for help.'
            u'\n'
            u'\nError: Invalid value for "-c" /'
            u' "--plugin-config": File'
            u' "/not/a/real/file/plugin_config.yml"'
            u' does not exist.'
            u'\n')

    @staticmethod
    @mock.patch(
        'dlpx.virtualization._internal.commands.download_logs.download_logs')
    @pytest.mark.usefixtures('dvp_config_file')
    def test_with_config_file_success(mock_download_logs, plugin_config_file,
                                      dvp_config_properties):
        engine = dvp_config_properties['engine']
        user = dvp_config_properties['user']
        password = dvp_config_properties['password']
        cwd = os.getcwd()

        try:
            os.chdir(os.path.dirname(plugin_config_file))
            runner = click_testing.CliRunner()
            result = runner.invoke(cli.delphix_sdk, ['download-logs'])
        finally:
            os.chdir(cwd)

        assert result.exit_code == 0, 'Output: {}'.format(result.output)
        mock_download_logs.assert_called_once_with(engine, plugin_config_file,
                                                   user, password, cwd)

    @staticmethod
    @mock.patch(
        'dlpx.virtualization._internal.commands.download_logs.download_logs')
    @pytest.mark.usefixtures('dvp_config_file')
    def test_with_config_file_override(mock_download_logs, plugin_config_file,
                                       dvp_config_properties):
        engine = dvp_config_properties['engine']
        user = 'fake_admin'
        password = dvp_config_properties['password']
        cwd = os.getcwd()

        try:
            os.chdir(os.path.dirname(plugin_config_file))
            runner = click_testing.CliRunner()
            result = runner.invoke(cli.delphix_sdk,
                                   ['download-logs', '-u', user])
        finally:
            os.chdir(cwd)

        assert result.exit_code == 0, 'Output: {}'.format(result.output)
        mock_download_logs.assert_called_once_with(engine, plugin_config_file,
                                                   user, password, cwd)

    @staticmethod
    @pytest.mark.parametrize('dvp_config_properties', [{
        'user': 'user',
        'password': 'password'
    }])
    @pytest.mark.usefixtures('dvp_config_file')
    def test_with_config_file_fail(plugin_config_file):
        cwd = os.getcwd()

        try:
            os.chdir(os.path.dirname(plugin_config_file))
            runner = click_testing.CliRunner()
            result = runner.invoke(cli.delphix_sdk, ['download-logs'])
        finally:
            os.chdir(cwd)

        assert result.exit_code == 2
        assert result.output == (
            u'Usage: delphix-sdk download-logs [OPTIONS]\n'
            u'\n'
            u'Error: Invalid value for "-e" / '
            u'"--engine": Option is required '
            u'and must be specified via the command line.'
            u'\n')
