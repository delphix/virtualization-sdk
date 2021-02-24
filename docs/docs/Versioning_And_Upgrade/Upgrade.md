# Upgrade
Upgrade is the process of moving from an older version of a plugin to a newer version.
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

!!! info "Zero dSource and VDB downtime during plugin upgrade"
    dSources and VDBs do not need to be disabled before a plugin upgrade is initiated. End users can continue to access data from existing VDBs during a plugin upgrade. However, while a particular plugin is in the process of being upgraded, no administrative Delphix Engine operations like: VDB Refresh, VDB Provision, dSource Disable/Enable etc will be allowed on the objects associated with that plugin. Objects associated with other plugins will not be affected.

## Data Migrations

### What is a Data Migration?

Whenever a new version of a plugin is installed on a Delphix Engine, the engine needs to migrate pre-existing data from its old format (as specified by the schemas in the old version of the plugin), to its new format (as specified by the schemas in the new version of the plugin).

A [data migration](/References/Glossary.md#data-migration) is a function that is responsible for doing this conversion. It is provided by the plugin.

Thus, when the new plugin version is installed, the engine will call all applicable data migrations provided by the new plugin. This ensures that all data is always in the format expected by the new plugin.

### A Simple Example

Let's go back to the above example of the plugin that adds a new boolean option to allow users to avoid syncing backup and hidden files. Here is a data migration that the new plugin can provide to handle the data format change:

```python
@plugin.upgrade.linked_source("2019.11.20")
def add_skip_option(old_linked_source):
    return {
      "skipHiddenAndBackup": false
    }
```

The exact rules for data migrations are covered in detail [below](Upgrade.md#rules-for-data-migrations). Here, we'll just walk through this code line by line and make some observations.

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

Here, we are returning a Python dictionary representing the new format of the data. In this example, the dictionary has only one field: `skipHiddenAndBackup`. Because the old version of the plugin had no ability to skip files, we default this property to `false` to match the new schema.


### Rules for Data Migrations

As shown above, the a data migration receives old-format input and produces new-format output. The rules and recommendations for data migrations follow:

#### Rules

* Input and output are Python dictionaries, with properties named exactly as specified in the schemas. Note that this differs from other plugin operations, where the inputs are defined with autogenerated Python [classes](/References/Schemas_and_Autogenerated_Classes.md), and whose properties use Python-style naming.

* Each data migration must be tagged with an ID string. This string must consist of one or more positive integers separated by periods.

* Data migration IDs must be numerically unique. Note that `"1.2"`, `"01.02"`, and "`1.2.0.0.0"` are all considered to be identical.

* Once released, a data migration must never be deleted. An attempted upgrade will fail if the already-installed plugin version has a data migration that does not appear in the to-be-installed version.

* At upgrade time, the engine will find the set of new migrations provided by the new version that are not already part of the already-installed version. Each of these migrations will then be run, in the order specified below.

* After running all applicable migrations, the engine will confirm that the resultant data conforms to the new version's schemas. If not, the upgrade will fail.

* Note that there is no requirement or guarantee that the input or output of any particular data migration will conform to a schema. We only guarantee that the input to the **first** data migration conforms to the schema of the already-installed plugin version. And, we only require that the output of the **final** data migration conforms to the schema of the new plugin version.

* Data migrations are run in the order specified by their IDs. The ordering is numerical, not lexicographical. Thus `"1"` would run before `"2"`, which would run before `"10"`.

* With the exception of [`upgrade_password`](/References/Platform_Libraries.md#upgrade_password), data migrations have no access to most [Platform Libraries](/References/Platform_Libraries.md) or remote hosts. For example: If a data migration attempts to use [run_bash](/References/Platform_Libraries.md#run_bash) the upgrade will fail.

* Password properties can be generalized to [credential-supplying objects](/References/Schemas.md#credentialssupplier) that offer alternative mechanisms for obtaining passwords and secrets, such as password vaults. To achieve that, a data migration must call [`upgrade_password`](/References/Platform_Libraries.md#upgrade_password).

* Note that the above rules imply that at least one data migration is required any time a schema change is made that would invalidate any data produced using a previous version of the plugin. For example: adding a `"required"` property to the new schema.


#### Recommendations
* We recommend using a "Year.Month.Date" format like `"2019.11.04"` for migration IDs. You can use trailing integers as necessary (e.g. use `"2019.11.04.5"` if you need something to be run between `"2019.11.04"` and `"2019.11.05"`).

* Even though they follow similar naming rules, migration IDs are not the same thing as plugin versions. We do not recommend using your plugin version in your migration IDs.

* We recommend using small, single-purpose data migrations. That is, if you end up making four schema changes over the course of developing a new plugin version, we recommend writing four different data migrations, one for each change.

### Data Migration Example

Here is a very simple data migration.
```python
@plugin.upgrade.repository("2019.12.15")
def add_new_flag_to_repo(old_repository):
  new_repository = dict(old_repository)
  new_repository["useNewFeature"] = False
  return new_repository
```

### Debugging Data Migration Problems

During the process of upgrading to a new version, the Delphix Engine will run all applicable data migrations, and then ensure that the resulting object matches the new schema. But, what if there is a bug, and the resulting object does **not** match the schema?

#### Security Concerns Prevent Detailed Error Messages
One problem here is that the Delphix Engine is limited in the information that it can provide in the error message. Ideally, the engine would say exactly what was wrong with the object (e.g.: "The field `port` has the value `15`, but the schema says it has to have a value between `256` and `1024`").

But, the Delphix Engine cannot do this for security reasons. Ordinarily, the Delphix Engine knows which fields contain sensitive information, and can redact such fields from error messages. But, the only reason the Delphix Engine has that knowledge is because the schema provides that information. If an object does **not** conform to the schema, then the Delphix Engine can't know what is sensitive and what isn't.

Therefore, the error message here might lack the detail necessary to debug the problem.

#### One Solution: Temporary Logging

During development of a new plugin version, you may find yourself trying to find and fix such a bug.
One technique is to use temporary logging.

For example, while you are trying to locate and fix the bug, you could put a log statement at the very end of each of your data migrations, like so:
```
  logger.debug("Migration 2010.03.01 returning {}".format(new_object))
  return new_object
```

See the [Logging](/References/Logging.md) section for more information about logging works.

From the logs, you'll be able to see exactly what each migration is returning. From there, hopefully the problem will become apparent. As a supplemental tool, consider pasting these results (along with your schema) into an online JSON validator for more information.

!!! warning
    It is **very important** that you only use logging as a temporary debugging strategy. **Such logging must be removed before you release the plugin to end users**. If this logging ends up in your end product, it could cause a serious security concern. Please see our [sensitive data best practices](/Best_Practices/Sensitive_Data.md) for more information.

### When Data Migrations Are Insufficient

New versions of plugins often require some modification of data that was written using an older version of the same plugin. Data migrations handle this modification. Unfortunately, data migrations cannot always fully handle all possible upgrade scenarios by themselves.

For example, a new plugin version might want to add a new required field to one of its schemas. But, the correct value for this new field might not be knowable while the upgrade is underway -- perhaps it must be entered by the user, or perhaps it would require automatic discovery to be rerun.

Such a situation will require some user intervention after the upgrade.

In all cases, of course you will want to **clearly document** to your users that there will extra work required so they can make sure they known what they are getting into before they decide to upgrade.

!!! tip
    It should also be said that you should try to avoid cases like this.  As much as possible, try to make your post-upgrade plugin function with no user intervention. Only resort to user intervention as a last resort.

The recommended strategy here is to arrange for the affected objects to be in an "invalid" state, and for your plugin code to detect this state, and throw errors when the objects are used.

For such a situation, we recommend the following process:

* Make your schema changes so that the affected property can be set in such a way that plugin code can identify it as being invalid. Typically this is done by allowing for some "sentinel" value. This may require you to have a less-strict schema definition than you might otherwise want.
* In your data migrations, make sure the affected properties are indeed marked invalid.
* In any plugin code that needs to use these properties, first check them for validity. If they are invalid, then raise an error that explains the situation to the user, and tells them what steps they need to take.

Following are two examples of schema changes that need extra user intervention after upgrade. One will require a rediscovery, and the other will require the user to enter information.

#### Autodiscovery Example

Suppose that a new plugin version adds a new required field to its repository schema. This new field specifies a full path to a database installation. The following listing shows what we'd ideally like the new repository schema to look like (`installationPath` is the new required property)

```
"repositoryDefinition": {
    "type": "object",
    "properties": {
        "name": { "type": "string" },
        "installationPath": { "type": "string", "format": "unixpath"}
    },
    "required": ["name", "installationPath"],
    "nameField": "name",
    "identityFields": ["name"]
}
```

The new plugin's autodiscovery code will know how to find this full path. Therefore, any repositories that are discovered (or rediscovered) after the upgrade will have this path filled in correctly.

But, there may be repositories that were discovered before the upgrade. The data migrations will have to ensure that *some* value is provided for this new field. However, a data migration will not be able to determine what the correct final value is.

One way to handle this is to modify the schema to allow a special value to indicate that the object needs to be rediscovered. In this example, we'll change the schema from the ideal version above, removing the `unixpath` constraint on this string:
```
"installationPath": { "type": "string" }
```

Now, our data migration can set this property to some special sentinel value that will never be mistaken for an actual installation path.
```
_REDISCOVERY_TOKEN = "###_REPOSITORY_NEEDS_REDISCOVERY_###"

@plugin.upgrade.repository("2020.02.04.01")
def repo_path(old_repository):
    # We need to add in a repository path, but there is no way for us to know
    # what the correct path is here, so we cannot set this to anything useful.
    # Instead, we'll set a special sentinel value that will indicate that the
    # repository is unusable until the remote host is rediscovered.
    old_repository["installationPath"] = _REDISCOVERY_TOKEN
    return old_repository
```

Now, wherever the plugin needs to use this path, we'll need to check for this sentinel value, and error out if we find it.  For example, we might need a valid path during the `configure` operation:
```
@plugin.virtual.configure()
def configure(virtual_source, snapshot, repository):
    if repository.installation_path == _REDISCOVERY_TOKEN:
        # We cannot use this repository as/is -- it must be rediscovered.
        msg = 'Unable to use repository "{}" because it has not been updated ' \
        'since upgrade. Please re-run discovery and try again'
        raise UserError(msg.format(repository.name))

    # ... actual configure code goes here
```

#### Manual Entry

Above, we looked at an example where the plugin could handle filling in new values for a new field at discovery time, so the user was simply asked to rediscover.

Sometimes, though, users themselves will have to be the ones to supply new values.

Suppose that a new plugin version wants to add a required field to the `virtualSource` object. This new property will tell which port the database should be accessible on. Ideally, we might want our new field to look like this:

```
"port": {"type": "integer", "minimum": 1024, "maximum": 65535}
```

Again, however, the data migration will not know which value is correct here. This is something the user must decide. Still, the data migration must provide *some* value. As before, we'll change the schema a bit from what would be ideal:

```
"port": {"type": "integer", "minimum": 0, "maximum": 65535}
```

Now, our data migration can use the value `0` as code for "this VDB needs user intervention".

```
@plugin.upgrade.virtual_source("2020.02.04.02")
def add_dummy_port(old_virtual_source):
    # Set the "port" property to 0 to act as a placeholder.
    old_virtual_source["port"] = 0
    return old_virtual_source
```

As with the previous example, our plugin code will need to look for this special value, and raise an error so that the user knows what to do. This example shows the [Virtual Source Reconfigure](/References/Plugin_Operations.md#virtual-source-reconfigure) operation, but of course, similar code will be needed anywhere else that the new `port` property is required.

```
@plugin.virtual.reconfigure()
def virtual_reconfigure(virtual_source, repository, source_config, snapshot):
    if virtual_source.parameters.port == 0:
        raise UserError('VDB "{}" cannot function properly. Please choose a ' \
        'port number for this VDB to use.'.format(virtual_source.parameters.name))

    # ... actual reconfigure code goes here
```
