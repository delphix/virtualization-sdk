#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

from enum import Enum, unique


@unique
class Operation(Enum):
    DISCOVERY_REPOSITORY = 'discovery.repository()'
    DISCOVERY_SOURCE_CONFIG = 'discovery.source_config()'

    LINKED_PRE_SNAPSHOT = 'linked.pre_snapshot()'
    LINKED_POST_SNAPSHOT = 'linked.post_snapshot()'
    LINKED_START_STAGING = 'linked.start_staging()'
    LINKED_STOP_STAGING = 'linked.stop_staging()'
    LINKED_STATUS = 'linked.status()'
    LINKED_WORKER = 'linked.worker()'
    LINKED_MOUNT_SPEC = 'linked.mount_specification()'

    VIRTUAL_CONFIGURE = 'virtual.configure()'
    VIRTUAL_UNCONFIGURE = 'virtual.unconfigure()'
    VIRTUAL_RECONFIGURE = 'virtual.reconfigure()'
    VIRTUAL_START = 'virtual.start()'
    VIRTUAL_STOP = 'virtual.stop()'
    VIRTUAL_PRE_SNAPSHOT = 'virtual.pre_snapshot()'
    VIRTUAL_POST_SNAPSHOT = 'virtual.post_snapshot()'
    VIRTUAL_STATUS = 'virtual.status()'
    VIRTUAL_INITIALIZE = 'virtual.initialize()'
    VIRTUAL_MOUNT_SPEC = 'virtual.mount_specification()'

    UPGRADE_REPOSITORY = 'upgrade.repository()'
    UPGRADE_SOURCE_CONFIG = 'upgrade.source_config()'
    UPGRADE_LINKED_SOURCE = 'upgrade.linked_source()'
    UPGRADE_VIRTUAL_SOURCE = 'upgrade.virtual_source()'
    UPGRADE_SNAPSHOT = 'upgrade.snapshot()'
