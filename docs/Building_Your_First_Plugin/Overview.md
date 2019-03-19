---
title: Virtualization SDK
---


# Overview

In the following few pages, we'll walk through an example of making a simple, working plugin.

Our plugin will virtualize simple directory trees on Unix systems. The actual contents of these directories could be anything: configuration files, documents, image libraries, etc. Our plugin won't care about the contents, though. To us, we just treat it as a directory tree full of files.

## Data Flow in the Delphix Engine
Here we'll briefly overview how data moves through the Delphix Engine.

### Ingestion
The first step is that Delphix needs to ingest data. Essentially, this means copying some data from a [source environment](../References/Glossary.md#source-environment) onto the Delphix Engine.

There are two basic strategies a plugin can use to do this copying, called [direct linking](../References/Glossary.md#direct-linking) and [staged linking](../References/Glossary.md#staged-linking). Our plugin will use the staged linking strategy, but see (link to reference) for more information about direct linking.

With staged linking, Delphix will mount an NFS share onto a "staging environment" . This environment can be the same as the source environment, but it could also be different. We'll write our plugin to handle both cases.

Once Delphix mounts the NFS share onto the staging environment, the plugin needs to arrange for the relevant data to be copied from the source environment onto the NFS share, which is backed by Delphix Engine storage.

When this initial copy is complete, Delphix will take a snapshot of the backing storage.

(diagram goes here)

Subsequently, this same basic operation will be repeated: Delphix mounts an NFS share, the plugin copies data onto it, Delphix snapshots the result.

### Provisioning
Any of these Delphix Engine snapshots can be used to create a virtual dataset, by "provisioning".

The snapshot is cloned on the Delphix Engine, and this newly-cloned data is mounted onto a "target environment" as a new virtual dataset. Any updates made to this virtual dataset will not affect the original snapshot from which it was provisioned.

(diagram goes here)

## Parts of a Plugin
There are three main parts of a plugin. We'll cover them briefly here, and then fill in more details later in the tutorial.

### Manifest
The manifest is where the plugin describes itself to the Delphix Engine. What is the plugin called? What version of the plugin is this? What type(s) of environments does the plugin work with? What features does the plugin offer?...

### Operations/Code
The plugin will need to provide "operations". These are Python functions, each of which implement one small piece of functionality. This is how the plugin can customize Delphix behavior to work with a particular kind of dataset.
One operation will handle setting up a newly-configured virtual dataset. One operation will handle copying data from a source environment, and so on.

Later in this tutorial we will cover the specific examples we need for our first plugin. See [Plugin Operations](../References/Plugin_Operations.md) for full details on which operations are available, which are required, what each one is required to do, etc.. Also see (link to advanced) for a more-full featured example which uses many more operations.

### Datatype Definitions
As part of normal operation, a plugin will need to generate and access certain pieces of information in order to do its job. For example, a plugin that works with Postgres might need to know which port number to connect to, or which credentials to use, etc.

Different plugins will have vastly different needs for what information is required here, and the Delphix Engine needs to know the details. Therefore, a plugin can define its own datatypes, which it does by providing [schemas](../References/Schemas.md). We'll go into more detail on this later in the tutorial as well.

## Prerequisites
In order to complete the following tutorial, you'll need to make sure you have the following set up and ready to go:

- You should have a SDK already downloaded and working, as described here (link)
- You should have a Delphix Engine, version x.y.z or above.
- You should have at least one, but preferably three, Unix hosts that can be added to the Delphix Engine as remote environments.
- Some tool for editing text files (mostly Python and JSON). A simple text editor would work fine, or you can use a full-fledged IDE.
