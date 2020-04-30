# Compatibility

Before we allow a newly-uploaded plugin to replace an already-installed plugin, we have to make sure that it will not cause any problems.

For example:

* The newly-uploaded plugin must be able to accept any existing data that has been written using the already-installed plugin.
* The user should not unexpectedly lose any features or bug fixes that are present in the already-installed plugin.

These restrictions are enforced by the Delphix Engine, and sometimes, the plugin itself.

## Delphix Engine Rules

The Delphix Engine will enforce these rules before a newly-uploded plugin is allowed to be installed:

* The [build number](/Versioning_And_Upgrade/Versioning.md#build-number) may only move forward, not backwards.
* All [data migration IDs](/References/Glossary.md#data-migration-id) that are present in the already-installed plugin must also be present on the newly-uploaded plugin. The newly-uploaded plugin may add more data migrations, of course.
