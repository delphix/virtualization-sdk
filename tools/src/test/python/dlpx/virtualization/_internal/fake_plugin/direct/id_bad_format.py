#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
# flake8: noqa
from dlpx.virtualization.platform import Plugin

plugin = Plugin()


@plugin.upgrade.repository('1234.0.0.')
def repo_upgrade(old_repository):
    return old_repository
