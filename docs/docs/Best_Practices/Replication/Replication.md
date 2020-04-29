# Overview

When a Delphix Engine is setup for replication to another engine, it can be be configured in a few ways:

- The entire engine could be replicated, which means that all the data objects will be replicated to the target.
- A subset of the objects could be replicated, which means an object/s and its dependencies will be replicated to the target.

In both the cases above, if a data object that belongs to a plugin is replicated, the associated plugin (including metadata like schemas, plugin configuration and its source code) is replicated as well. A replicated plugin and associated objects are available on the target engine for couple of operations:

## Replica Provisioning
Data sources and VDBs that belong to a plugin that are not failed over yet are available to provision a new VDB. When provisioning a VDB from a replicated source object, please note that the plugin that got replicated from the source engine has to be compatible with the plugin that lives on the target plugin.

## Failover
If the replicated and target plugin versions are compatible, failover operation on the Delphix Engine will automatically merge the plugins and associated objects and there will only be one plugin active. In some cases, an upgrade operation post failover is required to consolidate the plugins and enable the replicated plugin objects. For more info, refer to [this link](/Versioning_And_Upgrading/Special_Concerns/Replication.md) for how replication impacts plugin version and upgrade.

!!! info
    A replicated object is said to be in a namespace until a failover operation is performed. The plugin and its objects that are already on the target engine are referred to as the active plugin (and objects) in the below sections.

