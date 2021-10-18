#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
# flake8: noqa
from dlpx.virtualization.platform import Plugin, Status

direct = Plugin()


@direct.discovery.repository()
def repository_discovery(source_connection):
    return []


@direct.discovery.source_config()
def source_config_discovery(source_connection, repository):
    return []


@direct.linked.pre_snapshot()
def direct_pre_snapshot(direct_source, repository, source_config,
                        optional_snapshot_parameters):
    return


@direct.linked.post_snapshot()
def direct_post_snapshot(direct_source, repository, source_config,
                         optional_snapshot_parameters):
    return None


@direct.virtual.configure()
def configure(virtual_source, repository, snapshot):
    return None


@direct.virtual.mount_specification()
def mount_specification(repository, virtual_source):
    return None


@direct.virtual.post_snapshot()
def postSnapshot(repository, source_config, virtual_source):
    return None


@direct.virtual.pre_snapshot()
def preSnapshot(repository, source_config, virtual_source):
    pass


@direct.virtual.reconfigure()
def reconfigure(virtual_source, repository, source_config, snapshot):
    pass


@direct.virtual.start()
def start(repository, source_config, virtual_source):
    pass


@direct.virtual.status()
def status(repository, source_config, virtual_source):
    return Status.ACTIVE


@direct.virtual.stop()
def stop(repository, source_config, virtual_source):
    pass


@direct.virtual.unconfigure()
def unconfigure(repository, source_config, virtual_source):
    pass


@direct.virtual.cleanup()
def cleanup(repository, source_config, virtual_source):
    pass


@direct.upgrade.repository('2019.11.20')
def repo_upgrade(old_repository):
    return old_repository


@direct.upgrade.source_config('2019.11.22')
def sc_upgrade(old_source_config):
    return old_source_config


# Added second arg to check if length arg check fails.
@direct.upgrade.linked_source('2019.11.24')
def ls_upgrade(old_linked, old_source):
    return old_linked


# Renamed old_virtual_source to old_linked_source to test named arg checks.
@direct.upgrade.virtual_source('2019.11.26')
def ls_upgrade(old_linked_source):
    return old_linked_source


# Renamed old_snapshot to bad_input_name to test named arg checks.
@direct.upgrade.snapshot('2019.11.30')
def snap_upgrade(bad_input_name):
    return bad_input_name
