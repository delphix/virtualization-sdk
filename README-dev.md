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

## Development
 
### Development process

At a very high level, our development process usually looks like this:

1. Create a fork of the delphix/virtualization-sdk repository.
2. Clone the forked repository.
3. Make changes to SDK code. Test these changes manually and with unit tests. Iterate on this until you have everything working.
4. Bump major/minor/patch/build version depending on the scope of the change.
5. Commit your changes. Make sure the version number of the packages is updated appropriately.
6. Push your changes to a branch in the forked repository.
7. Run blackbox tests against that branch.
8. Publish a pull request to the delphix/virtualization-sdk once your code is ready for review.
9. Once the pull request is approved, merge the pull request into delphix/virtualization-sdk repository.

These steps are described in more detail below.

### Development environment
Development should be done in a personal virtualenv. To setup the virtual environment:

1. `virtualenv /path/to/env/root`. This should be a Python 2.7 virtualenv.
2. `source ~/path/to/env/root/bin/activate`.

### Installing the SDK from source
To install the SDK, follow these steps:

1. Create a file at 
    `<virtualenv-root>/pip.conf` that contains:
    
    ```
    [install]
    index-url=https://pypi.org/simple/
    extra-index-url=https://test.pypi.org/simple/
    ```
   
   One of the SDK dependencies - dvp-api - is currently hosted on [test PyPi](https://test.pypi.org/project/dvp-api/). 
   By default `pip` looks at pypi.org for packages to install. In order to successfully install the SDK, you have to 
   configure pip to search an additional package repository - test.pypi.org.
2. Go into one of the package directories (common, dvp, libs, platform, tools) and run the commands below.
3. Install the package's development dependencies: `pip install -r requirements.txt`.
4. Install the package itself (use `-e` flag if you want to install the package in editable mode): `pip install .`.


### CLI changes

To better understand how to develop and test `tools` changes, see [README-dev.md in the tools directory](https://github.com/delphix/virtualization-sdk/blob/develop/tools/README-dev.md).

## Versioning

The SDK is shipped as five Python packages that are currently versioned and shipped together: dvp, dvp-common, dvp-libs,
dvp-platform, and dvp-tools. 

The first thing to do is to change the version number of all the packages. Our versioning scheme follows the rules of
semantic versioning in order to help developers manage their "dependency hell". We use [bump2version](https://github.com/c4urself/bump2version)
to make the version management of all five packages easier. Semantic versioning rules are the following:

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

If you want to get rid of the pre-release label (bump from `1.1.0-internal-7` to `1.1.0`), run `bumpversion release`.

## Testing

Currently, there are three types of SDK testing: unit, manual, and functional (blackbox).

### Unit Testing

Go into one of the package directories (common, dvp, libs, platform, tools) and run the following commands (if you haven't done it already):

1. Install the package's development dependencies: `pip install -r requirements.txt`.
2. Install the package itself in editable mode: `pip install -e .`.
3. Run unit tests: `python -m pytest src/main/python`.

There's no way to locally run unit tests in all packages with one command. However, they will be run automatically
through GitHub Actions when you open a pull request. You can always open a draft pull request 

### Manual testing

#### Wrappers: dvp, common, platform, libs
The only way to manually test the new wrappers code is to build a plugin, upload it to a Delphix Engine and run through
all the standard workflows. The same workflows will be exercised by functional (blackbox) tests.

### Functional (blackbox) testing
To run blackbox tests, follow these steps: 
1. Push your code to a branch in the forked repository on Github. Let's say the branch is called `my-feature` in repository called `<username>/virtualization-sdk`.
2. Navigate to the app-gate directory and start tests using `git blackbox`. For the guide on which test suite to use,
see the next sections.

#### Blackbox tests targeting wrappers (mostly Delphix Engine workflows)
* appdata_python_samples (sample plugins from the app-gate):
`git blackbox -s appdata_python_samples --extra-params="-p virt-sdk-repo=https://github.com/<username>/virtualization-sdk.git -p virt-sdk-branch=my-feature"`,
* appdata_sanity with a direct Python plugin on CentOS 7.3: `git blackbox -s appdata_sanity -c APPDATA_PYTHON_DIRECT_CENTOS73 -a --extra-params="-p virt-sdk-repo=https://github.com/<username>/virtualization-sdk.git -p virt-sdk-branch=my-feature"`,
* appdata_sanity with a staged Python plugin on CentOS 7.3: `git blackbox -s appdata_sanity -c APPDATA_PYTHON_STAGED_CENTOS73 -a --extra-params="-p virt-sdk-repo=https://github.com/<username>/virtualization-sdk.git -p virt-sdk-branch=my-feature"`.

#### Blackbox tests targeting the CLI (~80% CLI tests)
* virtualization_sdk (installs and tests a direct Python plugin on Ubuntu 18): 
`git blackbox -s virtualization_sdk -c APPDATA_SDK_UBUNTU18_DIRECT_CENTOS73 --extra-params="-p virt-sdk-repo=https://github.com/<username>/virtualization-sdk.git -p virt-sdk-branch=my-feature"`,
* virtualization_sdk (installs and tests a staged Python plugin on Ubuntu 18): 
`git blackbox -s virtualization_sdk -c APPDATA_SDK_UBUNTU18_STAGED_CENTOS73 --extra-params="-p virt-sdk-repo=https://github.com/<username>/virtualization-sdk.git -p virt-sdk-branch=my-feature"`.