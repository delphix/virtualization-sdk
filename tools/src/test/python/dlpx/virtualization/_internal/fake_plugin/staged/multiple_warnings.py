#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
# flake8: noqa
from __future__ import print_function

import logging

from dlpx.virtualization.platform import Plugin

logger = logging.getLogger()
logger.setLevel(logging.NOTSET)

staged = Plugin()


# Renamed source_connection to connection to test if named arg check detects.
@staged.discovery.repository()
def repository_discovery(connection):
    return []


@staged.discovery.source_config()
def source_config_discovery(source_connection, repository):
    return []


@staged.linked.mount_specification()
def staged_mount_specification(staged_source, repository):
    return None


@staged.linked.pre_snapshot()
def staged_pre_snapshot(repository, source_config, staged_source,
                        optional_snapshot_parameters):
    pass


@staged.linked.post_snapshot()
def staged_post_snapshot(repository, source_config, staged_source,
                         optional_snapshot_parameters):
    return None


@staged.linked.start_staging()
def start_staging(repository, source_config, staged_source):
    pass


@staged.linked.stop_staging()
def stop_staging(repository, source_config, staged_source):
    pass


@staged.linked.status()
def staged_status(staged_source, repository, source_config):
    return None


@staged.linked.worker()
def staged_worker(repository, source_config, staged_source):
    pass


@staged.virtual.configure()
def configure(virtual_source, repository, snapshot):
    return None


@staged.virtual.reconfigure()
def reconfigure(virtual_source, repository, source_config, snapshot):
    return None


# Removed virtual.mount_specification for test validation.


@staged.virtual.pre_snapshot()
def pre_snapshot(repository, source_config, virtual_source):
    pass


@staged.virtual.post_snapshot()
def post_snapshot(repository, source_config, virtual_source):
    return None


@staged.virtual.start()
def start(repository, source_config, virtual_source):
    pass


# Added snapshot parameter to check if arg check fails.
@staged.virtual.stop()
def stop(repository, source_config, virtual_source, snapshot):
    pass


@staged.upgrade.repository('2019.10.30')
def repo_upgrade(old_repository):
    return old_repository
