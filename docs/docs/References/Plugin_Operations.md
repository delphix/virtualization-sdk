# Plugin Operations

## Summary
!!! warning
    If a Plugin Operation is **Required** and is not present, the corresponding Delphix Engine Operation will fail when invoked. The plugin can still be built and uploaded to the Delphix Engine.

!!! warning
    For each operation, the argument names must match exactly. For example, the Repository Discovery
    operation must have a single argument named `source_connection`.

Plugin Operation | **Required** | Decorator | Delphix Engine Operations
---------------- | -------- | --------- | -------------------------
[Repository<br/>Discovery](#repository-discovery) | **Yes** |`discovery.repository()` | [Environment Discovery](Workflows.md#environment-discovery-refresh)<br/>[Environment Refresh](Workflows.md#environment-discovery-refresh)
[Source Config<br/>Discovery](#source-config-discovery) | **Yes** |`discovery.source_config()` | [Environment Discovery](Workflows.md#environment-discovery-refresh)<br/>[Environment Refresh](Workflows.md#environment-discovery-refresh)
[Direct Linked Source<br/>Pre-Snapshot](#direct-linked-source-pre-snapshot) | **No** | `linked.pre_snapshot()` | [Linked Source Sync](Workflows.md#linked-source-sync)
[Direct Linked Source<br/>Post-Snapshot](#direct-linked-source-post-snapshot) | **Yes** | `linked.post_snapshot()` | [Linked Source Sync](Workflows.md#linked-source-sync)
[Staged Linked Source<br/>Pre-Snapshot](#staged-linked-source-pre-snapshot) | **No** | `linked.pre_snapshot()` | [Linked Source Sync](Workflows.md#linked-source-sync)
[Staged Linked Source<br/>Post-Snapshot](#staged-linked-source-post-snapshot) | **Yes** | `linked.post_snapshot()` | [Linked Source Sync](Workflows.md#linked-source-sync)
[Staged Linked Source<br/>Start-Staging](#staged-linked-source-start-staging) | **No** | `linked.start_staging()` | [Linked Source Enable](Workflows.md#linked-source-enable)
[Staged Linked Source<br/>Stop-Staging](#staged-linked-source-stop-staging) | **No** | `linked.stop_staging()` | [Linked Source Disable](Workflows.md#linked-source-disable)<br/>[Linked Source Delete](Workflows.md#linked-source-delete)
[Staged Linked Source<br/>Status](#staged-linked-source-status) | **No** |`linked.status()` | N/A
[Staged Linked Source<br/>Worker](#staged-linked-source-worker) | **No** |`linked.worker()` | N/A
[Staged Linked Source<br/>Mount Specification](#staged-linked-source-mount-specification) | **Yes** | `linked.mount_specification()` | [Linked Source Sync](Workflows.md#linked-source-sync)<br/>[Linked Source Enable](Workflows.md#linked-source-enable)
[Virtual Source<br/>Initialize](#virtual-source-initialize) | **No** | `virtual.initialize()` | [Virtual Source Create Empty VDB](Workflows.md#virtual-source-create-empty-vdb)
[Virtual Source<br/>Configure](#virtual-source-configure) | **Yes** | `virtual.configure()` | [Virtual Source Provision](Workflows.md#virtual-source-provision)<br/>[Virtual Source Refresh](Workflows.md#virtual-source-refresh)
[Virtual Source<br/>Unconfigure](#virtual-source-unconfigure) | **No** | `virtual.unconfigure()` | [Virtual Source Refresh](Workflows.md#virtual-source-refresh)<br/>[Virtual Source Delete](Workflows.md#virtual-source-delete)
[Virtual Source<br/>Reconfigure](#virtual-source-reconfigure) | **Yes** | `virtual.reconfigure()` | [Virtual Source Rollback](Workflows.md#virtual-source-rollback)<br/>[Virtual Source Enable](Workflows.md#virtual-source-enable)
[Virtual Source<br/>Cleanup](#virtual-source-cleanup) | **No** | `virtual.cleanup()` | [Virtual Source Delete](Workflows.md#virtual-source-delete)
[Virtual Source<br/>Start](#virtual-source-start) | **No** | `virtual.start()` | [Virtual Source Start](Workflows.md#virtual-source-start)
[Virtual Source<br/>Stop](#virtual-source-stop) | **No** | `virtual.stop()` | [Virtual Source Stop](Workflows.md#virtual-source-stop)
[Virtual Source<br/>Pre-Snapshot](#virtual-source-pre-snapshot) | **No** | `virtual.pre_snapshot()` | [Virtual Source Snapshot](Workflows.md#virtual-source-snapshot)
[Virtual Source<br/>Post-Snapshot](#virtual-source-post-snapshot) | **Yes** | `virtual.post_snapshot()` | [Virtual Source Snapshot](Workflows.md#virtual-source-snapshot)
[Virtual Source<br>Mount Specification](#virtual-source-mount-specification) | **Yes** | `virtual.mount_specification()` | [Virtual Source Enable](Workflows.md#virtual-source-enable)<br/>[Virtual Source Provision](Workflows.md#virtual-source-provision)<br/>[Virtual Source Refresh](Workflows.md#virtual-source-refresh)<br/>[Virtual Source Rollback](Workflows.md#virtual-source-rollback)<br/>[Virtual Source Start](Workflows.md#virtual-source-start)
[Virtual Source<br/>Status](#virtual-source-status) | **No** | `virtual.status()` | [Virtual Source Enable](Workflows.md#virtual-source-enable)
[Repository Data Migration](#repository-data-migration) | **No** | `upgrade.repository(migration_id)` | [Upgrade](Workflows.md#upgrade)
[Source Config Data Migration](#source-config-data-migration) | **No** | `upgrade.source_config(migration_id)` | [Upgrade](Workflows.md#upgrade)
[Linked Source Data Migration](#linked-source-data-migration) | **No** | `upgrade.linked_source(migration_id)` | [Upgrade](Workflows.md#upgrade)
[Virtual Source Data Migration](#virtual-source-data-migration) | **No** | `upgrade.virtual_source(migration_id)` | [Upgrade](Workflows.md#upgrade)
[Snapshot Data Migration](#snapshot-data-migration) | **No** | `upgrade.snapshot(migration_id)` | [Upgrade](Workflows.md#upgrade)


## Repository Discovery

Discovers the set of [repositories](Glossary.md#repository) for a plugin on an [environment](Glossary.md#environment). For a DBMS, this can correspond to the set of binaries installed on a Unix host.

### Required / Optional
**Required.**

### Delphix Engine Operations

* [Environment Refresh](Workflows.md#environment-discovery-refresh)
* [Environment Discovery](Workflows.md#environment-discovery-refresh)

### Signature

`def repository_discovery(source_connection)`

### Decorator

`discovery.repository()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
source_connection | [RemoteConnection](Classes.md#remoteconnection) | The connection associated with the remote environment to run repository discovery

### Returns

A list of [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) objects.

### Example

```python
from dlpx.virtualization.platform import Plugin
from generated.defintions import RepositoryDefinition

plugin = Plugin()

@plugin.discovery.repository()
def repository_discovery(source_connection):
  # Initialize the object, filling in all required fields
  repository = RepositoryDefinition(installPath="/usr/bin/install")
  # Set any additional non-required properties
  repository.version = "1.2.3"
  # Return one single repository
  return [repository]
```

> The above command assumes a [Repository Schema](Schemas_and_Autogenerated_Classes.md#repositorydefinition-schema) defined as:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["installPath"],
  "properties": {
    "installPath": { "type": "string" },
    "version": { "type": "string" }
  },
  "identityFields": ["installPath"],
  "nameField": ["installPath"]    
}
```


## Source Config Discovery

Discovers the set of [source configs](Glossary.md#source-config) for a plugin for a [repository](Glossary.md#repository). For a DBMS, this can correspond to the set of unique databases running using a particular installation on a Unix host.

### Required / Optional
**Required.**

### Delphix Engine Operations

* [Environment Refresh](Workflows.md#environment-discovery-refresh)
* [Environment Discovery](Workflows.md#environment-discovery-refresh)

### Signature

`def source_config_discovery(source_connection, repository)`

### Decorator

`discovery.source_config()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
source_connection | [RemoteConnection](Classes.md#remoteconnection) | The connection to the remote environment the corresponds to the repository.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository to discover source configs for.

### Returns
A list of [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class) objects.

### Example

```python
from dlpx.virtualization.platform import Plugin
from generated.definitions import SourceConfigDefinition

plugin = Plugin()

@plugin.discovery.source_config()
def source_config_discovery(source_connection, repository):
  source_config = SourceConfigDefinition(name="my_name", port=1000)
  return [source_config]
```

> The above command assumes a [Source Config Schema](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-schema) defined as:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["name"],
  "properties": {
    "name": { "type": "string" },
    "port": { "type": "number" }
  },
  "identityFields": ["name"],
  "nameField": ["name"]    
}
```

## Direct Linked Source Pre-Snapshot

Sets up a [dSource](Glossary.md#dsource) to ingest data. Only applies when using a [Direct Linking](Glossary.md#direct-linking) strategy.

### Required / Optional
**Optional**

### Delphix Engine Operations

* [Linked Source Sync](Workflows.md#linked-source-sync)

### Signature

`def linked_pre_snapshot(direct_source, repository, source_config, optional_snapshot_parameters)`

### Decorator

`linked.pre_snapshot()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
direct_source | [DirectSource](Classes.md#directsource) | The source associated with this operation.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.
source_config | [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class) | The source config associated with this source.
optional_snapshot_parameters | [SnapshotParametersDefinition](Classes.md#snapshotparametersdefinition) | The snapshot parameters. The value is `None` when executed during a snapshot policy.

### Returns
None

### Example

```python
from dlpx.virtualization.platform import Plugin
from generated.definitions import SourceConfigDefinition

plugin = Plugin()

@plugin.linked.pre_snapshot()
def linked_pre_snapshot(direct_source, repository, source_config):
  pass
```

## Direct Linked Source Post-Snapshot

Captures metadata from a [dSource](Glossary.md#dsource) once data has been ingested. Only applies when using a [Direct Linking](Glossary.md#direct-linking) strategy.

### Required / Optional
**Required.**

### Delphix Engine Operations

* [Linked Source Sync](Workflows.md#linked-source-sync)

### Signature

`def linked_post_snapshot(direct_source, repository, source_config, optional_snapshot_parameters)`

### Decorator

`linked.post_snapshot()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
direct_source | [DirectSource](Classes.md#directsource) | The source associated with this operation.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.
source_config | [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class) | The source config associated with this source.
optional_snapshot_parameters | [SnapshotParametersDefinition](Classes.md#snapshotparametersdefinition) | The snapshot parameters. The value is `None` when executed during a snapshot policy.

### Returns
[SnapshotDefinition](Schemas_and_Autogenerated_Classes.md#snapshotdefinition-class)

### Example

```python
from dlpx.virtualization.platform import Plugin
from generated.definitions import SnapshotDefinition

plugin = Plugin()

@plugin.linked.post_snapshot()
def linked_post_snapshot(direct_source, repository, source_config, optional_snapshot_parameters):
  snapshot = SnapshotDefinition()
  snapshot.transaction_id = 1000
  return snapshot
```

> The above command assumes a [Snapshot Schema](Schemas_and_Autogenerated_Classes.md#snapshot-schema) defined as:

```json
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "transactionId": { "type": "integer" }
  }
}
```

## Staged Linked Source Pre-Snapshot

Sets up a [dSource](Glossary.md#dsource) to ingest data. Only applies when using a [Staged Linking](Glossary.md#staged-linking) strategy.

### Required / Optional
**Optional.**

### Delphix Engine Operations

* [Linked Source Sync](Workflows.md#linked-source-sync)

### Signature

`def linked_pre_snapshot(staged_source, repository, source_config, optional_snapshot_parameters)`

### Decorator

`linked.pre_snapshot()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
staged_source | [StagedSource](Classes.md#stagedsource) | The source associated with this operation.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.
source_config | [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class) | The source config associated with this source.
optional_snapshot_parameters | [SnapshotParametersDefinition](Classes.md#snapshotparametersdefinition) | The snapshot parameters. The value is `None` when executed during a snapshot policy.

### Returns
None

### Example

```python
from dlpx.virtualization.platform import Plugin

plugin = Plugin()

@plugin.linked.pre_snapshot()
def linked_pre_snapshot(staged_source, repository, source_config, optional_snapshot_parameters):
  pass
```

## Staged Linked Source Post-Snapshot

Captures metadata from a [dSource](Glossary.md#dsource) once data has been ingested. Only applies when using a [Staged Linking](Glossary.md#staged-linking) strategy.

### Required / Optional
**Required.**

### Delphix Engine Operations

* [Linked Source Sync](Workflows.md#linked-source-sync)

### Signature

`def linked_post_snapshot(staged_source, repository, source_config, optional_snapshot_parameters)`

### Decorator

`linked.post_snapshot()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
staged_source | [StagedSource](Classes.md#stagedsource) | The source associated with this operation.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.
source_config | [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class) | The source config associated with this source.
optional_snapshot_parameters | [SnapshotParametersDefinition](Classes.md#snapshotparametersdefinition) | The snapshot parameters. The value is `None` when executed during a snapshot policy.

### Returns
[SnapshotDefinition](Schemas_and_Autogenerated_Classes.md#snapshotdefinition-class)

### Example

```python
from dlpx.virtualization.platform import Plugin
from generated.definitions import SnapshotDefinition

plugin = Plugin()

@plugin.linked.post_snapshot()
def linked_post_snapshot(staged_source, repository, source_config, optional_snapshot_parameters):
  snapshot = SnapshotDefinition()
  if optional_snapshot_parameters is not None and optional_snapshot_parameters.resync:
    snapshot.transaction_id = 1000
  else:
    snapshot.transaction_id = 10
  return snapshot
```

> The above command assumes a [Snapshot Schema](Schemas_and_Autogenerated_Classes.md#snapshot-schema) defined as:

```json
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "transactionId": { "type": "integer" }
  }
}
```

## Staged Linked Source Start-Staging

Sets up a [Staging Source](Glossary.md#staging-source) to ingest data. Only applies when using a [Staged Linking](Glossary.md#staged-linking) strategy.
Required to implement for Delphix Engine operations:

### Required / Optional
**Optional.**

### Delphix Engine Operations

* [Linked Source Enable](Workflows.md#linked-source-enable)

### Signature

`def start_staging(staged_source, repository, source_config)`

### Decorator

`linked.start_staging()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
staged_source | [StagedSource](Classes.md#stagedsource) | The source associated with this operation.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.
source_config | [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class) | The source config associated with this source.

### Returns
None

### Example

```python
from dlpx.virtualization.platform import Plugin

plugin = Plugin()

@plugin.linked.start_staging()
def start_staging(staged_source, repository, source_config):
  pass
```


## Staged Linked Source Stop-Staging

Quiesces a [Staging Source](Glossary.md#staging-source) to pause ingestion. Only applies when using a [Staged Linking](Glossary.md#staged-linking) strategy.

### Required / Optional
**Optional.**

### Delphix Engine Operations

* [Linked Source Disable](Workflows.md#linked-source-disable)
* [Linked Source Delete](Workflows.md#linked-source-delete)

### Signature

`def stop_staging(staged_source, repository, source_config)`

### Decorator

`linked.stop_staging()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
staged_source | [StagedSource](Classes.md#stagedsource) | The source associated with this operation.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.
source_config | [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class) | The source config associated with this source.

### Returns
None

###Examples

```python
from dlpx.virtualization.platform import Plugin

plugin = Plugin()

@plugin.linked.stop_staging()
def stop_staging(staged_source, repository, source_config):
  pass
```

## Staged Linked Source Status

Determines the status of a [Staging Source](Glossary.md#staging-source) to show end users whether it is healthy or not. Only applies when using a [Staged Linking](Glossary.md#staged-linking) strategy.

### Required / Optional
**Optional.**<br/>
If not implemented, the platform assumes that the status is `Status.ACTIVE`

### Delphix Engine Operations

N/A

### Signature

`def linked_status(staged_source, repository, source_config)`

### Decorator

`linked.status()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
staged_source | [StagedSource](Classes.md#stagedsource) | The source associated with this operation.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.
source_config | [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class) | The source config associated with this source.

### Returns
[Status](Classes.md#status)<br/>
`Status.ACTIVE` if the plugin operation is not implemented.

### Example

```python
from dlpx.virtualization.platform import Plugin
from dlpx.virtualization.platform import Status

plugin = Plugin()

@plugin.linked.status()
def linked_status(staged_source, repository, source_config):
  return Status.ACTIVE
```

## Staged Linked Source Worker

Monitors the status of a [Staging Source](Glossary.md#staging-source) on a reqular interval. It can be used to fix up any errors on staging if it is not functioning as expected. Only applies when using a [Staged Linking](Glossary.md#staged-linking) strategy.

### Required / Optional
**Optional.**

### Delphix Engine Operations

N/A

### Signature

`def worker(staged_source, repository, source_config)`

### Decorator

`linked.worker()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
staged_source | [StagedSource](Classes.md#stagedsource) | The source associated with this operation.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.
source_config | [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class) | The source config associated with this source.

### Returns
None

### Example

```python
from dlpx.virtualization.platform import Plugin

plugin = Plugin()

@plugin.linked.worker()
def worker(staged_source, repository, source_config):
  pass
```

## Staged Linked Source Mount Specification

Returns configurations for the mounts associated for data in staged source. The `ownership_specification` is optional. If not specified, the platform will default the ownership settings to the environment user used for the Delphix Operation.

### Required / Optional
**Required.**

### Delphix Engine Operations

* [Linked Source Sync](Workflows.md#linked-source-sync)
* [Linked Source Enable](Workflows.md#linked-source-enable)

### Signature

`def linked_mount_specification(staged_source, repository)`

### Decorator

`linked.mount_specification()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
staged_source | [StagedSource](Classes.md#stagedsource) | The source associated with this operation.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.

### Returns
[MountSpecification](Classes.md#mountspecification)

### Example

!!! info
    `ownership_specification` only applies to Unix hosts.

```python
from dlpx.virtualization.platform import Plugin
from dlpx.virtualization.platform import Mount
from dlpx.virtualization.platform import MountSpecification
from dlpx.virtualization.platform import OwenershipSpecification
from generated.definitions import SnapshotDefinition

plugin = Plugin()

@plugin.linked.mount_specification()
def linked_mount_specification(staged_source, repository):
  mount = Mount(staged_source.staged_connection.environment, "/some/path")
  ownership_spec = OwenershipSpecification(repository.uid, repository.gid)

  return MountSpecification([mount], ownership_spec)
```

## Virtual Source Initialize

Initializes a brand-new [empty VDB](Glossary.md#empty-vdb). As with all VDBs, this new dataset will have access to mounted Delphix Engine storage, but of course there will be no data there at first.

The job of the plugin is to do whatever is necessary to set up a new dataset from scratch. For example, this might involve running a `CREATE DATABASE` command.  This is an optional operation -- users will not be allowed to create empty VDBs for plugins that choose not to implement this operation.

As with the `configure` operation, this `initialize` operation must return source config parameters that represent the new dataset.

### Required / Optional
**Optional.**

### Delphix Engine Operations

* [Virtual Source Create Empty VDB](Workflows.md#virtual-source-create-empty-vdb)

### Signature

`def initialize(virtual_source, repository)`

### Decorator

`virtual.initialize()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
virtual_source | [VirtualSource](Classes.md#virtualsource) | The source associated with this operation.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.

### Returns
[SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class)

### Example

```python
from dlpx.virtualization.platform import Plugin
from generated.defintions import SourceConfigDefinition

plugin = Plugin()

@plugin.virtual.initialize()
def initialize(virtual_source, repository):
  source_config = SourceConfigDefinition(name="config_name")
  return source_config
```

> The above command assumes a [SourceConfig Schema](Schemas_and_Autogenerated_Classes.md#sourceconfig-schema) defined as:

```json
{
  "type": "object",
  "required": ["name"],
  "additionalProperties": false,
  "properties": {
    "name": { "type": "string" }
  },
  "identityFields": ["name"],
  "nameField": ["name"]
}
```

## Virtual Source Configure

Configures the data in a particular snapshot to be usable on a target environment. For database data files, this may mean recovering from a crash consistent format or backup. For application files, this may mean reconfiguring XML files or rewriting hostnames and symlinks.

### Required / Optional
**Required.**

### Delphix Engine Operations

* [Virtual Source Provision](Workflows.md#virtual-source-provision)
* [Virtual Source Refresh](Workflows.md#virtual-source-refresh)

### Signature

`def configure(virtual_source, snapshot, repository)`

### Decorator

`virtual.configure()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
virtual_source | [VirtualSource](Classes.md#virtualsource) | The source associated with this operation.
snapshot | [SnapshotDefinition](Schemas_and_Autogenerated_Classes.md#snapshotdefinition-class) | The snapshot of the data set to configure.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.

### Returns
[SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class)

### Example

```python
from dlpx.virtualization.platform import Plugin
from generated.defintions import SourceConfigDefinition

plugin = Plugin()

@plugin.virtual.configure()
def configure(virtual_source, repository, snapshot):
  source_config = SourceConfigDefinition(name="config_name")
  return source_config
```

> The above command assumes a [SourceConfig Schema](Schemas_and_Autogenerated_Classes.md#sourceconfig-schema) defined as:

```json
{
  "type": "object",
  "required": ["name"],
  "additionalProperties": false,
  "properties": {
    "name": { "type": "string" }
  },
  "identityFields": ["name"],
  "nameField": ["name"]
}
```

## Virtual Source Unconfigure

Prepares for the removal of virtual source data from a target host. Depending on your dataset, this might involve unregistering this dataset from the DBMS, modifying/deleting config files on the remote host, etc.

It's important to clean up anything VDB-specific from the target host during this operation. For example, if you've stored such data in the [scratch path](/Best_Practices/Scratch_Paths), then you should delete it during unconfigure.

### Required / Optional
**Optional.**

### Delphix Engine Operations

* [Virtual Source Refresh](Workflows.md#virtual-source-refresh)
* [Virtual Source Delete](Workflows.md#virtual-source-delete)
* [Virtual Source Disable](Workflows.md#virtual-source-disable)

### Signature

`def unconfigure(virtual_source, repository, source_config)`

### Decorator

`virtual.unconfigure()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
virtual_source | [VirtualSource](Classes.md#virtualsource) | The source associated with this operation.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.
source_config | [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class) | The source config associated with this source.

### Returns
None

### Example

```python
from dlpx.virtualization.platform import Plugin

plugin = Plugin()

@plugin.virtual.unconfigure()
def unconfigure(virtual_source, repository, source_config):
  pass
```

## Virtual Source Reconfigure

Re-configures the data for a virtual source to point to the data in a prior snapshot for the virtual source. For database data files, this may mean recovering from a crash consistent format or backup of a new snapshot. For application files, this may mean reconfiguring XML files or rewriting hostnames and symlinks.

### Required / Optional
**Required.**

### Delphix Engine Operations

* [Virtual Source Rollback](Workflows.md#virtual-source-rollback)
* [Virtual Source Enable](Workflows.md#virtual-source-enable)

### Signature

`def reconfigure(virtual_source, repository, source_config, snapshot)`

### Decorator

`virtual.reconfigure()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
virtual_source | [VirtualSource](Classes.md#virtualsource) | The source associated with this operation.
snapshot | [SnapshotDefinition](Schemas_and_Autogenerated_Classes.md#snapshotdefinition-class) | The snapshot of the data set to configure.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.
source_config | [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class) | The source config associated with this source.

### Returns
[SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class)

### Example

```python
from dlpx.virtualization.platform import Plugin
from generated.definitions import SourceConfigDefinition

plugin = Plugin()

@plugin.virtual.reconfigure()
def reconfigure(virtual_source, repository, source_config, snapshot):
  return SourceConfigDefinition(name="updated_config_name")
```

> The above command assumes a [SourceConfig Schema](Schemas_and_Autogenerated_Classes.md#sourceconfig-schema) defined as:

```json
{
  "type": "object",
  "required": ["name"],
  "additionalProperties": false,
  "properties": {
    "name": { "type": "string" }
  },
  "identityFields": ["name"],
  "nameField": ["name"]
}
```

## Virtual Source Cleanup

Intended to allow a final cleanup during a delete operation, unlike unconfigure which can be used to signal a temporary dissassociation with a database.

Cleanup is called during the delete flow after unconfigure.

### Required / Optional
**Optional.**

### Delphix Engine Operations

* [Virtual Source Delete](Workflows.md#virtual-source-delete)

### Signature

`def cleanup(virtual_source, repository, source_config)`

### Decorator

`virtual.cleanup()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
virtual_source | [VirtualSource](Classes.md#virtualsource) | The source associated with this operation.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.
source_config | [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class) | The source config associated with this source.

### Returns
None

### Example

```python
from dlpx.virtualization.platform import Plugin

plugin = Plugin()

@plugin.virtual.cleanup()
def cleanup(virtual_source, repository, source_config):
  pass
```

## Virtual Source Start

Executed whenever the data should be placed in a "running" state.

### Required / Optional
**Optional.**

### Delphix Engine Operations

* [Virtual Source Start](Workflows.md#virtual-source-start)

### Signature

`def start(virtual_source, repository, source_config)`

### Decorator

`virtual.start()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
virtual_source | [VirtualSource](Classes.md#virtualsource) | The source associated with this operation.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.
source_config | [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class) | The source config associated with this source.

### Returns
None

### Example

```python
from dlpx.virtualization.platform import Plugin

plugin = Plugin()

@plugin.virtual.start()
def start(virtual_source, repository, source_config):
  pass
```

## Virtual Source Stop

Executed whenever the data needs to be shut down.
Required to implement for Delphix Engine operations:

### Required / Optional
**Optional.**

### Delphix Engine Operations

* [Virtual Source Stop](Workflows.md#virtual-source-stop)

### Signature

`def stop(virtual_source, repository, source_config)`

### Decorator

`virtual.stop()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
virtual_source | [VirtualSource](Classes.md#virtualsource) | The source associated with this operation.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.
source_config | [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class) | The source config associated with this source.

### Returns
None

### Example

```python
from dlpx.virtualization.platform import Plugin

plugin = Plugin()

@plugin.virtual.stop()
def stop(virtual_source, repository, source_config):
  pass
```

## Virtual Source Pre-Snapshot

Prepares the virtual source for taking a snapshot of the data.

### Required / Optional
**Optional.**

### Delphix Engine Operations

* [Virtual Source Snapshot](Workflows.md#virtual-source-snapshot)

### Signature

`def virtual_pre_snapshot(virtual_source, repository, source_config)`

### Decorator

`virtual.pre_snapshot()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
virtual_source | [VirtualSource](Classes.md#virtualsource) | The source associated with this operation.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.
source_config | [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class) | The source config associated with this source.

### Returns
None

### Example

```python
from dlpx.virtualization.platform import Plugin

plugin = Plugin()

@plugin.virtual.pre_snapshot()
def virtual_pre_snapshot(virtual_source, repository, source_config):
  pass
```

## Virtual Source Post-Snapshot

Captures metadata after a snapshot.

### Required / Optional
**Required.**

### Delphix Engine Operations

* [Virtual Source Snapshot](Workflows.md#virtual-source-snapshot)

### Signature

`def virtual_post_snapshot(virtual_source, repository, source_config)`

### Decorator

`virtual.post_snapshot()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
virtual_source | [VirtualSource](Classes.md#virtualsource) | The source associated with this operation.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.
source_config | [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class) | The source config associated with this source.

### Returns
[SnapshotDefinition](Schemas_and_Autogenerated_Classes.md#snapshotdefinition-class)

### Example

```python
from dlpx.virtualization.platform import Plugin
from generated.defintions import SnapshotDefinition

plugin = Plugin()

@plugin.virtual.post_snapshot()
def virtual_post_snapshot(virtual_source, repository, source_config):
  snapshot = SnapshotDefinition()
  snapshot.transaction_id = 1000
  return snapshot
```

> The above command assumes a [Snapshot Schema](Schemas_and_Autogenerated_Classes.md#snapshot-schema) defined as:

```json
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "transactionId": { "type": "string" }
  }
}
```

## Virtual Source Mount Specification

Returns configurations for the mounts associated for data in virtual source.
The `ownership_specification` is optional. If not specified, the platform will default the ownership settings to the environment user used for the Delphix Operation.

### Required / Optional
**Required.**

### Delphix Engine Operations

* [Virtual Source Enable](Workflows.md#virtual-source-enable)
* [Virtual Source Provision](Workflows.md#virtual-source-provision)
* [Virtual Source Refresh](Workflows.md#virtual-source-refresh)
* [Virtual Source Rollback](Workflows.md#virtual-source-rollback)
* [Virtual Source Start](Workflows.md#virtual-source-start)

### Signature

`def virtual_mount_specification(virtual_source, repository)`

### Decorator

`virtual.mount_specification()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
virtual_source | [VirtualSource](Classes.md#virtualsource) | The source associated with this operation.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.

### Returns
[MountSpecification](Classes.md#mountspecification)

### Example

!!! info
    `ownership_specification` only applies to Unix hosts.

```python
from dlpx.virtualization.platform import Plugin
from dlpx.virtualization.platform import Mount
from dlpx.virtualization.platform import MountSpecification
from dlpx.virtualization.platform import OwenershipSpecification
from generated.definitions import SnapshotDefinition

plugin = Plugin()

@plugin.virtual.mount_specification()
def virtual_mount_specification(virtual_source, repository):
  mount = Mount(virtual_source.connection.environment, "/some/path")
  ownership_spec = OwenershipSpecification(repository.uid, repository.gid)

  return MountSpecification([mount], ownership_spec)
```


## Virtual Source Status

Determines the status of a [Virtual Source](Glossary.md#virtual-source) to show end users whether it is healthy or not.

### Required / Optional
**Optional.**<br/>
If not implemented, the platform assumes that the status is `Status.ACTIVE`.

### Delphix Engine Operations

* [Virtual Source Enable](Workflows.md#virtual-source-enable)

### Signature

`def virtual_status(virtual_source, repository, source_config)`

### Decorator

`virtual.status()`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
virtual_source | [VirtualSource](Classes.md#virtualsource) | The source associated with this operation.
repository | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class) | The repository associated with this source.
source_config | [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class) | The source config associated with this source.

### Returns
[Status](Classes.md#status)<br/>
`Status.ACTIVE` if the plugin operation is not implemented.

### Example
```python
from dlpx.virtualization.platform import Plugin
from dlpx.virtualization.platform import Status

plugin = Plugin()

@plugin.virtual.status()
def virtual_status(virtual_source, repository, source_config):
  return Status.ACTIVE
```


## Repository Data Migration

A Repository [Data Migration](Glossary.md#data-migration) migrates repository data from an older [schema](Glossary.md#schema) format to an updated schema format.

### Required / Optional
**Optional.**<br/>

!!! warning
    You must ensure that all repository data will match your updated repository schema after an upgrade operation. Depending on how your schema has changed, this might imply that you need to write one or more repository data migrations.

### Delphix Engine Operations

* [Upgrade](Workflows.md#upgrade)

### Signature

`def migrate_repository(old_repository)`

### Decorator

`upgrade.repository(migration_id)`

### Decorator Arguments

Argument | Type | Description
-------- | ---- | -----------
migration_id | String | The ID of this migration. An ID is a string containing one or more positive integers separated by periods. Each ID must be unique. More details [here](/Versioning_And_Upgrade/Upgrade.md#rules-for-data-migrations).

### Function Arguments
Argument | Type | Description
-------- | ---- | -----------
old_repository | Dictionary | The plugin-specific data associated with a repository, that conforms to the previous schema.

!!! warning
    The function argument `old_repository` is a Python dictionary, where each property name appears exactly as described in the previous repository schema. This differs from non-upgrade-related operations, where the function arguments are [autogenerated classes](Schemas_and_Autogenerated_Classes.md) based on the schema.


### Returns
Dictionary<br/>
A migrated version of the `old_repository` input that must conform to the updated repository schema.

### Example
```python
from dlpx.virtualization.platform import Plugin

plugin = Plugin()

@plugin.upgrade.repository("2019.12.15")
def add_new_flag_to_repo(old_repository):
  new_repository = dict(old_repository)
  new_repository["useNewFeature"] = False
  return new_repository
```

## Source Config Data Migration

A Source Config [Data Migration](Glossary.md#data-migration) migrates source config data from an older [schema](Glossary.md#schema) format to an updated schema format.

### Required / Optional
**Optional.**<br/>

!!! warning
    You must ensure that all source config data will match your source config schema after an upgrade operation. Depending on how your schema has changed, this might imply that you need to write one or more source config data migrations.

### Delphix Engine Operations

* [Upgrade](Workflows.md#upgrade)

### Signature

`def migrate_source_config(old_source_config)`

### Decorator

`upgrade.source_config(migration_id)`

### Decorator Arguments

Argument | Type | Description
-------- | ---- | -----------
migration_id | String | The ID of this migration. An ID is a string containing one or more positive integers separated by periods. Each ID must be unique. More details [here](/Versioning_And_Upgrade/Upgrade.md#rules-for-data-migrations).

### Function Arguments
Argument | Type | Description
-------- | ---- | -----------
old_source_config | Dictionary | The plugin-specific data associated with a source config, that conforms to the previous schema.

!!! warning
    The function argument `old_source_config` is a Python dictionary, where each property name appears exactly as described in the previous source config schema. This differs from non-upgrade-related operations, where the function arguments are [autogenerated classes](Schemas_and_Autogenerated_Classes.md) based on the schema.


### Returns
Dictionary<br/>
A migrated version of the `old_source_config` input that must conform to the updated source config schema.

### Example
```python
from dlpx.virtualization.platform import Plugin

plugin = Plugin()

@plugin.upgrade.source_config("2019.12.15")
def add_new_flag_to_source_config(old_source_config):
  new_source_config = dict(old_source_config)
  new_source_config["useNewFeature"] = False
  return new_source_config
```
## Linked Source Data Migration

A Linked Source [Data Migration](Glossary.md#data-migration) migrates linked source data from an older [schema](Glossary.md#schema) format to an updated schema format.

### Required / Optional
**Optional.**<br/>

!!! warning
    You must ensure that all linked source data will match your linked source schema after an upgrade operation. Depending on how your schema has changed, this might imply that you need to write one or more linked source data migrations.

### Delphix Engine Operations

* [Upgrade](Workflows.md#upgrade)

### Signature

`def migrate_linked_source(old_linked_source)`

### Decorator

`upgrade.linked_source(migration_id)`

### Decorator Arguments

Argument | Type | Description
-------- | ---- | -----------
migration_id | String | The ID of this migration. An ID is a string containing one or more positive integers separated by periods. Each ID must be unique. More details [here](/Versioning_And_Upgrade/Upgrade.md#rules-for-data-migrations).

### Function Arguments
Argument | Type | Description
-------- | ---- | -----------
old_linked_source | Dictionary | The plugin-specific data associated with a linked source, that conforms to the previous schema.

!!! warning
    The function argument `old_linked_source` is a Python dictionary, where each property name appears exactly as described in the previous linked source schema. This differs from non-upgrade-related operations, where the function arguments are [autogenerated classes](Schemas_and_Autogenerated_Classes.md) based on the schema.


### Returns
Dictionary<br/>
A migrated version of the `old_linked_source` input that must conform to the updated linked source schema.

### Example
```python
from dlpx.virtualization.platform import Plugin

plugin = Plugin()

@plugin.upgrade.linked_source("2019.12.15")
def add_new_flag_to_dsource(old_linked_source):
  new_linked_source = dict(old_linked_source)
  new_linked_source["useNewFeature"] = False
  return new_linked_source
```
## Virtual Source Data Migration

A Virtual Source [Data Migration](Glossary.md#data-migration) migrates virtual source data from an older [schema](Glossary.md#schema) format to an updated schema format.

### Required / Optional
**Optional.**<br/>

!!! warning
    You must ensure that all virtual source data will match your virtual source schema after an upgrade operation. Depending on how your schema has changed, this might imply that you need to write one or more virtual source data migrations.

### Delphix Engine Operations

* [Upgrade](Workflows.md#upgrade)

### Signature

`def migrate_virtual_source(old_virtual_source)`

### Decorator

`upgrade.virtual_source(migration_id)`

### Decorator Arguments

Argument | Type | Description
-------- | ---- | -----------
migration_id | String | The ID of this migration. An ID is a string containing one or more positive integers separated by periods. Each ID must be unique. More details [here](/Versioning_And_Upgrade/Upgrade.md#rules-for-data-migrations).

### Function Arguments
Argument | Type | Description
-------- | ---- | -----------
old_virtual_source | Dictionary | The plugin-specific data associated with a virtual source, that conforms to the previous schema.

!!! warning
    The function argument `old_virtual_source` is a Python dictionary, where each property name appears exactly as described in the previous virtual source schema. This differs from non-upgrade-related operations, where the function arguments are [autogenerated classes](Schemas_and_Autogenerated_Classes.md) based on the schema.


### Returns
Dictionary<br/>
A migrated version of the `old_virtual_source` input that must conform to the updated virtual source schema.

### Example
```python
from dlpx.virtualization.platform import Plugin

plugin = Plugin()

@plugin.upgrade.virtual_source("2019.12.15")
def add_new_flag_to_vdb(old_virtual_source):
  new_virtual_source = dict(old_virtual_source)
  new_virtual_source["useNewFeature"] = False
  return new_virtual_source
```
## Snapshot Data Migration

A Snapshot [Data Migration](Glossary.md#data-migration) migrates snapshot data from an older [schema](Glossary.md#schema) format to an updated schema format.

### Required / Optional
**Optional.**<br/>

!!! warning
    You must ensure that all snapshot data will match your snapshot schema after an upgrade operation. Depending on how your schema has changed, this might imply that you need to write one or more snapshot migrations.

### Delphix Engine Operations

* [Upgrade](Workflows.md#upgrade)

### Signature

`def migrate_snapshot(old_snapshot)`

### Decorator

`upgrade.snapshot(migration_id)`

### Decorator Arguments

Argument | Type | Description
-------- | ---- | -----------
migration_id | String | The ID of this migration. An ID is a string containing one or more positive integers separated by periods. Each ID must be unique. More details [here](/Versioning_And_Upgrade/Upgrade.md#rules-for-data-migrations).

### Function Arguments
Argument | Type | Description
-------- | ---- | -----------
old_snapshot | Dictionary | The plugin-specific data associated with a snapshot, that conforms to the previous schema.

!!! warning
    The function argument `old_snapshot` is a Python dictionary, where each property name appears exactly as described in the previous snapshot schema. This differs from non-upgrade-related operations, where the function arguments are [autogenerated classes](Schemas_and_Autogenerated_Classes.md) based on the schema.


### Returns
Dictionary<br/>
A migrated version of the `old_snapshot` input that must conform to the updated snapshot schema.

### Example
```python
from dlpx.virtualization.platform import Plugin

plugin = Plugin()

@plugin.upgrade.snapshot("2019.12.15")
def add_new_flag_to_snapshot(old_snapshot):
  new_snapshot = dict(old_snapshot)
  new_snapshot["useNewFeature"] = False
  return new_snapshot
```
