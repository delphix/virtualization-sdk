# Dealing With Sensitive Data

Often, a plugin will need to handle sensitive user-provided data. The most common example of this is a database password.

Plugins must be careful to handle sensitive data appropriately. Three tips for handling sensitive data are:

1. Tell the Delphix Engine which parts of your data are sensitive.
2. When passing sensitive data to remote plugin library functions (such as `run_bash`), use environment variables.
3. Avoid logging, or otherwise writing out the sensitive data.

Each of these tips are explained below.

## Marking Your Data As Sensitive

Because the Delphix Engine manages the storing and retrieving of plugin-defined data, it needs to know which pieces of data are sensitive. The plugin does this in its [schemas](/References/Glossary.md#schema), by using the special [`password`](/References/Schemas.md#password) keyword.

The following example of a schema defines an object with three properties, one of which is sensitive and tagged with the `password` keyword:

```json
{
    "type": "object",
    "properties": {
        "db_connectionPort": {"type": "string"},
        "db_username": {"type": "string"},
        "db_password": {"type": "string", "format": "password"}
    }
}
```

This tells the Delphix Engine to take special precautions with this password property, as follows:

1. The Delphix Engine will encrypt the password before storing it, and decrypt it only as necessary to pass back to the plugin.
2. The Delphix Engine will not write this password anywhere (for example, it will not appear in any system logs).
3. The Delphix Engine's UI and CLI will not display the password.
4. Clients of the Delphix Engine's public API will not be able to access the password.

!!! note
    Removing a previously added password property from a field and running a [Data Migration](/References/Glossary.md#data-migration) will expose the password in plaintext. If this is intentional, write a migration to ensure that the new property conforms to the new schema.

## Protecting Sensitive Data with Password Vaults

Plugins can also leverage the password vaults configured in the Delphix engine to avoid storing sensitive data in the engine itself. In addition, vaults can rotate secrets seamlessly behind the scenes without requiring Delphix users to update those secrets in the engine. To give users the option to choose between directly entering a secret, such as a password or private key, or retrieving it from a vault, Delphix provides [pre-defined credential types](/References/Schemas.md#delphix-specific-pre-defined-types).

When using these special types, the example above becomes:

```json
{
    "type": "object",
    "properties": {
        "db_connectionPort": {"type": "string"},
        "db_credentials_supplier": {
          "$ref": "https://delphix.com/platform/api#/definitions/passwordCredentialsSupplier"
        }
    }
}
```

For details on how the user can provide the information required for a property such as `db_credentials_supplier`, see the [section on pre-defined types](/References/Schemas.md#delphix-specific-pre-defined-types).

At runtime, the plugin code must convert the credentials information provided by the user into an actual set of credentials that the plugin can use. To do this, the plugin must call the library function [`retrieve_credentials`](/References/Platform_Libraries.md#retrieve_credentials). For example:

```python
from dlpx.virtualization import libs
from dlpx.virtualization.common import PasswordCredentials
...
@plugin.virtual.stop()
def my_virtual_stop(virtual_source, repository, source_config):
  credentials = libs.retrieve_credentials(virtual_source.parameters.db_credentials_supplier)
  assert isinstance(credentials, PasswordCredentials)
  connect_to_dbms(credentials.username, credentials.password)
```


## Using Environment Variables For Remote Data Passing

Sometimes, a plugin will need to pass sensitive data to a remote environment. For example, perhaps a database command needs to be run on a [staging environment](/References/Glossary.md#staging-environment), and that database command will need to use a password.

### Example
Let us take a look at a very simple example where we need to shutdown a database called "inventory" on a target environment by using the `db_cmd shutdown inventory` command. This command will ask for a password on `stdin`, and for our example our password is "hunter2".

If we were running this command by hand, it might look like this:
```bash
$ db_cmd shutdown inventory
Connecting to database instance...
Please enter database password:
```

At this point, we would type in "hunter2", and the command would proceed to shut down the database.

Since a plugin cannot type in the password by hand, it will do something like this instead:

```bash
$ echo "hunter2" | db_cmd shutdown inventory
```

### Don't Do This

First, let us take a look at how **not** to do this! Here is a bit of plugin python code that will run the above command.

```python
from dlpx.virtualization import libs
from dlpx.virtualization.platform import Plugin

plugin = Plugin()

@plugin.virtual.stop()
def my_virtual_stop(virtual_source, repository, source_config):
  # THIS IS INSECURE! DO NOT DO THIS!
  full_command = "echo {} | db_cmd shutdown {}".format(password, db_name)
  libs.run_bash(virtual_source.connection, full_command)
```

This constructs a Python string containing exactly the desired command from above. However, this is not recommended.

The problem here is that there is a cleartext password in the Python string. But, this Python string is not treated as sensitive by the Virtualization Platform. For example, suppose the Virtualization Platform cannot make a connection to the target environment. In which case, it will raise an error containing the Python string, so that people will know what command failed. But, in our example, that would result in the password being part of the cleartext error message.

### Using Environment Variables

The Delphix Engine provides a better way to pass sensitive data to remote bash (or powershell) calls: environment variables. Let us look at a different way to run the same command as above.

```python
from dlpx.virtualization import libs
from dlpx.virtualization.platform import Plugin

plugin = Plugin()

@plugin.virtual.stop()
  # Use environment variables to pass sensitive data to remote commands
  environment_vars = {
    "DATABASE_PASSWORD" : password
  }
  full_command = "echo $DATABASE_PASSWORD | db_cmd shutdown {}".format(db_name)
  libs.run_bash(virtual_source.connection, full_command, variables=environment_vars)
```

!!! note
	We are no longer putting the cleartext password into the Python command string. Instead, we are instructing the Virtualization Platform to put the password into an environment variable on the target environment. The Python command string merely mentions the name of the environment variable, and does not contain the password itself.

Once the command runs on the target environment, Bash will substitute in the password, and the database shutdown will run as expected.

Unlike with the command string, the Virtualization Platform **does** treat environment variables as sensitive information, and will not include them in error messages or internal logs, etc.

## Don't Write Out Sensitive Data

Plugin writers are strongly advised to never write out unencrypted sensitive data. This is common-sense general advice that applies to all areas of programming, not just for plugins. However, there are a couple of special concerns for plugins.

The Virtualization Platform provides logging capabilities to plugins. The generated logs are unencrypted and not treated as sensitive. Therefore, it is important for plugins to **never log sensitive data**.

In addition, remember that your plugin is not treated as sensitive by the Virtualization Platform. Plugin code is distributed unencrypted, and is viewable in cleartext by Delphix Engine users. Sensitive data such as passwords should never be hard-coded in your plugin code.
