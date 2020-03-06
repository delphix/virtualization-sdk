#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
# flake8: noqa
from dlpx.virtualization.platform import Plugin

plugin = Plugin()


@plugin.upgrade.repository('5.4.0.1')
def repo_upgrade(old_repository):
    return old_repository


@plugin.upgrade.snapshot('5.04.000.01')
def snap_upgrade(old_snapshot):
    return old_snapshot
