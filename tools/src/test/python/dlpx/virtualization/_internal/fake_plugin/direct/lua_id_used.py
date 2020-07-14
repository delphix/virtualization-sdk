#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
# flake8: noqa
from dlpx.virtualization.platform import MigrationType, Plugin

plugin = Plugin()


@plugin.upgrade.repository('5.4', MigrationType.LUA)
def repo_upgrade(old_repository):
    return old_repository


@plugin.upgrade.snapshot('5.04', MigrationType.LUA)
def snap_upgrade(old_snapshot):
    return old_snapshot


@plugin.upgrade.repository('5.4', MigrationType.LUA)
def repo_upgrade_two(old_repository):
    return old_repository