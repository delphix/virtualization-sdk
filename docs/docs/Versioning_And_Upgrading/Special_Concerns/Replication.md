# Replication

If the Delphix Engine is setup to replicate data objects to a target engine, there are a few things to consider when uploading a new plugin or upgrading an existing plugin. These considerations are in addition to what a normal upload needs to take into account.

## Delphix Engine Rules

In some cases, a plugin would need an upgrade after a failover operation is done on the target engine.

- After failover, the replicated plugin (now marked as 'inactive') needs an upgrade since its version is lower than the version of the plugin installed on the target Delphix Engine.
- After failover, the live plugin (a.k.a 'active' plugin) needs an upgrade since its version is either lower or not compatible with replicated plugin.

!!! info
    If the replicated and target plugin versions are compatible, failover will automatically merge the plugins and associated objects and there will only be one plugin active.

!!! info
    In some rare cases, a replicated plugin is incompatible with the target plugin even though the target plugin is of a higher version - e.g. target plugin has a data migration that is not present in the replicated plugin or target plugin is built with a lower version of the Virtualization SDK. In such cases, a multi-step upgrade might help.

## Inactive plugin needs upgrade
In most cases, the replicated plugin upgrade is a user initiated operation on the Delphix Engine. However, this operation may fail if the plugins are not compatible. For such a case, a fault (and exception) on the Delphix Engine would indicate that the replicated plugin needs an upgrade and the replicated plugin is marked 'inactive'. As a plugin author, it is a good idea to document the compatibility between the different official releases of a plugin so that a compatible plugin is uploaded.

## Active plugin needs upgrade
In some cases, an active plugin on the target Delphix Engine would need an upgrade to make it compatible with the replicated plugin. Again, as in the case of upgrading a replicated plugin, following [these](/Best_Practices/Replication/Managing_Versions_With_Replication.md) recommendations will help the end user choose the right plugin version to upload.
