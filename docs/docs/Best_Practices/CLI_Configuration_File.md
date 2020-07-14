# CLI Configuration File

The CLI configuration file can be used to set default values for CLI command options.

## Location

The configuration file is located in the user's home directory under `.dvp/config`.

```
<USER_HOME>
    └── .dvp
        └── config
```

Your user's home directory will depend on the operating system, but can be referred to using `~` in Unix-based operating systems or `%UserProfile%` in Windows.

## Supported Options

!!! note "Use `default` profile"

	Only the values listed in the `default` profile are used unless they are overridden by values passed in from a command line option with the same name.

The CLI configuration file supports the following options:

### engine
Specifies the Delphix Engine which can be used as part of the [dvp upload](/References/CLI.md#upload) or [dvp download-logs](/References/CLI.md#download-logs) command.

```
engine = engine.example.com
```

### user
Specifies the user to a Delphix Engine which is used as part of the [dvp upload](/References/CLI.md#upload) or [dvp download-logs](/References/CLI.md#download-logs) command.

```
user = admin
```

### password
Specifies the password for the user to a Delphix Engine which is used as part of the [dvp upload](/References/CLI.md#upload) or [dvp download-logs](/References/CLI.md#download-logs) command.

```
password = userpassword
```

### Example

The following example uses all of the supported options for the CLI configuration file:
```
[default]
engine = engine.example.com
user = admin
password = userpassword
```