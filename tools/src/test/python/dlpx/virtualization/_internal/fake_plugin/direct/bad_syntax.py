#
# Copyright (c) 2020 by Delphix. All rights reserved.
#
# flake8: noqa
from dlpx.virtualization.platform import Plugin

plugin = Plugin()


@plugin.discovery.repository()
def repository_discovery(source_connection)
    return None


@plugin.discovery.source_config()
def source_config_discovery(source_connection, repository)
    return None
