---
title: Virtualization SDK
---


# Overview

In the following few pages, we will walk through an example of making a simple, working plugin.

Our plugin will virtualize simple directory trees on Unix systems. The actual contents of these directories could be anything: configuration files, documents, image libraries, etc. Our plugin will not care about the contents and will treat it as a directory tree full of files.

## Data Flow in the Delphix Engine
Here we will briefly overview how data moves through the Delphix Engine.

### Ingestion
It all begins with Delphix ingesting data—copying some data from what we call a [source environment](/References/Glossary.md#source-environment)  onto the Delphix Engine.

Plugins can use either of two basic strategies to do this copying:

 - [direct linking](/References/Glossary.md#direct-linking), where the Delphix Engine pulls data directly from the source environment.
 - [staged linking](/References/Glossary.md#staged-linking), where the plugin is responsible for pulling data from the source environment.

Our plugin will use the staged linking strategy.

With staged linking, Delphix exposes and mounts storage to a [staging environment](/References/Glossary.md#staging-environment).  This would be an NFS share for Unix environments and iSCSI disks for Windows environments. You can use either the source environment or a different environment for staging. We will write our plugin to handle both approaches.

Once Delphix mounts the storage share onto the staging environment, the plugin needs to arrange for the relevant data to be copied from the source environment onto the storage share, which is backed by Delphix Engine storage.

When this initial copy is complete, Delphix will take a snapshot of the backing storage.

(**Diagram coming soon!**)

This same basic operation will be repeated when Delphix mounts an NFS share: The plugin copies data onto it, then Delphix snapshots the result.

### Provisioning
**Provisioning** is when you take a Delphix Engine snapshot and create a virtual dataset from it.

First the snapshot is cloned onto the Delphix Engine, then this newly-cloned data is mounted as a virtual dataset onto a **target environment**. While this new virtual dataset gets updated by its end users, the original snapshot is persistent. You can use it in a few ways:

 - Provision other virtual datasets from it
 - Rewind the virtual dataset back to the state it represents
 - Create a physical database from it in what we call V2P: Virtual to Physical

(**Diagram coming soon!**)

## Parts of a Plugin
A plugin consists of three main parts. We will cover them briefly here, and then fill in more details later in the tutorial.

### Plugin Config
Plugin config is where the plugin describes itself to the Delphix Engine. What is the plugin called? What version of the plugin is being used? What type(s) of environments does the plugin work with? What features does the plugin offer?...

### Plugin Operations
The plugin will need to provide operations. These are Python functions, each of which implements one small piece of functionality. This is how the plugin customizes Delphix behavior to work with the kind of dataset you’re building the plugin for. One operation will handle setting up a newly-configured virtual dataset. Another will handle copying data from a source environment, and so on.

Later we’ll provide examples for our first plugin. See [Plugin Operations](/References/Plugin_Operations.md) for full details on the operations that are available, which are required, and what each one is required to do.

### Schemas
As part of normal operations, plugins need to generate and access certain pieces of information in order to do their job. For example, plugins that work with Postgres might need to know which port number to connect to, or which credentials to use.

Defining your plugin’s schemas will enable it to give the Delphix Engine the details it needs to run the operations we’ve built into it. Different datasets can have very different needs. The [schemas](/References/Schemas.md) you provide for your plugin will tell Delphix how to operate with your dataset.

## Prerequisites
To complete the tutorial that follows, make sure you check off the things on this list:

- Download the SDK and get it working
- A running Delphix Engine, version x.y.z or above.
- Add at least one Unix host—but preferably three—to the Delphix Engine as remote environments
- Have a tool at hand for editing text files—mostly Python and JSON. A simple text editor would work fine, or you can use a full-fledged IDE.

!!! question "[Survey](https://forms.gle/26APvZq7Lm6nEQ8q8)"
    Please fill out this [survey](https://forms.gle/26APvZq7Lm6nEQ8q8) to give us feedback about this section.
