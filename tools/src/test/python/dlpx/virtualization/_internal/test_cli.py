#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import os

import click.testing as click_testing
import mock
import pytest

from dlpx.virtualization._internal import cli


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
    @mock.patch('dlpx.virtualization._internal.commands.initialize.init')
    def test_init_default_params(mock_init):
        runner = click_testing.CliRunner()

        result = runner.invoke(cli.delphix_sdk, ['init'])

        assert result.exit_code == 0, 'Output: {}'.format(result.output)

        # 'staged' and os.getcwd() are the expected defaults
        mock_init.assert_called_once_with('staged', os.getcwd())

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.initialize.init')
    def test_init_non_default_params(mock_init):
        runner = click_testing.CliRunner()

        result = runner.invoke(cli.delphix_sdk,
                               ['init', '-t', 'direct', '-r', '.'])

        assert result.exit_code == 0, 'Output: {}'.format(result.output)
        mock_init.assert_called_once_with('direct', os.getcwd())

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.upload.upload')
    def test_upload_valid_params(mock_upload):
        engine = 'engine'
        user = 'admin'
        plugin = 'plugin'
        password = 'password'
        runner = click_testing.CliRunner()

        result = runner.invoke(cli.delphix_sdk, [
            'upload', '-e', engine, '-u', user, '-p', plugin, '--password',
            password
        ])

        assert result.exit_code == 0, 'Output: {}'.format(result.output)
        mock_upload.assert_called_once_with(engine, user, plugin, False,
                                            password)

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
