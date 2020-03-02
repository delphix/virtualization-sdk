# Copyright (c) 2019 by Delphix. All rights reserved.

# Delphix Virtualization SDK

This README is for SDK developers. If you are a plugin developer please refer to [README.md](README.md).

The artifact produced by this repository is a set of Python distributions that make up the SDK.

## Background

There are two parts of the SDK that are important to think about separately since they have slightly different workflows.

1. The `tools` package is the SDK's CLI. This aids in plugin development, testing, and distribution.
2. `common`, `libs`, and `platform` contain what are collectively called the "wrappers". These are vanilla Python classes
that abstract the Virtualization API protobuf messages (published by app-gate) away from plugin developers. These expose
the API plugin developers write against.

All dependencies of a plugin must be packaged with the plugin including the protobuf messages (`dvp-api`) and the wrappers.
This is done automatically by `dvp build`.

This is what causes the slightly different workflows in development. Changes to `tools` are completely isolated from the
Delphix Engine and wrappers changes only impact the plugin build.

## Development process

At a very high level, our development process usually looks like this:

1. Create a fork of the delphix/virtualization-sdk repository.
2. Clone the forked repository.
3. Make changes to SDK code. Test these changes manually and with unit tests. Iterate on this until you have everything working.
4. Commit your changes and build all Python package distributions. Make sure the version number of the packages is updated appropriately.
5. Publish Python distributions to artifactory. 
7. Run blackbox against the newly uploaded SDK version.
7. Publish a pull request to the delphix/virtualization-sdk once your code is ready for review.
8. Once the pull request is approved, it will merged into delphix/virtualization-sdk repository.

These steps are described in more detail below.

## Local SDK Development

To setup local development, refer to README-dev.md in the `tools` directory. This walks through the setup of a local virtualenv for development. This should be done for _all_ SDK changes.

### Configure pip index

`dvp build` executes `pip` to install the wrappers. By default `pip` looks at pypi.org for packages to install. Internal builds of the SDK are published to artifactory, not pypi. In order to configure pip to look at artifactory, create a file at `<virtualenv-root>/pip.conf` that contains:

```
[install]
trusted-host=artifactory.delphix.com
index-url=http://artifactory.delphix.com/artifactory/api/pypi/dvp-virtual-pypi/simple/
```

### CLI changes

To better understand how to develop and test `tools` changes, see README-dev.md in the `tools` directory.

### Wrappers changes

Run `dvp build --dev` to build your plugin and then upload it to a Delphix Engine to test.

The wrappers are built with the plugin. `dvp build` has a hidden `--dev` flag. This builds `common`, `libs`, and `platform` locally and bundles them with the plugin. A special configuration entry is needed in your dvp config file which is located at `~/.dvp/config`:

```
[dev]
vsdk_root = /path/to/vsdk_repo_root
```

## Versioning

The SDK is shipped as five Python packages that are currently versioned and shipped together: dvp, dvp-common, dvp-libs,
dvp-platform, and dvp-tools. 

The first thing to do is to change the version number of all the packages. Our versioning scheme follows the rules of
semantic versioning in order to help developers manage their "dependency hell". We use bump2version 
(https://github.com/c4urself/bump2version) to make the version management of all five packages easier. Semantic versioning rules are the following:

```
Given a version number MAJOR.MINOR.PATCH, increment the:

    MAJOR version when you make incompatible API changes,
    MINOR version when you add functionality in a backwards compatible manner, and
    PATCH version when you make backwards compatible bug fixes.
```
Source: https://semver.org/

The version format is MAJOR.MINOR.PATCH for released versions and MAJOR.MINOR.PATCH-RELEASE-BUILD for pre-release builds.
For more details see `.bumpversion.cfg` in the root of this repository.

If you want to bump the build number from `1.1.0-internal-7` to `1.1.0-internal-8`, run `bumpversion build`.

If you want to bump the major/minor/patch version, run `bumpversion [major|minor|patch]`.

If you want to get rid of the pre-release label (bump from `1.1.1-internal-7` to `1.1.0`), run `bumpversion release`.

## Testing

Currently, there are three types of SDK testing: unit, manual, and functional (blackbox).

### Unit Testing

Go into one of the package directories (common, dvp, libs, platform, tools) and run the following commands (if you haven't done it already):
1. Install the package's development dependencies: `pip install -r requirements.txt`.
2. Install the package itself in editable mode: `pip install -e .`.
3. Run unit tests: `python -m pytest src/main/python`.

There's no way to locally run unit tests in all packages with one command. However, they will be run automatically through GitHub Actions when you open a pull request. 

### Testing sdk-gate changes with app-gate code

#### Manual testing

Run `dvp build --dev` to build your plugin and then upload it to a Delphix Engine to test.

The wrappers are built with the plugin. `dvp build` has a hidden `--dev` flag. This builds `common`, `libs`, and `platform` locally and bundles them with the plugin. A special configuration entry is needed in your dvp config file which is located at `~/.dvp/config`:

```
[dev]
vsdk_root = /path/to/vsdk_repo_root
```

##### Functional (blackbox) testing
(Now) Let's assume you're working on the SDK version `1.1.0-internal-10`.
To run blackbox tests, follow these steps:
1. Navigate to each package directory (common, dvp, libs, platform, tools) and run `python setup.py sdist bdist_wheel`. This will build Python package distributions.
2. Run `./bin/upload.sh` to upload Python distributions to artifactory. 
2. Navigate to the app-gate directory and run 
`git blackbox -s appdata_python_samples --extra-params="-p sdk-version=1.0.0-internal-10"`.


(Soon) We will be able to move to this process once blackbox runner can build Python distributions without using Gradle.
To run blackbox tests, follow these steps: 
1. Push your code to a branch in the forked repository on Github. Let's say the branch is called `feature1` in repository called `username/virtualization-sdk`.
2. Navigate to the app-gate directory and run 
`git blackbox -s appdata_samples --extra-params="-p virt-sdk-repo=https://github.com/username/virtualization-sdk.git -p virt-sdk-branch=feature1"`.

#### Setup

1. There are two environment variables that need to be set in order to publish: `ARTIFACTORY_PYPI_USER` and `ARTIFACTORY_PYPI_PASS`.

	`ARTIFACTORY_PYPI_USER` and `ARTIFACTORY_PYPI_PASS` are one set of credentials used to upload the Python distributions to our internal PyPI repositories. The credentials are the same for both internal PyPI repositories mentioned above.

   - `ARTIFACTORY_PYPI_USER` and `ARTIFACTORY_PYPI_PASS` is the username/password combo given to you by whoever setup your Artifactory pypi account. This is an account separate from your Artifactory account. If you do not have one, please reach out to the `#artifactory` channel and request a `dvp-uploaders-python` account. See <https://docs.delphix.com/pages/viewpage.action?spaceKey=EO&title=Artifactory-instance#Artifactory-instance-SDKpythonpackages> for directions on how to add the account. These are used to upload the Python distributions to our internal PyPI repositories. The credentials are the same for both internal PyPI repositories mentioned above.

2. `twine` needs to be installed. This is a Python package that is used to upload Python distributions. If it's not installed, install it by running `pip install twine`.
