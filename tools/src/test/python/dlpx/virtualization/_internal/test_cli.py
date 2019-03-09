#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import os

import click.testing as click_testing
import mock
import pytest
import yaml

from dlpx.virtualization._internal import cli, exceptions, plugin_util


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


class TestCompileCli:
    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.compile.compile')
    def test_compile_default_plugin_file(mock_compile, plugin_config_filename,
                                         plugin_config_content):

        runner = click_testing.CliRunner()
        # Change the runner's working dir to test the default works
        with runner.isolated_filesystem():
            with open(plugin_config_filename, 'w') as f:
                f.write(
                    yaml.dump(plugin_config_content, default_flow_style=False))

            plugin_config_file = os.path.realpath(f.name)
            result = runner.invoke(cli.delphix_sdk, ['compile'])

            assert result.exit_code == 0, 'Output: {}'.format(result.output)
            mock_compile.assert_called_once_with(plugin_config_file)

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.compile.compile')
    def test_compile_valid_params(mock_compile, plugin_config_file):
        runner = click_testing.CliRunner()
        result = runner.invoke(cli.delphix_sdk,
                               ['compile', '-c', plugin_config_file])

        assert result.exit_code == 0, 'Output: {}'.format(result.output)
        mock_compile.assert_called_once_with(plugin_config_file)

    @staticmethod
    @pytest.mark.parametrize('plugin_config_filename', ['plugin.yml'])
    @mock.patch('dlpx.virtualization._internal.commands.compile.compile')
    def test_compile_valid_params_new_name(mock_compile, plugin_config_file):
        runner = click_testing.CliRunner()
        result = runner.invoke(cli.delphix_sdk,
                               ['compile', '-c', plugin_config_file])

        assert result.exit_code == 0, 'Output: {}'.format(result.output)
        mock_compile.assert_called_once_with(plugin_config_file)

    @staticmethod
    @pytest.mark.parametrize('plugin_config_file',
                             ['/not/a/real/file/plugin_config.yml'])
    def test_compile_file_not_exist(plugin_config_file):
        runner = click_testing.CliRunner()
        result = runner.invoke(cli.delphix_sdk,
                               ['compile', '-c', plugin_config_file])

        assert result.exit_code == 2
        assert result.output == (u'Usage: delphix-sdk compile [OPTIONS]'
                                 u'\nTry "delphix-sdk compile -h" for help.'
                                 u'\n'
                                 u'\nError: Invalid value for "-c" /'
                                 u' "--plugin-config": File'
                                 u' "/not/a/real/file/plugin_config.yml"'
                                 u' does not exist.'
                                 u'\n')


class TestBuildCli:
    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.newbuild.build')
    def test_build_default_plugin_file(mock_build, plugin_config_filename,
                                       plugin_config_content, artifact_file):

        runner = click_testing.CliRunner()
        # Change the runner's working dir to test the default works
        with runner.isolated_filesystem():
            with open(plugin_config_filename, 'w') as f:
                f.write(
                    yaml.dump(plugin_config_content, default_flow_style=False))

            plugin_config_file = os.path.realpath(f.name)
            result = runner.invoke(cli.delphix_sdk,
                                   ['newbuild', '-a', artifact_file])

            assert result.exit_code == 0, 'Output: {}'.format(result.output)
            mock_build.assert_called_once_with(plugin_config_file,
                                               artifact_file)


class TestUploadCli:
    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.upload.upload')
    def test_upload_valid_params(mock_upload, artifact_file):
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
    def test_upload_bad_password(mock_upload, artifact_file):
        engine = 'engine'
        user = 'admin'
        password = 'delphix2'
        mock_upload.side_effect = exceptions.HttpPostError(
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
            'Plugin upload failed with HTTP Status 401'
            '\nDetails: Invalid username or password.'
            '\nAction: Try with a different set of credentials.'
            '\n')
        mock_upload.assert_called_once_with(engine, user, artifact_file,
                                            password)

    @staticmethod
    @pytest.mark.parametrize('artifact_file',
                             ['/not/a/real/file/artifact.json'])
    def test_upload_file_not_exist(artifact_file):
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


class TestInitCli:
    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.initialize.init')
    def test_init_default_params(mock_init, plugin_name):
        runner = click_testing.CliRunner()

        result = runner.invoke(cli.delphix_sdk, ['init', '-n', plugin_name])

        assert result.exit_code == 0, 'Output: {}'.format(result.output)

        # 'DIRECT' and os.getcwd() are the expected defaults
        mock_init.assert_called_once_with(os.getcwd(), plugin_name,
                                          plugin_util.DIRECT_TYPE, None)

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.initialize.init')
    def test_init_non_default_params(mock_init, plugin_name,
                                     plugin_pretty_name):
        runner = click_testing.CliRunner()

        result = runner.invoke(cli.delphix_sdk, [
            'init', '-s', plugin_util.STAGED_TYPE, '-r', '.', '-n',
            plugin_name, '--pretty-name', plugin_pretty_name
        ])

        assert result.exit_code == 0, 'Output: {}'.format(result.output)
        mock_init.assert_called_once_with(os.getcwd(), plugin_name,
                                          plugin_util.STAGED_TYPE,
                                          plugin_pretty_name)

    @staticmethod
    def test_init_invalid_ingestion_strategy(plugin_name):
        runner = click_testing.CliRunner()

        result = runner.invoke(
            cli.delphix_sdk,
            ['init', '-n', plugin_name, '-s', 'FAKE_STRATEGY'])

        assert result.exit_code != 0

    @staticmethod
    def test_init_name_required():
        runner = click_testing.CliRunner()

        result = runner.invoke(cli.delphix_sdk, ['init'])

        assert result.exit_code != 0
