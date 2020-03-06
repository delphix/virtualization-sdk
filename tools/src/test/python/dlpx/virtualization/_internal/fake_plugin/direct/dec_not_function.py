#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
# flake8: noqa
from __future__ import print_function

import logging

from dlpx.virtualization.platform import Plugin

logger = logging.getLogger()
logger.setLevel(logging.NOTSET)

plugin = Plugin()


@plugin.discovery.repository()
def repository_discovery(source_connection):
    return None


@plugin.discovery.source_config()
def source_config_discovery(source_connection, repository):
    return None


# Defining the decorator as not a function
@plugin.linked.pre_snapshot()
class PreSnapshot(object):
    pass
