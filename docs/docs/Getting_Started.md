# Getting Started
The Virtualization SDK is a Python package on [PyPI](https://pypi.org/project/dvp/). Install it in your local development environment so that you can build and upload a plugin.

The SDK consists of three parts:

- The `dlpx.virtulization.platform` module
- The `dlpx.virtualization.libs` module
- A CLI

The platform and libs modules expose objects and methods needed to develop a plugin. The CLI is used to build and upload a plugin.

## Requirements

- macOS 10.14+, Ubuntu 16.04+, or Windows 10
- Python 2.7 (Python 3 is not supported)
- Java 7+
- Delphix Engine 6.0.7.0 or above

## Installation
To install the latest version of the SDK run:

```
$ pip install dvp
```

!!! tip "Use a Virtual Environment"
	 We highly recommended that you develop plugins inside of a virtual environment. To learn more about virtual environments, refer to [Virtualenv's documentation](https://virtualenv.pypa.io/en/latest/).

	 The virtual environment needs to use Python 2.7. This is configured when creating the virtualenv:

	 ```$ virtualenv -p /path/to/python2.7/binary ENV```

To install a specific version of the SDK run:

```
$ pip install dvp==<version>
```

To upgrade an existing installation of the SDK run:

```
$ pip install dvp --upgrade
```

!!! note "API Build Version"
    The version of the SDK defines the version of the Virtualization Platform API your plugin will be built against.

## Basic Usage

Our [CLI reference](/References/CLI.md) describes commands, provides examples, and a help section.

To build your plugin:

```
$ dvp build -c <plugin_config> -a <artifact_file>
```

This will generate an upload artifact at `<artifact_file>`. That file can then be uploaded with:

```
$ dvp upload -e <delphix_engine_address> -u <delphix_admin_user> -a <artifact_file>
```

You will be prompted for the Delphix Engine user's password.

You can also use a [CLI Configuration File](/Best_Practices/CLI_Configuration_File.md) to set default values for [CLI](/References/CLI.md) command options.

## Questions?

If you have questions, bugs or feature requests reach out to us via the [Virtualization SDK GitHub repository](https://github.com/delphix/virtualization-sdk/).
