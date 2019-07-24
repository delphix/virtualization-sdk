# CLI Configuration File

Save frequently used configuration settings and credentials in a file which is used by the `dvp` CLI.

## Where is the Configuration File Stored?

The `dvp` CLI uses the settings specified in a local file named `config`, in a folder named `.dvp`, which is located in your user's home directory. Your user's home directory will depend on the operating system, but can be referred to using `~` in Unix-based operating systems or `%UserProfile%` in Windows.

For example, the following commands will list files and directories in the `.dvp` folder.
Linux, macOS, or Unix
```
$ ls ~/.dvp
```
Windows
```
C:\> dir "%UserProfile%\.dvp"
```

## Supported config File Settings

!!! note
	Only the values listed in the `default` profile are used unless they are overridden by values passed in from a command line option with the same name.

### Settings

The `dvp` configuration file supports the following settings:

#### engine
Specifies the Delphix Engine which is used as part of any `dvp upload` or `dvp download-logs` command request.

```
engine = engine.example.com
```

#### user
Specifies the user to a Delphix Engine which is used as part of any `dvp upload` or `dvp download-logs` command request.

```
user = admin
```

#### password
Specifies the password for the user to a Delphix Engine which is used as part of any `dvp upload` or `dvp download-logs` command request.

```
password = userpassword
```

### Example

The following example uses all of the supported settings for the `dvp` configuration file:
```
[default]
engine = engine.example.com
user = admin
password = userpassword
```