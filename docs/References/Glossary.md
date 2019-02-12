# Glossary for Plugin Authors


## Automatic Discovery
[Discovery](#discovery) which is done by the Delphix Engine (with help from a plugin) itself, with no need for the end user to provide any information.

## Decorator
A Python construct which is used by plugins to "tag" certain functions, so that the Delphix Engine knows which function corresponds to which plugin operation.

## Direct Linking/Syncing
A strategy that involves data being ingested directly from the source environment onto the Delphix Engine, without the assistance of a staging environment.

## Discovery
The process by which the Delphix Engine learns about how a particular environment can be used for ingesting or virtualizing datasets.

## Dsource
A dataset on the Delphix Engine which is an ingested copy of a pre-existing dataset on a source environment (pronounced /dɪˈsoʊrs/)

## Environment
A remote system that the Delphix Engine can interact with. An environment can be used as a [source](#source-environment), [staging](#staging-environment) or [target](#target-environment) environment (or any combination of those).  For example, a Linux machine that the Delphix Engine can connect to is an environment.

## Linking
The process by which the Delphix Engine connects a new [dsource](#dsource) to a pre-existing dataset on a source environment.

## Manual Discovery
[Discovery](#discovery) which the end user does by manually entering the necessary information into the Delphix Engine.

## Plugin
A tool that customizes the Delphix Engine so it knows how to interact with a particular kind of dataset.

## Plugin Operation
A piece of functionality that provided by a plugin in order to customize Delphix Engine behavior to work with a particular kind of dataset. A plugin operation is implemented as a Python function.
For example, a MySQL plugin might provide an operation called "stop" which knows how to stop a MySQL database.

## Provisioning
The process of making a virtual copy of a dataset and making it available for use on a target environment.

## Repository
Information that represents a set of dependencies that a dataset requires in order to be functional. For example, a particular Postgres database might require an installed Postgres 9.6 DBMS, and so its associated repository would contain all the information required to interact with that DBMS.

## Schema
A formal description of a data type. Plugins use JSON format for their schemas (link to reference for JSON schemas).

## Source Config
A collection of information that the Delphix Engine needs to interact with a dataset on an environment.

## Source Environment
An environment containing data that is ingested by the Delphix Engine.

## Staged Linking/Syncing
A strategy where a [staging environment](#staging-environment) is used to coordinate the ingestion of data into a [dsource](#dsource).

## Staging Environment
An [environment](#environment) used by the Delphix Engine to coordinate ingestion from a [source environment](#source-environment).

## Syncing
The process by which the Delphix Engine ingests data from a dataset on a [source environment](#source-environment) into a [dsource](#dsource). Syncing always happens immediately after [linking](#linking), and typically is done periodically thereafter.

## Target Environment
An [environment](#environment) on which Delphix-provided virtualized datasets can be used.
