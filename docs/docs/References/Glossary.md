# Glossary


## Artifact
A single file that is the result of a [build](#building). It is this artifact which is distributed to users, and which is installed onto engines.

## Automatic Discovery
[Discovery](#discovery) which is done by the Delphix Engine (with help from a plugin) itself, with no need for the end user to provide any information.

## Building
The process of creating an [artifact](#artifact) from the collection of files that make up the plugin's source code.

## Data Migration
A python function which is called as part of the upgrade process. It handles transforming data from an older format to a newer format. More details [here](/Versioning_And_Upgrade/Upgrade.md#data-migrations).

## Data Migration ID
Each data migration is tagged with a unique ID. This allows the Delphix Engine to know which data migrations need to be run, in which order, when upgrading to a new plugin version. More details [here](/Versioning_And_Upgrade/Upgrade.md#data-migrations).

## Decorator
A Python construct which is used by plugins to "tag" certain functions, so that the Delphix Engine knows which function corresponds to which plugin operation.

## Direct Linking
A strategy that involves data being ingested directly from the source environment onto the Delphix Engine, without the assistance of a staging environment.

## Discovery
The process by which the Delphix Engine learns about how a particular environment can be used for ingesting or virtualizing datasets.

## dSource
See [Linked Dataset](#linked-dataset)

## Empty VDB
A VDB that is created from scratch, without provisioning from another dataset. Users can create empty VDBs when they want to construct a brand-new dataset from within Delphix, instead of creating it externally and then ingesting it.

This "empty" VDB, of course, will typically not stay empty for long. Data will be added as users work with the new dataset.

A plugin can support this functionality by implementing the [initialize](Plugin_Operations.md#virtual-source-initialize) operation.

## Environment
A remote system that the Delphix Engine can interact with. An environment can be used as a [source](#source-environment), [staging](#staging-environment) or [target](#target-environment) environment (or any combination of those).  For example, a Linux machine that the Delphix Engine can connect to is an environment.

## Environment User
A set of user credentials that the Delphix Engine can use to interact with an [Environmnet](#environment). For example, a username and password to login to a Linux machine.

## Linked Dataset
A dataset on the Delphix Engine which holds an ingested copy of a pre-existing external dataset from a source environment. A linked dataset is often called a [dSource](#dsource).

## Linked Source
An object on the Delphix Engine that holds information related to a [linked dataset](#linked-dataset).

## Linking
The process by which the Delphix Engine connects a new [dSource](#dsource) to a pre-existing dataset on a source environment.

## Logging
Logging is when a plugin writes out some human-readable information to a log file. The log file can then be examined, typically in order to debug a problem with the plugin.

## Plugin Config
A [YAML](#yaml) file containing a list of plugin properties: What is the plugin's name? What version of the plugin is this? Etc. More details [here](Plugin_Config.md).

## Manual Discovery
[Discovery](#discovery) which the end user does by manually entering the necessary information into the Delphix Engine.

## Mount Specification
A collection of information, provided by the plugin, which give all the details about how and where [virtual datasets](#virtual-dataset) should be mounted onto [target environments](#target-environment). This term is often shortened to "Mount Spec".

## Password Properties
In [schemas](#schema), any string property can be tagged with `"format": "password"`. This will let the Delphix Engine know that the property contains sensitive information. Any such values will only be stored in encrypted format, and the UI will not display the values on screen.

## Platform Libraries
A set of Python functions that are provided by the Virtualization Platform. Plugins use these library functions to request that the Virtualization Platform do some task on behalf of the plugin. For example, running a Bash command on an environment, or making an log entry.

## Plugin
A tool that customizes the Delphix Engine so it knows how to interact with a particular kind of dataset.

## Plugin Operation
A piece of functionality that provided by a plugin in order to customize Delphix Engine behavior to work with a particular kind of dataset. A plugin operation is implemented as a Python function.
For example, a MySQL plugin might provide an operation called "stop" which knows how to stop a MySQL database.

## Provisioning
The process of making a virtual copy of a dataset and making it available for use on a target environment.

## Replication
Delphix allows end users to replicate data objects between Delphix Engines by creating a replication profile. Data objects that belong to a plugin can also be part of the replication profile. Refer to the [Delphix Engine Documentation](https://docs.delphix.com/docs/) for more details.

## Repository
Information that represents a set of dependencies that a dataset requires in order to be functional. For example, a particular Postgres database might require an installed Postgres 9.6 DBMS, and so its associated repository would contain all the information required to interact with that DBMS.

## Schema
A formal description of a data type. Plugins use JSON format for their [schemas](Schemas_and_Autogenerated_Classes.md#schemas-and-autogenerated-classes).

## Snapshot
A point-in-time read-only copy of a dataset. A snapshot includes associated metadata represented by the [SnapshotDefinition Schema](Schemas_and_Autogenerated_Classes.md#snapshotdefinition).

## Snapshot Parameters
User provided parameters for the snapshot operation which can be defined in a [Snapshot Parameters Definition](Schemas_and_Autogenerated_Classes.md#snapshotparametersdefinition).

## Source Config
A collection of information that the Delphix Engine needs to interact with a dataset (whether [linked](#linked-dataset) or [virtual](#virtual-dataset) on an [environment](#environment).

## Source Environment
An [environment](#environment) containing data that is ingested by the Delphix Engine.

## Staged Linking
A strategy where a [staging environment](#staging-environment) is used to coordinate the ingestion of data into a [dsource](#dsource).

## Staging Environment
An [environment](#environment) used by the Delphix Engine to coordinate ingestion from a [source environment](#source-environment).

## Syncing
The process by which the Delphix Engine ingests data from a dataset on a [source environment](#source-environment) into a [dsource](#dsource). Syncing always happens immediately after [linking](#linking), and typically is done periodically thereafter.

## Target Environment
An [environment](#environment) on which Delphix-provided virtualized datasets can be used.

## Lua Toolkit
Legacy model for writing "plugins" in Lua, with limited documentation and limited support for writing, building and uploading toolkits. This was the predecessor to the Virtualization SDK.

## Upgrade Operation
A special plugin operation that takes data produced by an older version of a plugin, and transforms it into the format expected by the new version of the plugin.

## VDB
See [Virtual Dataset](#virtual-dataset)

## Version
A string identifier that is unique for every public release of a plugin.

## Virtual Dataset
A dataset that has been cloned from a snapshot, and whose data is stored on the Delphix Engine. A virtual dataset is made available for use by mounting it to a [target environment](#target-environment). A virtual dataset is often called a "VDB".

## Virtual Source
An object on the Delphix Engine that holds information related to a [virtual dataset](#virtual-dataset).

## YAML
YAML is a simple language often used for configuration files. Plugins define their [plugin config](#plugin-config) using YAML.
