---
title: Virtualization SDK
---

# Data Ingestion

## How Does Delphix Ingest Data?

As discussed in the [previous page](/References/Your_First_Plugin/Discovery), the Delphix Engine uses the [discovery](/References/Glossary/#discovery) process to learn about datasets that live on a [source environment](/References/Glossary/#source-environment). This section describes how we ingest such a dataset into the Delphix Engine. It is a two-step process.

### Linking

The first step is called [linking](/References/Glossary/#linking). This is simply the creation of a new dataset on the Delphix Engine, which is associated with the dataset on the source environment. This new linked dataset is called a [dSource](/References/Glossary/#dsource).

### Syncing

Immediately after linking, the new dSource is [synced](/References/Glossary/#syncing). This is the process by which data from the source environment is copied onto the Delphix Engine. Subsequent syncs may then be periodically performed in order to keep the dSource up-to-date.

The details of how this copying is done will vary significantly from plugin to plugin. For example, some plugins will simply copy files from the filesystem. Other plugins might contact a DBMS and instruct it to send backup or replication streams. There are many possibilities here, but they all break down into two main strategies that the plugin author can choose from:

With the [direct](/References/Glossary/#direct-linkingsyncing) strategy, the plugin is not in charge of the data copying. Instead the Delphix Engine will directly pull raw data from the source environment, using the Unix tool `rsync` (or `robocopy` on Windows). The plugin merely provides the location of the data. This is a very simple strategy, and it is also quite limiting.

For our first plugin, we'll be using the more flexible [staging](/References/Glossary/#staged-linkingsyncing) strategy. With this strategy, the Delphix Engine will use NFS (or CIFS on Windows) to mount storage onto a [staging environment](/References/Glossary/#staging-environment). Our plugin will then be in full control of how to get data from the source environment onto this NFS mount.

!!! note "Gotcha"
    Although it is not common, it is entirely possible that the staging environment is the same thing as the source environment. Be careful not to assume otherwise in your plugins.

For more details about deciding between using a direct or a staging strategy, please see (link to best practices section).

### Our Syncing Strategy

For our purposes here in this intro plugin, we'll use a simple strategy. We'll simply copy files from the filesystem on the source environment onto the NFS mount on the staging environment. We'll do this by running `scp` from our staging environment, and use user-provided credentials to connect to the source environment.

For simplicity's sake, we will not bother handling the case mentioned above where the staging environment is the same as the source environment


## Defining Your Linked Source Data Format

In order to be able to successfully do the copying required, plugins might need to get some information from the user. In our case, we will need to connect from the staging environment to the source environment using the `scp` tool. This means we will need to know a username and password.

Again, we will be using a JSON schema to define the data format. The user will be presented with a UI that will let them provide all the information our schema specifies.

(TODO: describe where to put this schema)
```javascript
{
    "type": "object",
    "additionalProperties": false,
    "required": ["username", "password"],
    "properties" {
        "username": {
            "type": "string",
            "prettyName": "Username on Source Host",
            "description": "Username for making SSH connection to source host"
        },
        "password": {
            "type": "string",
            "prettyName": "Password on Source Host",
            "description": "Password for making SSH connection to source host",
            "format": "password"
        }
    }
}
```

There is one new thing to notice about this schema, as compared with our discovery schemas. The `password` property is tagged as [`"format": "password"`](/References/Glossary/#password-property). This ensures that the Delphix Engine will take precautions like not displaying the value on-screen. For full details, see (link to reference section).

With this schema, the user will be required to provide a username and password as part of the linking process.


## Implementing Syncing in Your Plugin

As explained here (link to reference flowchart), the Delphix Engine will always run the plugin's `preSnapshot` operation just before taking a snapshot of the dsource. That means our `preSnapshot` operation has to get the NFS share into the desired state. For us, that means that's the time to do our data copy.

Create a file in your preferred editor (TODO: add suggested/required filename), and add the following Python code. (TODO: revisit when decorators are finalized)

```python
@delphix.linked_pre_snapshot
def copy_data_from_source(source_environment, staging_environment, source_config, linked_source, mount_location):
    environment_variables = { "PASSWORD": linked_source.password }
    scp_data_location = "%s@%s:%s".format(linked_source.username, source_environment.hostname, source_config.path)
    scp_command = "echo $PASSWORD | scp -r %s %s".format(scp_data_location, mount_location)

    result = dx.run_bash(staging_environment, copy_command, environment_variables)

    if result.exit_code != 0:
        raise ValueError("Could not copy files. Please check username and password.\n%s".format(result.stderr)
```

Taking this line-by-line, here's what's happening in our new method:

```python
@delphix.linked_pre_snapshot
```

This [decorator](/References/Glossary/#password-property) tells the Delphix Engine that this code will define our "pre-snapshot" operation.

```python
def copy_data_from_source(source_environment, staging_environment, source_config, linked_source, mount_location):
```

This begins the Python function that implements our pre-snapshot operation. As compared with our discovery code, there are a lot more inputs coming in from the Delphix Engine.

!!! note "Gotcha"
    The order of these input arguments matters. That is, the first input argument is always going to represent the source environment, the second the staging environment, and so on. It's highly recommended to use these same variable names to avoid confusion.

```python
    environment_variables = { "PASSWORD": linked_source.password }
    scp_data_location = "%s@%s:%s".format(linked_source.username, source_environment.hostname, source_config.path)
    scp_command = "echo $PASSWORD | scp -r %s %s".format(scp_data_location, mount_location)
```

Here, we are preparing data to help us run a Bash command on the staging host. First, we set up a Python dictionary that represents the environment variables we want. Next, we construct a Python string that represents the actual command we want to run.

Note that we are using the `scp` tool to copy files from the source environment onto the NFS share that is mounted to the staging environment.


```python
    result = dx.run_bash(staging_environment, copy_command, environment_variables)
    if result.exit_code != 0:
        raise ValueError("Could not copy files. Please check username and password.\n%s".format(result.stderr)
```

This code actually runs the Bash command. The function `run_bash` that we're calling here is a called a [callback](/References/Glossary/#callback). Plugins use callbacks to request that the Delphix Engine do work on the plugin's behalf. In our case, we are telling the Delphix Engine to run our bash command on the staging environment.

We also check that the command succeeded. If not, we will raise an error that explains the situation to the user.

For full details on the `run_bash` callback, and on callbacks in general, please see (link to reference).

## How to Link and Sync in the Delphix Engine

Let's try it out and make sure this works!

You should already have a respository and source config set up from the previous page.

Next, you should set up a separate staging environment. (TODO: add instructions here)

Go to "Manage/Environments", select your **source** environment, and then go to the "Databases" tab. Find your "Directory Tree" repository, and your source config underneath it.

Click "Add dSource" on your source config. This will begin the linking process.

You should be presented with a UI in which you will have to specify which environment you want to use for staging. You will also be asked to provide the username and password needed to connect to the source environment.

After you have finished entering this information, the initial sync process will begin. This is what will call your pre-snapshot operation, thus copying data.

!!! note "Gotcha"
    Once you've manually created a dsource, you will not be allowed to modify your plugin's linked source schema. We'll cover how to deal with this correctly later, in the upgrade section. For now, if you need to change your plugin's linked source schema, you'll have to first delete any dsources you've manually added.
