# Copyright (c) 2019 by Delphix. All rights reserved.

# Delphix Virtualization SDK

This README is for SDK developers. If you are a plugin developer please refer to [README.md](README.md).

The artifact produced by this repository is a set of Python distributions that make up the SDK.

# Development process

This repository is going through a lot of changes. It is being migrated to GitHub and open sourced. The development process will change throughout this process so please refer back to this README regularly to understand what the current development process is.

At a very high level, our development process usually looks like this:

1. Make changes to SDK and appgate code. Test these changes manually. Iterate on this until you have everything working.
2. Publish a development build of the SDK to artifactory.
3. Update the version of the SDK specified in the app gate.
4. Publish a review for SDK code, and also publish a "provisional" review of appgate code. Address any feedback.
5. Push the SDK code and publish new SDK builds to our internal servers.
6. Finalize your appgate review.
7. Push the appgate changes

Not every type of change requires every step.

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

At the moment blackbox refers to a property file in the app-gate to determine the version of the SDK to install for tests so this property always needs to updated for automated testing.

NOTE: The app-gate does not pull in the wrappers or CLI from this repository.

The easiest way to do both of these is:

1. Update the version of the SDK to something unique and clearly a development build. The standard is `x.y.z-internal-abc-<your_name>`. For example, `1.1.0-internal-001-grant`.
2. Run `./gradlew publishDebug` from the root of this repository.
3. In `appliance/gradle.properties` in the app-gate update `virtualizationSdkVer` to match the SDK version.

Run an appliance-update for manual testing and/or kick off automated blackbox tests by running `git blackbox -s appdata_python_samples` from your app-gate development branch.


## SDK Review and Provisional app-gate review

Once you're finished with local development and testing, you can publish your final SDK review to reviewboard.

In addition, it's customary to publish a "provisional" appgate review, so that people can get insight into how the out-for-review SDK changes will actually be used by the appgate. Of course, this review will contain all your temporary local-build changes mentioned above. So, in your review, you'll want to mention that these temporary changes will be reverted before the review is finalized.

## Pushing and Deploying SDK Code


### Publishing

There are two Gradle tasks that do publishing: `publishDebug` and `publishProd`. They differ in two ways:

1. They publish the Python distributions to separate repositories on Artifactory. `publishDebug` uploads to `dvp-local-pypi`. This is a special repository that has been setup to test the SDK. It falls back our our production PyPI repository, but artifacts uploaded to `dvp-local-pypi` do not impact production artifacts. This should be used for testing. `publishProd` does upload the Python distributions to our production Artifactory PyPI repository, `delphix-local`.

2. `publishProd` runs tests, formatting, and linting while `publishDebug` does not.

NOTE: The external release to `pypi.org` is done outside of the build system.

#### Setup

1. There are two environment variables that need to be set in order to publish: `ARTIFACTORY_PYPI_USER` and `ARTIFACTORY_PYPI_PASS`.

	`ARTIFACTORY_PYPI_USER` and `ARTIFACTORY_PYPI_PASS` are one set of credentials used to upload the Python distributions to our internal PyPI repositories. The credentials are the same for both internal PyPI repositories mentioned above.

   - `ARTIFACTORY_PYPI_USER` and `ARTIFACTORY_PYPI_PASS` is the username/password combo given to you by whoever setup your Artifactory pypi account. This is an account separate from your Artifactory account. If you do not have one, please reach out to the `#artifactory` channel and request a `dvp-uploaders-python` account. See <https://docs.delphix.com/pages/viewpage.action?spaceKey=EO&title=Artifactory-instance#Artifactory-instance-SDKpythonpackages> for directions on how to add the account. These are used to upload the Python distributions to our internal PyPI repositories. The credentials are the same for both internal PyPI repositories mentioned above.

2. `twine` needs to be installed. This is a Python package that is used to upload Python distributions. If it's not installed, install it by running `pip install twine`.

#### Final Publishing

Once you are absolutely certain all changes have been made run `./gradlew publishProd`. This will run checks, create the Python distributions, and upload all of them to Artifactory with the Python distributions going to `delphix-local`.

## Using Newly-Deployed SDK Build

Now, we have to go back to our `appgate` code and make it point to the newly-deployed build on artifactory, instead of the local build we used to test. To achieve that,
modify `appliance/gradle.properties` and change `virtualizationSdkVer` to refer to your new version number.

## Finalizing Appgate Review

Once you've got the above changes completed, tested, and checked into git, you can update your appgate review. Now, your review will be ready for final ship-its.
