# Platform Libraries
Delphix provides a set of functions that plugins can use for executing remote commands, etc.

## retrieve_credentials

Takes a [credentials-supplier](Schemas.md#credentialssupplier) object and returns a [`PasswordCredentials`](Classes.md#passwordcredentials) or [`KeyPairCredentials`](Classes.md#keypaircredentials) object. If the credentials supplier refers to a password vault, the operation obtains the credentials from that vault.

The operation accepts only credentials-supplier objects exactly as provided by parameters of the plugin operation, without any changes. Credential suppliers are effectively opaque to plugin code; their internals can change without notice.

### Signature

`def retrieve_credentials(credentials_supplier)`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
credentials_supplier | dict | Unmodified object provided within the `parameters` field of a plugin operation parameter that conforms to [`credentialsSupplier`](Schemas.md#credentialssupplier), [`passwordCredentialsSupplier`](Schemas.md#passwordcredentialssupplier), or [`keyCredentialsSupplier`](Schemas.md#keycredentialssupplier).

### Returns
An object of the abstract type [`Credentials`](Classes.md#credentials). Concretely, a [`PasswordCredentials`](Classes.md#passwordcredentials) or [`KeyPairCredentials`](Classes.md#keypaircredentials).

### Throws
An exception with a descriptive `message` attribute if either:

1. The secret is returned by the vault and the type of this secret does not match the type(s) required by the [`expectedSecretType`](Schemas.md#option-3-cyberark-vault-credentials) property of the credentials supplier. For example, this occurs when the secret is a `keyPair` but `expectedSecretType` is set to `password`. Or,
1. The `credentials_supplier` parameter does not equal any credentials supplier passed to the plugin by the engine.

### Example

```python
from dlpx.virtualization import libs
from dlpx.virtualization.common import PasswordCredentials

@plugin.virtual.stop()
def my_virtual_stop(virtual_source, repository, source_config):
    credentials = libs.retrieve_credentials(virtual_source.parameters.db_credentials_supplier)
    environment_vars = { "DATABASE_USERNAME" : credentials.username }
    if isinstance(credentials, PasswordCredentials):
        environment_vars["DATABASE_PASSWORD"] = credentials.password
    else:
        environment_vars["DATABASE_KEY"] = credentials.private_key
```

## run_bash

Executes a bash command on a remote Unix host.

### Signature

`def run_bash(remote_connection, command, variables=None, use_login_shell=False, check=False)`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
remote_connection | [RemoteConnection](Classes.md#remoteconnection) | Connection associated with the remote host to run the command on.
command | String | Command to run on the host.
variables | dict[String, String] | **Optional**. Environment variables to set when running the command.
use_login_shell | boolean | **Optional**. Whether to use a login shell.
check | boolean | **Optional**. Whether or not to raise an exception if the `exit_code` in the `RunBashResponse` is non-zero.

### Returns
An object of `RunBashResponse`

Field | Type | Description
----- | ---- | -----------
exit_code | Integer | Exit code from the command.
stdout | String | Stdout from the command.
stderr | String | Stderr from the command.

### Examples

##### Calling bash with an inline command.

```python
from dlpx.virtualization import libs

command = "echo 'Hi' >> /tmp/debug.log"
variables = {"var": "val"}

response = libs.run_bash(connection, command, variables)

print response.exit_code
print response.stdout
print response.stderr
```

##### Using parameters to construct a bash command.

```python
from dlpx.virtualization import libs

name = virtual_source.parameters.username
port = virtual_source.parameters.port
command = "mysqldump -u {} -p {}".format(name,port)

response = libs.run_bash(connection, command)
```

##### Running a bash script that is saved in a directory.

###### Python 2.7 recommended approach
```python

 import pkgutil
 from dlpx.virtualization import libs

 script_content = pkgutil.get_data('resources', 'get_date.sh')

 # Execute script on remote host
 response = libs.run_bash(direct_source.connection, script_content)
```
###### Python 3.8 recommended approach
```python

 from importlib import resources
 from dlpx.virtualization import libs

 script_content = resources.read_text('resources', 'get_date.sh')

 # Execute script on remote host
 response = libs.run_bash(direct_source.connection, script_content)
```
For more information please go to [Managing Scripts for Remote Execution](/Best_Practices/Managing_Scripts_For_Remote_Execution.md) section.

## run_expect

Executes a tcl command or script on a remote Unix host.

### Signature

`def run_expect(remote_connection, command, variables=None)`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
remote_connection | [RemoteConnection](Classes.md#remoteconnection) | Connection associated with the remote host to run the command on.
command | String | Expect(Tcl) command to run.
variables | dict[String, String] | **Optional**. Environment variables to set when running the command.

### Returns
An object of `RunExpectResponse`

Field | Type | Description
----- | ---- | -----------
exit_code | Integer | Exit code from the command.
stdout | String | Stdout from the command.
stderr | String | Stderr from the command.

### Example

Calling expect  with an inline command.

```python
from dlpx.virtualization import libs

command = "puts 'Hi'"
variables = {"var": "val"}

repsonse = libs.run_expect(connection, command, variables)

print response.exit_code
print response.stdout
print response.stderr
```

## run_powershell

Executes a powershell command on a remote Windows host.

### Signature

`def run_powershell(remote_connection, command, variables=None, check=False)`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
remote_connection | [RemoteConnection](Classes.md#remoteconnection) | Connection associated with the remote host to run the command on.
command | String | Command to run to the remote host.
variables | dict[String, String] | **Optional**. Environment variables to set when running the command.
check | boolean | **Optional**. Whether or not to raise an exception if the `exit_code` in the `RunPowershellResponse` is non-zero.

### Returns
An object of `RunPowershellResponse`

Field | Type | Description
----- | ---- | -----------
exit_code | Integer | Exit code from the command.
stdout | String | Stdout from the command.
stderr | String | Stderr from the command.

### Example

Calling powershell with an inline command.

```python
from dlpx.virtualization import libs

command = "Write-Output 'Hi'"
variables = {"var": "val"}

response = libs.run_powershell(connection, command, variables)

print response.exit_code
print response.stdout
print response.stderr
```

## run_sync

Copies files from the remote source host directly into the dSource, without involving a staging host.

### Signature

`def run_sync(remote_connection, source_directory, rsync_user=None, exclude_paths=None, sym_links_to_follow=None)`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
remote_connection | [RemoteConnection](Classes.md#remoteconnection) | Connection associated with the remote host to run the command on.
source_directory | String | Directory of files to be synced.
rsync_user | String | **Optional** User who has access to the directory to be synced.
exclude_paths | list[String] | **Optional** Paths to be excluded.
sym_links_to_follow | list[String] | **Optional** Symbollic links to follow if any.

### Returns

None

### Example

```python
from dlpx.virtualization import libs

source_directory = "sourceDirectory"
rsync_user = "rsyncUser"
exclude_paths = ["/path1", "/path2"]
sym_links_to_follow = ["/path3", "/path4"]

libs.run_sync(connection, source_directory, rsync_user, exclude_paths, sym_links_to_follow)
```

## upgrade_password

Takes a plain password and, optionally, a user name and converts them to an object that conforms to [`credentialsSupplier`](Schemas.md#credentialssupplier). This function generalizes an existing password property to allow users to later select an alternative source, such as a password vault.

This function can be called only from [data migrations](/Versioning_And_Upgrade/Upgrade/#data-migrations). The resulting object can be assigned to a property of type [`credentialsSupplier`](Schemas.md#credentialssupplier) or  [`passwordCredentialsSupplier`](Schemas.md#passwordcredentialssupplier).

### Signature

`def upgrade_password(password, username=None)`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
password | String | A plain password.
username | String | **Optional**. A user name.

### Returns
A `dict` object that conforms to [`passwordCredentialsSupplier`](Schemas.md#passwordcredentialssupplier).

### Example

```python
from dlpx.virtualization import libs

@plugin.upgrade.linked_source("2021.02.15")
def convert_password_to_credentials_supplier(old_linked_source):
    new_linked_source = dict(old_linked_source)
    password = old_linked_source["credentials"]
    username = old_linked_source["username"]
    new_linked_source["credentials"] = libs.upgrade_password(password, username)
    del new_linked_source["username"]
    return new_linked_source
```
