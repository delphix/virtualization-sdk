# Plugin Versioning

Like any other piece of software, a plugin will change over time. New features will be added, bugs will be fixed, and so on.

To keep track of this, plugins must specify a version string. There are rules about what sorts of plugin changes go along with changes to the version string. Before we get into the rules, let's talk about a problem that we want to avoid.

## Problems With Data Format Mismatches

Plugins supply [schemas](Glossary.md#schema) to define their own datatypes. Data that conforms to these schemas is saved by the Delphix Engine. Later, the Delphix Engine may read back that saved data, and provide it to plugin code.

Imagine this sequence of events:

1. A plugin is initially released. In its snapshot schema, it defines two properties, `date` and `time`, that together specify when the snapshot was taken.
2. A user installs the initial release of the plugin on their Delphix Engine.
3. The user takes a snapshot of a [dSource](Glossary.md#dsource). Along with this snapshot is stored the `date` and `time`.
4. A new version of the same plugin is released. In this new version, the snapshot schema now only defines a single property called `timestamp`, which specified both the date and the time together in a single property.
5. The user installs the new plugin version.
6. The user attempts to [provision](Glossary.md#provisioning) a new [VDB](Glossary.md#vdb) from the snapshot they took in step 3.

Now, when provision-related plugin code is called (for example the [configure](Plugin_Operations.md#virtual-source-configure) operation), it is going to be handed the snapshot data that was stored in step 2.

The problem here is that we'll have a data format mismatch. The previously-saved snapshot data will have separate `date` and `time` fields, but the new plugin code will be expecting instead a single field called `timestamp`.

## Data Upgrading

**Coming Soon!**

## Versioning Rules

Each plugin declares a version string in the format `<major>.<minor>.<patch>`. The `major` and `minor` parts must always be integers, but `patch` can be any alphanumeric string.

There are two scenarios where one version of a plugin can be installed on an engine that already has another version of the same plugin installed.

### Patch-only Changes

If only the `patch` part of the version is changing, there are a relaxed set of rules:

* Schemas **may not** change.
* There is no defined ordering for patches. So long as `major` and `minor` do not change, any patch level can replace any other patch level.

### Major/Minor Changes

If either `major` or `minor` (or both) is changing, then the following rules are applied:

* The major/minor pair **may not** decrease. If you have version `1.2.x` already installed, then for example you can install `1.3.y` or `2.0.y`. But, you are not allowed to "downgrade" to version `1.1.z`.
* Schemas **may** change.
* The plugin **must** provide upgrade operations so that old-format data can be converted as necessary.
