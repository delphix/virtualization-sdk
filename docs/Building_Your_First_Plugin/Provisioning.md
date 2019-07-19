---
title: Virtualization SDK
---

# Provisioning

## What is Provisioning?
Once Delphix has a [snapshot](/References/Glossary.md#snapshot) of a dataset (for example of a dSource), it is possible to quickly clone that snapshot to create a new [virtual dataset](/References/Glossary.md#virtual-dataset). This new virtual dataset will be made available for use on a [target environment](/References/Glossary.md#target-environment). This process is called [provisioning](/References/Glossary.md#provisioning).

## Our Provisioning Strategy
For many plugins, there is a lot of work that needs to be done before a newly-provisioned virtual dataset can be made useful. For example, it might need to be registered with a running DBMS. Or, maybe some data inside the dataset needs to be changed so it behaves properly on the target environment.

In our case, however, there is very little to do. All we really require is that the files in the virtual dataset are accessible at some path on the target environment. Since the Delphix Engine takes care of mounting the data, we only need to worry about controlling *where* that data is mounted.

## Defining our Provision-Related Data Formats

We have already seen four custom data formats: for repositories, source configs, snapshots and
linked sources. The final one is used for [virtual sources](/References/Glossary.md#virtual-source).

Recall that, for our plugin, a VDB is just a directory full of files. There is no special
procedure needed to enable it, no DBMS to coordinate with, etc. All we need to do is make the files
available on the target environment.

So, the only question for the user is "Where should these files live?"

Open up `schema.json`, locate the `virtualSourceDefintion` section, and change it to look like this:

```json
"virtualSourceDefinition": {
    "type": "object",
    "additionalProperties" : false,
    "required": ["mountLocation"],
    "properties" : {
        "mountLocation": {
            "type": "string",
            "format": "unixpath",
            "prettyName": "Mount Location on Target Host",
            "description": "Where to mount VDB onto the target host"
        }
    }
},
```

This should look familiar from the source config schema that we did earlier. We only have one
property, and it represents the mount location on the target environment.

## Implementing Provisioning

There are numerous ways for a plugin to customize the provisioning process.
For our example plugin, we just need to do a few things:

1. Tell Delphix where to mount the virtual dataset.
2. Create a `sourceConfig` to represent each newly-provisioned virtual dataset.
3. Modify an existing `sourceConfig`, if necessary, when the virtual dataset is refreshed or rewound.
4. Construct snapshot-related data any time a snapshot is taken of the virtual dataset.

### Controlling Mounting

As we saw previously with linked sources, we need to tell Delphix where to mount the dataset. Open
up `plugin_runner.py` and find the `plugin.virtual.mount_specification` decorator. Change that function so that
it looks like this:

```python
@plugin.virtual.mount_specification()
def vdb_mount_spec(virtual_source, repository):
    mount_location = virtual_source.parameters.mount_location
    mount = Mount(virtual_source.connection.environment, mount_location)
    return MountSpecification([mount])
```

As we did with linked sources, we just look up what the user told us, and then package that up
and return it to Delphix.

### Creating a Source Config for a new VDB

Just like we saw earlier with [linked datasets](/References/Glossary.md#linked-dataset), each virtual dataset will need its own source config so that the Delphix Engine can interact with it. Our plugin is in charge of creating that source config at provision time

As a reminder, here is what our schema looks like for source configs:

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

Thus, for each newly-cloned virtual dataset, we create a new source config object with a name and a
path. This is done by the `configure` plugin operation.

In addition to generating a new source config, the configure operation is also tasked with getting
the newly-cloned dataset ready for use on the target environment. What this means exactly will vary
from plugin to plugin. For our simple plugin, the dataset does not require any setup work, and so we
only have to worry about the source config.

Find the `plugin.virtual.configure` decorator and change the function to look like this:

```python
@plugin.virtual.configure()
def configure_new_vdb(virtual_source, snapshot, repository):
    mount_location = virtual_source.parameters.mount_location
    name = "VDB mounted at {}".format(mount_location)
    return SourceConfigDefinition(path=mount_location, name=name)
```

### Modifying a Source Config after Rewind or Refresh

Just as a new VDB might need to be configured, a refreshed or rewound VDB might need to be
"reconfigured" to handle the new post-refresh (or post-rewind) state of the VDB. So, just as there
is a `configure` operation, there is also a `reconfigure` operation.

The main difference between the two is that `configure` must *create* a source config, but
`reconfigure` needs to *modify* a pre-existing source config.

In our simple plugin, there is no special work to do at reconfigure time, and there is no reason
to modify anything about the source config. We just need to write a `reconfigure` operation that
returns the existing source config without making any changes. Find the `plugin.virtual.reconfigure` decorator and modify the function as follows.

```python
@plugin.virtual.reconfigure()
def reconfigure_existing_vdb(virtual_source, repository, source_config, snapshot):
    return source_config
```

### Saving Snapshot Data

As with our linked sources, we don't actually have anything we need to save when VDB snapshots are
taken. And, again, `dvp init` has created a post-snapshot operation that will work just fine for us without modification:

```python
@plugin.virtual.post_snapshot()
def virtual_post_snapshot(virtual_source, repository, source_config):
    return SnapshotDefinition()
```

## How To Provision in the Delphix Engine

Finally, let us try it out to make sure provisioning works!

1. Again, use `dvp build` and `dvp upload` to get your new changes onto your Delphix Engine.
2. Click **Manage > Datasets**.
3. Select the dSource you created in the last page. You should see at least one snapshot, and maybe more than one if you have manually taken a snapshot, or if you have a snapshot policy in place. Select one of these snapshots and click the **Provision vFiles** icon.
4. This will open the Provision VDB wizard. Complete the steps and select **Submit**.
  During VDB provisioning one of the things you will have to do is to provide the data required by your virtual source schema. In our case, that means you will be asked to provide a value for `mountLocation`. You will also be asked to choose a target environment on which the new VDB will live. After the wizard finishes, you will see a job appear in the **Actions** tab on the right-hand side of the screen. When that job completes, your new VDB should be ready.
5. To ensure everything has worked correctly, log into to your target environment. From there, you can examine the directory you specified as the `mountLocation`. What you should see is a copy of the directory that you linked to with your dSource.

!!! question "[Survey](https://forms.gle/zTot9R9sx9PcMwmz5)"
    Please fill out this [survey](https://forms.gle/zTot9R9sx9PcMwmz5) to give us feedback about this section.
