# Overview

Once you start writing and releasing your plugin, you’ll reach a point when bug fixes or new features may require schema changes. The plugin upgrade process enables objects that have been created with a prior schema to be migrated to the newly defined schema. When this happens, a new version of the plugin must be created. The following few pages will walk through how versions need to change between upgrades and what needs to be written in the plugin to make sure upgrade is successful.

## Plugin Versioning

Like any other piece of software, plugins change over time. Every so often, there will be a new release. To keep track of the different releases, each plugin release has its own versioning information. Depending on what changes are included in a particular release, there are different rules and recommendations for how the versioning information should be changed. More information on versioning is located [here](Versioning.md).

## Upgrade

Upgrade is the process by which an older version of a plugin is replaced by a newer version. Depending on what has changed between the two versions, this process may also include modifying pre-existing plugin defined objects so they conform to the new schema expected by the new version of the plugin. Information on the upgrade process can be found [here](Upgrade.md).
