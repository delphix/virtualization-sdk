# Getting Started
The Virtualization SDK is a Python package on [PyPI](https://pypi.org/project/dvp/). Install it in your local development environment so that you can build and upload a plugin.

The SDK consists of three parts:

- The `dlpx.virtulization.platform` module
- The `dlpx.virtualization.libs` module
- A CLI

The platform and libs modules expose objects and methods needed to develop a plugin. The CLI is used to build and upload a plugin.

## Requirements

- macOS 10.10+ or Ubuntu 14.04+
- Python 2.7 (Python 3 is not supported)
- Java 7+

## Installation
To install the latest version of our SDK (0.4.0) run:

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

## Enable the Delphix Engine Feature Flag

Login to the Delphix Engine CLI as the `sysadmin` user:

```
$ ssh sysadmin@<delphix-engine-hostname>
> system
> enableFeatureFlag
> set name=PYTHON_TOOLKITS
> ls
Properties
    type: FeatureFlagParameters
    name: PYTHON_TOOLKITS (*)
> commit
    Feature flag "PYTHON_TOOLKITS" enabled. If using the CLI, log out and log back in to use the feature.
Warning: This feature is only supported for specific configurations. If you do not have explicit permission from your account representative to use this feature, disable it and contact them.
```

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

You will be prompt for the Delphix Engine user's password.

## Troubleshooting

#### Installation fails with incorrect version spec

!!! error
    `'install_requires' must be a string or list of strings containing valid project version requirement specifiers; Expected version spec in enum34;python_version < '3.4' at ;python_version < '3.4'`

This is likely caused by an out of date `setuptools` version (minimum version `38.0.0`) which is often due to not installing the SDK into a virtual environment. To fix this, first setup a virtual environment and attempt to install the SDK there. If you are already using a virtual environment you can update `setuptools` with:

```
$ pip install setuptools --upgrade
```

!!! question "[Survey](https://forms.gle/pMZSzbU6tAkaHxLt8)"
    Please fill out this [survey](https://forms.gle/pMZSzbU6tAkaHxLt8) to give us feedback about this section.
