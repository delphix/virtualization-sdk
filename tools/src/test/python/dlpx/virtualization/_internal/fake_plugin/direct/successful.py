#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
# flake8: noqa
from dlpx.virtualization.platform import MigrationType, Plugin, Status

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
    path = virtual_source.parameters.path
    name = "VDB mounted to " + path
    return None

@direct.virtual.initialize()
def initialize(virtual_source, repository):
    path = virtual_source.parameters.path
    name = "VDB mounted to " + path
    return None

@direct.virtual.mount_specification()
def mount_specification(repository, virtual_source):
    return None


@direct.virtual.post_snapshot()
def post_snapshot(repository, source_config, virtual_source):
    return None


@direct.virtual.pre_snapshot()
def pre_snapshot(repository, source_config, virtual_source):
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


@direct.upgrade.repository('1.3', MigrationType.LUA)
def repo_upgrade(old_repository):
    return old_repository


@direct.upgrade.snapshot('1.3', MigrationType.LUA)
def snap_upgrade(old_snapshot):
    return old_snapshot


@direct.upgrade.repository('2019.10.30')
def repo_upgrade(old_repository):
    return old_repository


@direct.upgrade.snapshot('2019.11.30')
def snap_upgrade(old_snapshot):
    return old_snapshot
