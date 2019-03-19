# Getting Started
The Virtualization SDK is a Python package on [PyPI](https://pypi.org/user/delphix/). Install it in your local development environment so you can build and upload a plugin.

The SDK consists of three parts:

- The `dlpx.virtulization.platform` module
- The `dlpx.virtualization.libs` module
- A CLI

The platform and libs modules expose objects and methods needed to develop a plugin. The CLI is used to build and upload a plugin.

## Requirements

- OS X 10.14 or Ubuntu 16+?
- Python 2.7 (Python 3 is not supported)

## Installation
To install the latest version run:

```
$ pip install dvp
```

!!! note "NOTE"
	 We highly recommended that you develop plugins inside of a virtual environment. To learn more about virtual environments, refer to [Virtualenv's documentation](https://virtualenv.pypa.io/en/latest/).
	 
	 The virtual environment needs to use Python 2.7. This is configured when creating the virtualenv:
	 
	 ```$ virtualenv -p /path/to/python2.7/binary ENV```

To install a specific version of the SDK run:

```
$ pip install dvp==<version>
```

!!! note "NOTE"
    The version of the SDK defines the version of the Virtualization Platform API your plugin is built against.

## Basic Usage
Our [CLI reference](References/CLI) page describes commands and provides examples and a help section.

To build your plugin:

```
$ dvp build -c <plugin_config_file> -a <artifact_file>
```

This will generate an upload artifact at `<artifact_file>`. That file can then be uploaded with:

```
$ dvp upload -e <delphix_engine_address> -u <delphix_admin_user>
```

This will prompt you for the Delphix Engine user's password.

## FAQs?

## Troubleshooting