#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import click
import pytest
from click import testing as click_testing

from dlpx.virtualization._internal import click_util


class TestClickUtil:
    @staticmethod
    def test_mutually_exclusive_options_success():
        @click.command()
        @click.option(
            '-a',
            cls=click_util.MutuallyExclusiveOption,
            mutually_exclusive=['b'])
        @click.option(
            '-b',
            cls=click_util.MutuallyExclusiveOption,
            mutually_exclusive=['a'])
        def test_command(a, b):
            click.echo(a)

        runner = click_testing.CliRunner()

        result = runner.invoke(test_command, ['-a', 'arg'])

        assert result.exit_code == 0
        assert result.output == 'arg\n'

    @staticmethod
    def test_mutually_exclusive_options_failed():
        @click.command()
        @click.option(
            '-a',
            is_flag=True,
            cls=click_util.MutuallyExclusiveOption,
            mutually_exclusive=['b'])
        @click.option(
            '-b',
            is_flag=True,
            cls=click_util.MutuallyExclusiveOption,
            mutually_exclusive=['a'])
        def test_command(a, b):
            pass

        runner = click_testing.CliRunner()

        result = runner.invoke(test_command, ['-a', '-b'])

        assert result.exit_code != 0

    @staticmethod
    def test_validate_option_exists_with_value():
        expected = 'arg'

        actual = click_util.validate_option_exists(
            None, click.Option(param_decls=['-a']), expected)

        assert actual == expected

    @staticmethod
    def test_validate_option_exists_without_value():
        with pytest.raises(click.BadParameter):
            click_util.validate_option_exists(None,
                                              click.Option(param_decls=['-a']),
                                              None)

    @staticmethod
    def test_validate_option_exists_without_value_with_envvar_option():
        envvar = 'DELPHIX_ENVVAR'
        with pytest.raises(click.BadParameter) as excinfo:
            click_util.validate_option_exists(
                None, click.Option(param_decls=['-a'], envvar=envvar), None)

        # Check that the exception message includes the environment variable
        assert envvar in str(excinfo.value)
