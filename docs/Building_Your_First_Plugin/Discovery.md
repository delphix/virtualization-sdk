---
title: Virtualization SDK
---

# Discovery

## What is Discovery?
In order to ingest data from a source environment, the Delphix Engine first needs to learn information about the data: Where does it live? How can it be accessed? What is it called?

[Discovery](/References/Glossary.md#discovery) is the process by which the Delphix Engine learns about remote data. Discovery can be either:

- [automatic](/References/Glossary.md#automatic-discovery) — where the plugin finds the remote data on its own
- [manual](/References/Glossary.md#manual-discovery) — where the user tells us about the remote data

For our first plugin, we will be using a mix of these two techniques.

## Source Configs and Repositories

### What are Source Configs and Repositories?

A [source config](/References/Glossary.md#source-config) is a collection of information that Delphix uses to represent a dataset. Different plugins will have different ideas about what a "dataset" is (an entire database? a set of config files? an application?). For our first plugin, it is simply a directory tree on the filesystem of the remote environment.

A [repository](/References/Glossary.md#repository) represents what you might call "data dependencies" -- anything installed on the remote host that the dataset depends on. For example, if you are working with a Postgres database, then your repository will represent an installation of a particular version of the Postgres DBMS. In this plugin, we do not have any special dependencies, except for the simple existence of the unix system on which the directory lives.

We will be using automatic discovery for our repositories, and manual discovery for our source configs. This is the default configuration that is created by `dvp init`, so there is nothing further we need to do here.

### Defining Your Data Formats
Because each plugin will have different ideas about what a repository or source config represents, different plugins will have different sets of information that they need to collect and store.

Delphix needs to know the format of this information. How many pieces of information are collected? What are they called? Are they strings? Numbers?

For our first plugin, we do not need a lot of information. We use no special information about our repositories (except some way for the user to identify them). For source configs, all we need to know is the path to the directory from which we will be ingesting data.

The plugin needs to describe all of this to the Delphix Engine, and it does so using [schemas](/References/Glossary.md#schema).  Recall that when we ran `dvp init`, a file full of bare-bones schemas was created. As we build up our first toolkit, we will be augmenting these schemas to serve our needs.

#### Repository Schema
Open up the `schema.json` file in your editor/IDE and locate `repositoryDefinition`, it should look like this:

```json
{
    "repositoryDefinition": {
        "type": "object",
        "properties": {
            "name": { "type": "string" }
        },
        "nameField": "name",
        "identityFields": ["name"]
    }
}
```

Since we do not have any special dependencies, we can just leave it as-is.

For detailed information about exactly how repository schemas work, see [the reference page](/References/Schemas.md).

In brief, what we are doing here is saying that each of our repositories will have a single property called `name`, which will be used both as a unique identifier and as the user-visible name of the repository.

#### Source Config Schema

For source configs, the bare-bones schema is not going to be good enough. Recall that for us, a source config represents a directory tree on a remote environment.

Locate the `sourceConfigDefinition` inside the `schema.json` file and modify the definition so it looks like this:

```json
"sourceConfigDefinition": {
    "type": "object",
    "required": ["name", "path"],
    "additionalProperties": false,
    "properties": {
        "name": {
          "type": "string",
          "prettyName": "Dataset Name",
          "description": "User-visible name for this dataset"
        },
        "path": {
          "type": "string",
          "format": "unixpath",
          "prettyName": "Path",
          "description": "Full path to data location on the remote environment"
        }
    },
    "nameField": "name",
    "identityFields": ["path"]
},
```

Now, we have two properties, a property `name` serving as the user-visible name of the source config and `path` which tells us where the data lives on the remote host. Note  we are using `path` as the unique identifier.

Because we are using manual discovery, the end user is going to be responsible for filling in values for `name` and `path`. So, we have added some things to our schema that we did not need for repositories.

The `prettyName` and `description` entries will be used by the UI to tell the user what these fields mean.

Because we set `additionalProperties` to `false`, this will prevent users from supplying properties other than `name` and `path`.

Finally, we have specified that the `path` property must be a well-formatted Unix path. This allows the UI to enforce that the format is correct before the user is allowed to proceed. (Note this only enforces the format, and does not actually check to see if the path really exists on some remote environment!)

Refer to the reference page for [Schemas](/References/Schemas.md) for more details about these entries, and for other things that you can do in these schemas.

## Implementing Discovery in Your Plugin

### About Python Code

As described in the overview section, plugins customize the behavior of the Delphix Engine by providing Python code. Each customizable piece of behavior is called a "plugin operation". The plugin provides separate Python functions for each of the operations that it wants to customize.

Right now, we are concerned with discovery. There are two customizable operations related to automatic discovery, one for repositories and one for source configs. In both cases, the job of the Python method is to automatically collect whatever information the schemas (see above) require, and to return that information to the Delphix Engine. The Delphix Engine will run these customized operations whenever a new environment is added, or when an existing environment is rediscovered.

### A Look at the Generated Code
Recall that the `dvp init` command we ran created a file called `src/plugin_runner.py`. Open this file in your editor/IDE. You will see that this file already contains a bunch of Python code. Let's take a look at the first three blocks of code in this file.

```python
from dlpx.virtualization.platform import Mount, MountSpecification, Plugin

from generated.definitions import (
    RepositoryDefinition,
    SourceConfigDefinition,
    SnapshotDefinition,
)
```
These `import` lines make certain functionality available to our Python code. Some of this functionality will
be used just below, as we implement discovery. Others will be used later on, as we implement
ingestion and provisioning. Later, you'll add more `import`s to unlock more functionality.

```python
plugin = Plugin()
```

This line creates a Python object which allows us to define our plugin types. We have the ability to do this because of the `import Plugin` statement above.

This object is stored in a variable we have elected to call `plugin`. We are free to call this variable anything we want, so long as we also change the `entryPoint` line in the `plugin_config.yml` file. For this example, we will just leave it as `plugin`.

```python
#
# Below is an example of the repository discovery operation.
#
# NOTE: The decorators are defined on the 'plugin' object created above.
#
# Mark the function below as the operation that does repository discovery.
@plugin.discovery.repository()
def repository_discovery(source_connection):
    #
    # This is an object generated from the repositoryDefinition schema.
    # In order to use it locally you must run the 'build -g' command provided
    # by the SDK tools from the plugin's root directory.
    #

    return [RepositoryDefinition(name='1e87dc30-3cdb-4f0a-9634-07ce017d20d1')]
```

This is our first [plugin operation](/References/Plugin_Operations.md). In this case, it's defining what will happen when the Delphix Engine wants to discover repositories on an environment.  Let's take a look at this code line-by-line

```python
@plugin.discovery.repository()
def repository_discovery(source_connection):
```

This begins the definition of a function called `repository_discovery`.

We are using a Python [decorator](/References/Glossary.md#decorator) which signals to the Delphix Engine that this is the function which should be called when it is time to do repository discovery. The actual name of the function doesn't matter here. Note that we are using our `plugin` variable here as part of the decorator.

The Delphix Engine will pass us information about the source environment in an argument called `source_connection`.

!!! warning
    The name of this input argument matters. That is, you'll always need to have an argument called
    `source_connection` here. Each plugin operation has its own set of required argument names. For
    details on which arguments apply to which operations, see the [reference section](/References/Plugin_Operations.md).

```python
    return [RepositoryDefinition(name='1e87dc30-3cdb-4f0a-9634-07ce017d20d1')]
```

This creates and returns a Python object that corresponds to the format defined by our repository schema. Because out repository has exactly one string property called `name`, therefore this Python object has one property called `name`.

Notice that the code generator has filled in the value of `name` with a random string. This results in a plugin operation that works, but which will not be very helpful for the user. We'll change this later.


The rest of the file contains more plugin operations, and we'll be modifying them later.


### Repository Discovery

Now, we need to modify the provided [repository discovery](/References/Plugin_Operations.md#repository-discovery) operation. This operation will examine a remote environment, find any repositories, and return information about them to the Delphix Engine.

As a reminder, our only external dependency on the remote environment is simply the existence of a filesystem. Since every Unix host has a filesystem, that means we will have exactly one repository per remote environment. Therefore, our repository discovery operation can be very simple.

In fact, as we saw above, the default-generated `repository_discovery` function does almost exactly what we want -- it returns one single repository for any Unix host that it is asked to work with. The only problem with it is that it uses
unhelpful name.  That's really easy to change!

Replace or modify `repository_discovery` so it looks like this:

```python
@plugin.discovery.repository()
def repository_discovery(source_connection):
    repository = RepositoryDefinition('Repository for our First Plugin')
    return [repository]
```

!!! tip
    Be careful to always use consistent indentation in Python code!


### Source Config Discovery

For source configs, we will rely solely on manual discovery. Therefore, the user will tell us which directories they want to ingest from. We still have to define a source config discovery operation -- it just won't need to do much.

The job of this operation is to return only source configs associated with the given `repository`. This function will be called once per repository. In our case, that means it will only be called once.

Because we want to supply **no** automatically-discovered source configs, this function should simply returns an empty list.

In fact, `dvp init` has already generated a function for us that does exactly this.

```python
@plugin.discovery.source_config()
def source_config_discovery(source_connection, repository):
    return []
```

If we wanted to do automatic discovery of source configs, we'd modify this function. But, for our purposes now, the existing code is fine and we don't need to change anything.



## How to Run Discovery in the Delphix Engine

Let us make sure discovery works!

1. Run the `dvp build` commands, as before. This will build the plugin, with all of the new changes, and create an artifact.

2. Run `dvp upload -e <engine> -u <user>`, as before. This will get all the new changes onto the Delphix Engine.

3. Once the new plugin is uploaded, add a remote unix environment to your engine. To do this, go to **Manage > Environments**, chose **Add Environment** from the menu, answer the questions, and **Submit**. (If you already have an environment set up, you can just refresh it instead).

  To keep an eye on this discovery process, you may need to open the **Actions** tab on the UI. If any errors happen, they will be reported here.

4. After the automatic discovery process completes, go to the **Databases** tab. You will see an entry for **Repository For Our First Plugin**. This is the repository you created in your Python code.

![Screenshot](images/PostDiscovery.png)

Notice that it says *No databases found on installation*. This is because we chose not to do automatic source config discovery.

However, because we have allowed manual source config discovery, you can add your own entries by clicking the plus sign (**Add Database**). Complete the information in the Add Database dialog and click Add.

![Screenshot](images/AddDatabase.png)

This should all look familiar. It is precisely what we defined in our source config schema. As expected, there are two entries, one for our `name` property, and one for `path`.

For example, in the above screenshot, we are specifying that we want to sync the `/bin` directory
from the remote host, and we want to call it `Binaries`. You can pick any directory and name that
you want.

Once you have added one or more source configs, you will be able to sync. This is covered on the next page.


!!! warning
    Once you have automatically or manually created source configs, you will not be allowed to modify your plugin's source config schema. We will cover how to deal with this later in the upgrade section. For now, if you need to change your plugin's source config schema:

    - You will have to delete any source configs you have manually added.
    - Delete the plugin and its corresponding objects (dSources, Virtual Sources, etc) if the source configs were manually discovered.

!!! question "[Survey](https://forms.gle/cEWzdTnvi6vNeMT58)"
    Please fill out this [survey](https://forms.gle/cEWzdTnvi6vNeMT58) to give us feedback about this section.
