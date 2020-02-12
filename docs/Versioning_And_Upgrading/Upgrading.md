# Upgrading

Upgrading is the process of moving from an older version of a plugin to a newer version.

# Motivating Example

Upgrading is not as simple as just replacing the installed plugin with a newer one.  The main complication comes when the new plugin version makes changes to its [schemas](/References/Glossary.md#schema).

Consider the case of a plugin that works with collections of text files -- the user points it to a directory tree containing text files, and the plugin syncs the files from there.

The first release of such a plugin might have no link-related user options. So the plugin's linked source schema might define no properties at all:

```json
"linkedSourceDefinition": {
    "type": "object",
    "additionalProperties" : false,
    "properties" : {
    }
}
```

And, the syncing code is very simple:
```python
@plugin.linked.pre_snapshot()
def linked_pre_snapshot(direct_source, repository, source_config):
    libs.run_sync(
        remote_connection = direct_source.connection,
        source_directory = source_config.path
        )
```


But, later, some users request a new feature -- they want to avoid syncing any backup or hidden files. So, a new plugin version is released. This time, there is a new boolean property in the linked source schema where users can elect to skip these files, if desired.
```json
"linkedSourceDefinition": {
    "type": "object",
    "additionalProperties" : false,
    "required": ["skipHiddenAndBackup"],
    "properties" : {
      "skipHiddenAndBackup": { "type": "boolean" }
    }
}
```

The plugin code that handles the syncing can now pay attention to this new boolean property:
```python
_HIDDEN_AND_BACKUP_SPECS = [
    "*.bak",
    "*~",  # Backup files from certain editors
    ".*"  # Unix-style hidden files
]

@plugin.linked.pre_snapshot()
def linked_pre_snapshot(direct_source, repository, source_config):
    exclude_spec = _HIDDEN_AND_BACKUP_SPECS if direct_source.parameters.skip_hidden_and_backup else []

    libs.run_sync(
        remote_connection = direct_source.connection,
        source_directory = source_config.path,
        exclude_paths = exclude_spec
        )
```

Suppose a user has an engine with linked sources created by the older version of this plugin. That is, the existing linked sources have no `skipHiddenAndBackup` property.

If the user installs the new version of the plugin, we have a problem! The above `pre_snapshot` code from the new plugin will attempt to access the `skip_hidden_and_backup` property, which we've just seen will not exist!

The solution to this problem is to use [data migrations](/References/Glossary.md#data-migration), explained below.


# Data Migrations

## What is a Data Migration?

Whenever a new version of a plugin is installed to a Delphix Engine, the engine needs to convert pre-existing data from its old format (as specified by the schemas in the old version of the plugin), to its new format (as specified by the schemas in the new version of the plugin).

A [data migration](/References/Glossary.md#data-migration) is a function that is responsible for doing this conversion. It is provided by the plugin.

Thus, when the new plugin version is installed, the engine will call all applicable data migrations provided by the new plugin. This ensures that all data is always in the format expected by the new plugin.

## A Simple Example

Let's go back to the above example of the plugin that adds a new boolean option to allow users to avoid syncing backup and hidden files. Here is a data migration that the new plugin can provide to handle the data format change:

```python
@plugin.upgrade.linked_source("2019.11.20")
def add_skip_option(old_linked_source):
    return {
      "skipHiddenAndBackup": false
    }
```

The exact rules for data migrations are covered in detail below. Here, we'll just walk through this code line by line and make some observations.

```python
@plugin.upgrade.linked_source("2019.11.20")
```
The above line is a [decorator](/References/Glossary.md#decorator) that identifies the following function as a data migration. This particular migration will handle linked sources. It is given an ID of `2019.11.20` -- this controls when this migration is run in relation to other data migrations.

```python
def add_skip_option(old_linked_source):
```

Note that the data migration takes an argument representing the old-format data. In this simple example, we know that there are no properties in the old-format data, so we can just ignore it.

```python
    return {
      "skipHiddenAndBackup": false
    }
```

Here, we are returning a Python dictionary representing the new format of the data. In this example, the dictionary has only one field: `skipHiddenAndBackup`. Because the old version of the plugin had no ability to skip files, we set this property to `false` to match.


## Rules for Data Migrations

As shown above, the a data migration receives old-format input and produces new-format output. The rules and recommendations for data migrations follow:

### RULES

* Input and output are Python dictionaries, with properties named exactly as specified in the schemas. Note that this differs from other plugin operations, where the inputs are defined with Python classes, and whose properties use Python-style naming.

* Each data migration must be tagged with an ID string. This string must consist of one or more positive integers separated by periods.

* Data migration IDs must be numerically unique. Note that `"1.2"`, `"01.02"`, and "`1.2.0.0.0"` are all considered to be identical.

* Once released, a data migration must never be deleted. An attempted upgrade will fail if the already-installed version has a data migration that does not appear in the to-be-installed version.

* At upgrade time, the engine will find the set of new migrations provided by the new version that are not already part of the already-installed version. Each of these migrations will then be run, in the order specified below.

* After running all applicable migrations, the engine will confirm that the resultant data conforms to the new version's schemas. If not, the upgrade will fail.

* Note that there is no requirement or guarantee that the input or output of any particular data migration will conform to a schema. We only guarantee that the input to the **first** data migration conforms to the schema of the already-installed plugin version. And, we only require that the output of the **final** data migration conforms to the schema of the new plugin version.

* Data migrations are run in the order specified by their IDs. The ordering is numerical, not lexicographical. Thus `"1"` would run before `"2"`, which would run before `"10"`.

* Data migrations have no access to remote hosts. If a data migration attempts to use `run_bash` or similar, the upgrade will fail.

* Note that the above rules imply that at least one data migration is required any time a schema change is made that would invalidate any data produced using a previous version of the plugin.


### Recommendations
* We recommend using a "Year.Month.Date" format like `"2019.11.04"` for migration IDs. You can use trailing integers as necessary (e.g. use `"2019.11.04.5"` if you need something to be run between `"2019.11.04"` and `"2019.11.05"`).

* Even though they follow similar naming rules, migration IDs are not the same thing as plugin versions. We do not recommend using your plugin version in your migration IDs.

* We recommend using small, single-purpose data migrations. That is, if you end up making four schema changes over the course of developing a new plugin version, we recommend writing four different data migrations, one for each change.

## Data Migration Example

Here is a very simple data migration.
```python
@plugin.upgrade.repository("2019.12.15")
def add_new_flag_to_repo(old_repository):
  new_repository = dict(old_repository)
  new_repository["useNewFeature"] = False
  return new_repository
```

MAYBE TODO: Add more examples?
