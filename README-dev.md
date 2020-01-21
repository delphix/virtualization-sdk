# Copyright (c) 2019 by Delphix. All rights reserved.

# Delphix Virtualization SDK

This README is for SDK developers. If you are a plugin developer please refer to [README.md](README.md).

The artifact produced by this repository is a set of Python distributions that make up the SDK.

# Development process

This repository is going through a lot of changes. It is being migrated to GitHub and open sourced. The development process will change throughout this process so please refer back to this README regularly to understand what the current development process is.

At a very high level, our development process usually looks like this:

1. Make changes to SDK and appgate code. Test these changes manually. Iterate on this until you have everything working.
2. Update the version of the SDK.
3. Create a remote branch in the virtualization-sdk Gitlab repo (e.g. projects/my-test).
4. Push your commit to that branch.
5. Publish a review for SDK code. Address any feedback. Run unit and blackbox tests.
6. Push the SDK code.

These steps are described in more detail below.

## Background

There are two parts of the SDK that are important to think about separately since they have slightly different workflows.

1. The `tools` package is the SDK's CLI. This aids in plugin development, testing, and distribution.
2. `common`, `libs`, and `platform` contain what are collectively called the "wrappers". These are vanilla Python classes that abstract the Virtualization API protobuf messages (published by app-gate) away from plugin developers. These expose the API plugin developers write against.

All dependencies of a plugin must be packaged with the plugin including the protobuf messages (`dvp-api`) and the wrappers. This is done automatically by `dvp build`.

This is what causes the slightly different workflows in development. Changes to `tools` are completely isolated from the Delphix Engine and wrappers changes only impact the plugin build.

Unfortunately, at the moment _all_ SDK changes require an app-gate change. Currently BlackBox looks at a property file in the app-gate to determine which version of the SDK to install during tests. This will eventually change, but at the moment any SDK change needs to be accompanied by an app-gate change that, at a minimum, bumps this version.

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

### Versioning
The first thing to do is to change the version number. There are _two_ places where the version needs to be changed unfortunately. For almost all cases, this will simply involve incrementing the "build number", which is the three-digit number at the very end of the version.

1. In the root of the SDK codebase, open the `build.gradle` file, and change the version.
2. In `tools/src/main/python/dlpx/virtualization/_internal/settings.cfg` change the `package_version` property.

The two versions should be identical.

This repository is going through a transition in which Gradle will eventually be removed. The version string will eventually only live in the individual packages themselves.

### Testing

Currently, there are three types of SDK testing: unit, manual, and blackbox.

#### Unit Testing

Running `./gradlew test` from the top level of the repository will run all SDK unit tests. Smaller sets of tests can be run from inside each directory (`common`, `platform`, etc.) by going into that directory and running `../gradlew test`. These can also be run through your IDE.

#### Testing sdk-gate changes with app-gate code

Blackbox expects you to push your SDK changes to a branch on Gitlab.

1. Push your SDK changes to a remote branch on Gitlab, let's call it `projects/my-test`.
2. Navigate to the app-gate directory and run `git blackbox -s appdata_python_samples --extra-params="-p virt-sdk-branch=projects/my-test"`.
If you also want to specify the repository (the Virtualization SDK Gitlab repo is the default), you can do that via `virt-sdk-repo` parameter:
`git blackbox -s appdata_python_samples --extra-params="-p virt-sdk-repo=https://gitlab.delphix.com/virtualization-platform/virtualization-sdk.git -p virt-sdk-branch=projects/my-test"`.
If for some reason you want to build all Python distributions and upload them to artifactory, you can still do that using `sdk-version` parameter:
`git blackbox -s appdata_python_samples --extra-params="-p sdk-version=1.1.0-internal-007-upgrade"`.

For manual testing, you can install the SDK locally, build a plugin using the SDK, and upload it to your Delphix engine. There are no changes required to the app-gate code.

## Pushing and Deploying SDK Code

### Publishing

Since Blackbox can build SDK from source, there's no need to publish the SDK Python distributions to the artifactory. However, if for some reason you need to do that, the process is described below.

There are two Gradle tasks that do publishing: `publishDebug` and `publishProd`. They differ in two ways:

1. They publish the Python distributions to separate repositories on Artifactory. `publishDebug` uploads to `dvp-local-pypi`. This is a special repository that has been setup to test the SDK. It falls back our our production PyPI repository, but artifacts uploaded to `dvp-local-pypi` do not impact production artifacts. This should be used for testing. `publishProd` does upload the Python distributions to our production Artifactory PyPI repository, `delphix-local`.

2. `publishProd` runs tests, formatting, and linting while `publishDebug` does not.

NOTE: The external release to `pypi.org` is done outside of the build system.

#### Setup

1. There are two environment variables that need to be set in order to publish: `ARTIFACTORY_PYPI_USER` and `ARTIFACTORY_PYPI_PASS`.

	`ARTIFACTORY_PYPI_USER` and `ARTIFACTORY_PYPI_PASS` are one set of credentials used to upload the Python distributions to our internal PyPI repositories. The credentials are the same for both internal PyPI repositories mentioned above.

   - `ARTIFACTORY_PYPI_USER` and `ARTIFACTORY_PYPI_PASS` is the username/password combo given to you by whoever setup your Artifactory pypi account. This is an account separate from your Artifactory account. If you do not have one, please reach out to the `#artifactory` channel and request a `dvp-uploaders-python` account. See <https://docs.delphix.com/pages/viewpage.action?spaceKey=EO&title=Artifactory-instance#Artifactory-instance-SDKpythonpackages> for directions on how to add the account. These are used to upload the Python distributions to our internal PyPI repositories. The credentials are the same for both internal PyPI repositories mentioned above.

2. `twine` needs to be installed. This is a Python package that is used to upload Python distributions. If it's not installed, install it by running `pip install twine`.

