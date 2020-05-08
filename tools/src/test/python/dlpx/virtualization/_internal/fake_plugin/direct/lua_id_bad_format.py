#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
# flake8: noqa
from dlpx.virtualization.platform import MigrationType, Plugin

plugin = Plugin()


@plugin.upgrade.repository('1.0.patchversion', MigrationType.LUA)
def repo_upgrade(old_repository):
    return old_repository
