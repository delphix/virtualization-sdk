#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

import os

import click
from click_configfile import (ConfigFileReader, Param, SectionSchema,
                              matches_section)

CONFIG_DIR_NAME = '.dvp'
CONFIG_FILE_NAME = 'config'


class ConfigSectionSchema(object):
    """
    Describes all possible properties of the configuration file, which will be
    limited to command line options that relate to the delphix engine such as:
    engine, user, and password.
    """
    @matches_section("default")
    class DvpProperties(SectionSchema):
        engine = Param(type=str)
        user = Param(type=str)
        password = Param(type=str)

    @matches_section('dev')
    class DevProperties(SectionSchema):
        vsdk_root = Param(type=str)


class ConfigFileProcessor(ConfigFileReader):
    """
    The config file processor will search for a config file in the current
    user's home directory.
    """
    config_files = [
        os.path.expanduser(os.path.join('~', CONFIG_DIR_NAME,
                                        CONFIG_FILE_NAME))
    ]
    config_section_schemas = [
        ConfigSectionSchema.DvpProperties, ConfigSectionSchema.DevProperties
    ]


def validate_option_exists(ctx, param, value):
    """
    A callback to be used to validate a Click option. Raises a
    click.BadParameter exception if the value is not set or if
    the property name does not exist in the config file.

    This should be used when we want a required optional, but do not want an
    argument. Arguments are ordered and do not come with flags making them
    unwieldy at times, particularly when there is a default. If there are two
    argument, bar and foo in that order, and bar has a default the default
    is useless since if only one parameter is specified Click will fail with
    too few arguments. There is no way with Click arguments to have a flag to
    indicate that the value passed in is meant for foo and not bar. If we want
    this sort of functionality then we are stuck with Click optionals which are
    always optional out of the box.
    """
    if not value and param.name not in ctx.obj.keys():
        # Let the user know if there is an environment variable for this param
        if param.envvar:
            raise click.BadParameter(
                ('Option is required and must be specified via '
                 'the command line or using the environment variable "{}".'.
                 format(param.envvar)))
        else:
            raise click.BadParameter(('Option is required and must be '
                                      'specified via the command line.'))
    return value


class MutuallyExclusiveOption(click.Option):
    """
    A Click Option type that is mutually exclusive with another option. Click
    does not support mutually exclusive options out of the box.

    Example usage:

    @click.command()
    @click.option(
        '-a',
        cls=click_util.MutuallyExclusiveOption,
        is_flag=True,
        mutually_exclusive=['b'])
    @click.option(
        '-b',
        cls=click_util.MutuallyExclusiveOption,
        default='123',
        mutually_exclusive=['a'])
    def command(a, b):
        # do stuff

    All other default Click options can still be specified.

    Two examples of when this would be useful:
    1) Providing quiet and verbose flags. Neither or one, but not both can be
    specified.
    2) From the Dephix SDK's upload command: the commands provides a --plugin
    option that points to an already built artifact. It also provides a -b flag
    to build the plugin before it is uploaded as a convenience. These two
    should not be specified together.
    """
    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop('mutually_exclusive', []))
        super(MutuallyExclusiveOption, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise click.UsageError(
                '"{}" is mutually exclusive with argument(s) "{}".'.format(
                    self.name, ', '.join(self.mutually_exclusive)))

        return super(MutuallyExclusiveOption,
                     self).handle_parse_result(ctx, opts, args)


class PasswordPromptIf(click.Option):
    """
    Remove the need for a prompt if a parameter is already specified via the
    configuration file. This is done by building a custom class derived from
    click.Option and overriding click.Option.handle_parse_result().
    """
    def __init__(self, *args, **kwargs):
        super(PasswordPromptIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        # remove prompt if password exists in configuration file
        if 'password' in ctx.obj.keys():
            self.prompt = None

        return super(PasswordPromptIf,
                     self).handle_parse_result(ctx, opts, args)
