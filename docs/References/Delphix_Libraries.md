---
title: Virtualization SDK
---

# Delphix Libraries

## run_bash

Executes a bash command on a remote Unix host.

### Signature

`def run_bash(remote_connection, command, variables=None, use_login_shell=False)`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
remote_connection | [SourceConnection](Classes.md#sourceconnection) | Connection associated with the remote host to run the command on.
command | String | Command to run to the host.
variables | dict[String, String] | Optional. Environement variables to set when running the command.
use_login_shell | boolean | Optional. Whether to use a login shell.

### Returns
An object of `RunBashResponse`

Field | Type | Description
----- | ---- | -----------
exit_code | Integer | Exit code from the command.
stdout | String | Stdout from the command.
stderr | String | Stderr from the command.

### Example

```python
from dlpx.virtualization import libs

command = "echo 'Hi' >> /tmp/debug.log"
vars = {"var": "val"}

response = libs.run_bash(connection, command, vars)

print response.exit_code
print response.stdout
print response.stderr
```

## run_expect

Executes a tcl command or script on a remote Unix host.

### Signature

`def run_expect(remote_connection, command, variables=None)`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
remote_connection | [SourceConnection](Classes.md#sourceconnection) | Connection associated with the remote host to run the command on.
command | String | Expect(Tcl) command to run.
variables | dict[String, String] | Optional. Environement variables to set when running the command.

### Returns

None

### Example

```python
from dlpx.virtualization import libs

command = "puts 'Hi'"
vars = {"var": "val"}

libs.run_expect(connection, command, vars)
```

## run_powershell

Executes a powershell command on a remote Windows host.

### Signature

`def run_powershell(remote_connection, command, variables=None)`

### Arguments

Argument | Type | Description
-------- | ---- | -----------
remote_connection | [SourceConnection](Classes.md#sourceconnection) | Connection associated with the remote host to run the command on.
command | String | Command to run to the remote host.
variables | dict[String, String] | Optional. Environement variables to set when running the command.

### Returns
An object of `RunPowershellResponse`

Field | Type | Description
----- | ---- | -----------
exit_code | Integer | Exit code from the command.
stdout | String | Stdout from the command.
stderr | String | Stderr from the command.

### Example

```python
from dlpx.virtualization import libs

command = "Write-Output 'Hi'"
vars = {"var": "val"}

response = libs.run_powershell(connection, command, vars)

print response.exit_code
print response.stdout
print response.stderr
```