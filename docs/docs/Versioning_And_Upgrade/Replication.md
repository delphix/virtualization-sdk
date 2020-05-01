# Replication
A Delphix Engine (source) can be setup to replicate data objects to another Delphix Engine (target). Plugins built using the Virtualization SDK work seamlessly with Delphix Engine replication with no additional development required from plugin developers.

Only a single version of a plugin can be active on a Delphix Engine at a time. We discuss some basic scenarios below. For more detailed information refer to the [Delphix Engine Documentation](https://docs.delphix.com/docs/).

## Replica Provisioning
Replicated dSource or VDB snapshots can be used to provision new VDBs onto a target Delphix Engine, without failing over any of the objects. When provisioning a VDB from a replicated snapshot:

* A version of the plugin has to be installed on the target Delphix Engine.
* The versions of the plugins installed on the source and target Delphix Engines have to be [compatible](/Versioning_And_Upgrade/Compatibility.md).

Once provisioned, the VDB on the target Delphix Engine will be associated with the version of the plugin installed on the target Delphix Engine, any required data migrations will be run as part of the provisioning process. For more details refer to the [Delphix Engine Documentation](https://docs.delphix.com/docs/).

## Replication Failover
On failover, there are three scenarios for each plugin:

| Scenario | Outcome
| -------- | -------
Source plugin **not installed** on target Delphix Engine | The plugin will be failed over and marked as `active` on the target Delphix Engine.
Source plugin version **is equal to** the target plugin version | The plugin from the source will be merged with the plugin on the target Delphix Engine.
Source plugin version **is not equal to** the target plugin version | The plugin from the source will be marked `inactive` on the target Delphix Engine. An `inactive` plugin can be subsequently activated, after failover, if it is [compatible](/Versioning_And_Upgrade/Compatibility.md) with the existing `active` plugin. Activating a plugin will do an upgrade and merge the `inactive` plugin, and all its associated objects, with the `active` plugin. For more details refer to the [Delphix Engine Documentation](https://docs.delphix.com/docs/).