# Special Concerns

## Backports and Hotfixes

If your plugin uses an ["enterprise-style"](/Versioning_And_Upgrading/Versioning/#app-style-vs-enterprise-style) release strategy, then you'll probably want to occasionally provide new "minor" versions that build atop older versions.

Code changes that are applied atop old releases are usually called "backports". Sometimes, they are also called "hotfixes", if the change is specifically created for a single user.

These releases present a problem: although they are built atop an older code branch, they are still newer than some releases from a newer code branch. Below, we'll walk through how we prevent users from "upgrading" to a new-branch release that would be incompatible with an installed old-branch release.

### Motivating Example
Let's take a look at an example of a possible timeline of releases.

> **February**: The initial version of a plugin is released, with build number "1.0". This is a simple plugin that uses a simple strategy for syncing dSources.

> **April**: A new version is released, with build number "1.1". This adds some bugfixes and adds some small optimizations to improve the performance of syncing.

> **August**: A new version is released, with build number "2.0". This uses a completely new syncing strategy that is far more sophisticated and efficient.

Let's assume that not all users will want to upgrade to the 2.0 release immediately. So, even months later, you expect to have a significant number of users still on version 1.0 or 1.1.

Later, in October, a bug is found which impacts all releases. This bug is important enough that you want to fix it for **all** of your customers (not just the ones using 2.0).

Here are the behaviors we need:

* Our 2.0 customers should be able to get the new bugfix without giving up any of the major new features that were part of 2.0.
* Our 1.0 and 1.1 customers should be able to get the new bugfix without also needing to accept all the major new features that were part of 2.0.
* Once a customer has received the bugfix, it should be impossible to lose the bugfix in an upgrade.

### Strategy

There are two general strategies you can use here:

* You can write [compatibility-checking logic](/Versioning_And_Upgrading/Compatibility/#plugin-defined-compatibility) that explicitly prevents any attempted 2.0 upgrade that would mean losing the bugfix.
* You can include a [data migration](/Versioning_And_Upgrading/Upgrading/#data-migrations) along with your bugfix. If your bugfix involves a schema change, you will have to do this anyways. If not, you can still include a data migration that simply does nothing. If a user with the bugfix attempts to "upgrade" to 2.0, the Delphix Engine will prevent it, because the 2.0 releases does not include this migration.

You would typically follow these steps:

* Fix the bug by applying a code change atop the 2.0 code.
* Make a new release of the plugin that includes that bugfix, with the build number "2.1". If you are using the data migration strategy, then include the new data migration in your 2.1 release.
* Separately, apply the same bugfix atop the 1.1 code. Note: depending on how code changed between 1.1 and 2.0, this 1.1-based bugfix might not contain the exact same code as we used with 2.0.
* If you're using the custom compatibility strategy, then write the compatibility logic alongside that 1.1-based bugfix.
* Make another new release of the plugin, this time with build number "1.2". This release includes the 1.1-based bugfix. It also should include either the new data migration or the new compatibility logic.


This meets our requirements:

* Our 2.0 customers can install version 2.1. This gives them the bugfix, and keeps all the features from 2.0.
* Our 1.0 and 1.1 customers can install version 1.2. This gives them the bugfix without any of the 2.0 features.
* It is impossible for a 2.1 customer to lose the bugfix, because the Delphix Engine will not allow the build number to go "backwards". So, a 2.1 customer will not be able to install versions 2.0, 1.1, or 1.0.
* It is also impossible for a 1.2 customer to lose the bugfix.
    * They cannot install 1.0 or 1.1 because the build number is not allowed to decrease.
    * They also cannot install 2.0. Either the compatibility logic, or the data migration, will prevent this.

Note that a 1.2 customer can still upgrade to 2.1 at any time. This will allow them to keep the bugfix, and also take advantage of the new features that were part of 2.0.


## When Data Migrations Are Insufficient

New versions of plugins often require some modification of data that was written using an older version of the same plugin. Data migrations handle this modification. Unfortunately, data migrations cannot always fully handle all possible upgrade scenarios by themselves.

For example, a new plugin version might want to add a new required field to one of its schemas. But, the correct value for this new field might not be knowable while the upgrade is underway -- perhaps it must be entered by the user, or perhaps it would require automatic discovery to be rerun.

Such a situation will require some user intervention after the upgrade.

In all cases, of course you will want to **clearly document** to your users that there will extra work required so they can make sure they known what they are getting into before they decide to upgrade.

It should also be said that you should try to avoid cases like this.  As much as possible, try to make your post-upgrade plugin function with no user intervention. Only resort to user intervention as a last resort.

### Forcing User Intervention After Plugin Upgrade

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

As with the previous example, our plugin code will need to look for this special value, and raise an error so that the user knows what to do. This example shows the status operation, but of course, similar code will be needed anywhere else that the new `port` property is required.

```
@plugin.virtual.status()
def virtual_status(virtual_source, repository, source_config):
    if virtual_source.parameters.port == 0:
        raise UserError('VDB "{}" cannot function properly. Please choose a ' \
        'port number for this VDB to use.'.format(virtual_source.parameters.name))

    # ... actual status checking code goes here
```

## Debugging Data Migration Problems

During the process of upgrading to a new version, the Delphix Engine will run
all applicable data migrations, and then ensure that the resulting object
matches the new schema. But, what if there is a bug, and the resulting object
does **not** match the schema?

### Security Concerns Prevent Detailed Error Messages
One problem here is that the Delphix Engine is limited in the information that
it can provide in the error message. Ideally, the engine would say exactly what
was wrong with the object (e.g.: "The field `port` has the value `15`, but the
schema says it has to have a value between `256` and `1024`").

But, the Delphix Engine cannot do this for security reasons. Ordinarily, the
Delphix Engine knows which fields contain sensitive information, and can redact
such fields from error messages. But, the only reason the engine has that
knowledge is because the schema provides that information. If an object does
**not** conform to the schema, then the Delphix Engine can't know what is
sensitive and what isn't.

Therefore, the error message here might lack the detail necessary to debug the
problem.

### One Solution: Temporary Logging

During development of a new plugin version, you may find yourself trying to find
and fix such a bug.

One technique is to use temporary logging.

For example, while you are trying to locate and fix the bug, you could put a log
statement at the very end of each of your data migrations, like so:
```
  logger.debug("Migration 2010.03.01 returning {}".format(new_object))
  return new_object
```

See the [Logging](/References/Logging.md) section for more information about
logging works.

From the logs, you'll be able to see exactly what each migration is returning.
From there, hopefully the problem will become apparent. As a supplemental tool,
consider pasting these results (along with your schema) into an online JSON
validator for more information.

Note: It is **very important** that you only use logging as a temporary
debugging strategy. **Such logging must be removed before you release the plugin
to end users**. If this logging ends up in your end product, it could cause
a serious security concern. Please see our
[sensitive data best practices](/Best_Practices/Sensitive_Data.md) for more
information.
