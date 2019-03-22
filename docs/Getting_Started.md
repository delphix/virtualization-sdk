# Getting Started
The Virtualization SDK is a Python package on [PyPI](https://pypi.org/user/delphix/). Install it in your local development environment so that you can build and upload a plugin.

The SDK consists of three parts:

- The `dlpx.virtulization.platform` module
- The `dlpx.virtualization.libs` module
- A CLI

The platform and libs modules expose objects and methods needed to develop a plugin. The CLI is used to build and upload a plugin.

## Requirements

- OS X 10.14 or Ubuntu 16+?
- Python 2.7 (Python 3 is not supported)

## Installation
To install the latest version of our SDK run:

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

!!! note "API Build Version"
    The version of the SDK defines the version of the Virtualization Platform API your plugin will be built against.

## Basic Usage

Our [CLI reference](References/CLI) describes commands, provides examples, and a help section.

To build your plugin:

```
$ dvp build -c <plugin_config_file> -a <artifact_file>
```

This will generate an upload artifact at `<artifact_file>`. That file can then be uploaded with:

```
$ dvp upload -e <delphix_engine_address> -u <delphix_admin_user> -a <artifact_file>
```

You will be prompt for the Delphix Engine user's password.

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

## FAQs?

## Troubleshooting

#### Installation fails with `'install_requires' must be a string or list of strings containing valid project version requirement specifiers; Expected version spec in enum34;python_version < '3.4' at ;python_version < '3.4'`

This is likely caused by an out of date `setuptools` version which is often due to not installing the SDK into a virtual environment. To fix this, first setup a virtual environment and attempt to install the SDK there. If you are already using a virtual environment you can update `setuptools` with:

```
$ pip install setuptools --upgrade
```
