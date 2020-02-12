# Special Concerns

## Backports and Hotfixes

If your plugin uses an ["enterprise-style"](/Versioning_And_Upgrading/Versioning/#app-style-vs-enterprise-style) release strategy, then you'll probably want to occasionally provide new "minor" versions that build atop older versions.

Code changes that are applied atop old releases are usually called "backports". Sometimes, they are also called "hotfixes", if the change is specifically created for a single user.

### Example
Let's take a look at an example of a possible timeline of releases.

> **February**: The initial version of a plugin is released, with build number "1.0". This is a simple plugin that uses a simple strategy for syncing dsources.

> **April**: A new version is released, with build number "1.1". This adds some bugfixes and adds some small optimzations to improve the performance of syncing.

> **August**: A new version is released, with build number "2.0". This uses a completely new syncing strategy that is far more sophisticated and efficient.

Let's assume that not all users will want to upgrade to the 2.0 release immediately. So, even months later, you will have a significant number of users still on version 1.0 or 1.1.

Later, in October, a bug is found which impacts all releases. This bug is important enough that you want to fix it for **all** of your customers (not just the ones using 2.0).

Here are the behaviors we need:

* Our 2.0 customers should be able to get the new bugfix without giving up any of the major new features that were part of 2.0.
* Our 1.0 and 1.1 customers should be able to get the new bugfix without also needing to accept all the major new features that were part of 2.0.
* Once a customer has received the bugfix, it should be impossible to lose the bugfix in an upgrade.

### Strategy

Here is how this situation would typically be handled:

* Fix the bug by applying a code change atop the 2.0 code.
* Make a new release of the plugin that includes that bugfix, with the build number "2.1".
* Separately, apply the same bugfix atop the 1.1 code. Note: depending on how code changed between 1.1 and 2.0, this 1.1-based bugfix might not contain the exact same code as we used with 2.0.
* Write [compatibility-checking logic](/Versioning_And_Upgrading/Compatibility/#plugin-defined-compatibility)  that disallows any attempt to upgrade to 2.0 (2.1 is allowed, of course)
* Make another new release of the plugin, this time with build number "1.2". This release includes the 1.1-based bugfix and the new compatibility logic.


This meets our requirements:

* Our 2.0 customers can install version 2.1. This gives them the bugfix, and keeps all the features from 2.0.
* Our 1.0 and 1.1 customers can install version 1.2. This gives them the bugfix without any of the 2.0 features.
* It is impossible for a 2.1 customer to lose the bugfix, because the Delphix Engine will not allow the build number to go "backwards". So, a 2.1 customer will not be able to install versions 2.0, 1.1, or 1.0.
* It is also impossible for a 1.2 customer to lose the bugfix.
    * They cannot install 1.0 or 1.1 because the build number is not allowed to decrease.
    * They cannot install 2.0 because of the new compatibility logic.

Note that a 1.2 customer can still upgrade to 2.1 at any time. This will allow them to keep the bugfix, and also take advantage of the new features that were part of 2.0.


## When Data Migrations Are Insufficient

New versions of plugins often require some modification of data that was written using an older version of the same plugin. Data migrations handle this modification. Unfortunately, data migrations cannot always fully handle all possible upgrade scenarios by themselves.

For example, a new plugin version might want to add a new required field to one of its schemas. But, the correct value for this new field might not be knowable while the upgrade is underway -- perhaps it must be entered by the user, or perhaps it would require automatic discovery to be rerun.

Such a situation will require some user intervention after the upgrade.

### Suggested Solution

For such a situation, we recommend the following process:

* Make your schema changes so that the affected property can be set in such a way that plugin code can identify it as being invalid. There are a number of different ways to do this, and the examples below will illustrate two of them.
* In your data migrations, make sure the affected properties are indeed marked invalid.
* In any plugin code that needs to use these properties, first check them for validity. If they are invalid, then raise an error that explains the situation to the user, and tells them what steps they need to take.


### Examples

Following are two examples of schema changes that need extra user intervention after upgrade. One will require a rediscovery, and the other will require the user to enter information.

#### Autodiscovery Example

Suppose that a new plugin version adds a new required field to its repository schema. This new field specifies a full path to a database installation. The following listing shows what we'd like the new repository schema to look like (`installationPath` is the new required property)

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

But, there may be repositories that were discovered before the upgrade. The data migrations will have to ensure that *some* value is provided for this new field. However, a data migration will not be able to determine what the correct final value is. So, the data migration can put some kind of placeholder there.

One way to to this is to modify the schema to allow a special value to indicate that the object needs to be rediscovered. In this example, we'll use the JSON `"null"` type to indicate this:
```
"installationPath": { "type": ["string", "null"], "format": "unixpath"}
```
This schema is saying that the property must either be a string representing a unix path, or else `null`.

So, now our data migration can set this property to the JSON null value (in Python code, this is represented as `None`):
```
TODO: Add working code here of a data migration setting this field to null/None
```

Now, wherever the plugin needs to use this path, we'll need to check to make sure that we really have one.
```
TODO: Add working code example of raising an exception when path is None. Error should say that the host must be rediscovered before the operation in question can be performed.
```


#### Manual Entry

The above example used some JSON schema trickery to allow multiple acceptable datatypes for the same field. This was nice, since it allowed us to very clearly distinguish when an object needed user intervention.

However, that's not usually possible with a user-facing schema. In a user-facing schema, each field usually needs to only accept a single datatype. Otherwise, the UI can become cluttered and ugly, or sometimes even nonfunctional. So, let's look at an option for what to do with a user-facing schema.

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
TODO: Add working code example of a data migration setting the port to 0
```

As with the previous example, our plugin code will need to look for this special value, and raise an error so that the user knows what to do.

```
TODO: Add code example of raising exception when port is 0. User should be told that they need to manually edit the properties of this VDB, and to change the port value.
```
