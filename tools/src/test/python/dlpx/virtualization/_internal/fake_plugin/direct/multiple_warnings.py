#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
# flake8: noqa
from dlpx.virtualization.platform import Plugin, Status

vfiles = Plugin()


@vfiles.discovery.repository()
def repository_discovery(source_connection):
    return []


@vfiles.discovery.source_config()
def source_config_discovery(source_connection, repository):
    return []


@vfiles.linked.pre_snapshot()
def direct_pre_snapshot(direct_source, repository, source_config,
                        optional_snapshot_parameters):
    return


@vfiles.linked.post_snapshot()
def direct_post_snapshot(direct_source, repository, source_config,
                         optional_snapshot_parameters):
    return None


@vfiles.virtual.configure()
def configure(virtual_source, repository, snapshot):
    path = virtual_source.parameters.path
    name = "VDB mounted to " + path
    return None


@vfiles.virtual.mount_specification()
def mount_specification(repository, virtual_source):
    return None


@vfiles.virtual.post_snapshot()
def post_snapshot(repository, source_config, virtual_source):
    return None


@vfiles.virtual.pre_snapshot()
def pre_snapshot(repository, source_config, virtual_source):
    pass


# Removed virtual.reconfigure for required methods check test.


@vfiles.virtual.start()
def start(repository, source_config, virtual_source):
    pass


# Added snapshot arg to check if named arg check fails.
@vfiles.virtual.status()
def status(repository, source_config, virtual_source, snapshot):
    return Status.ACTIVE


@vfiles.virtual.stop()
def stop(repository, source_config, virtual_source):
    pass


@vfiles.virtual.unconfigure()
def unconfigure(repository, source_config, virtual_source):
    pass


@vfiles.virtual.cleanup()
def cleanup(repository, source_config, virtual_source, bad_arg):
    pass


@vfiles.upgrade.repository('2019.10.30')
def repo_upgrade(old_repository):
    return old_repository
