# Copyright (c) 2019 by Delphix. All rights reserved.

# Delphix Virtualization SDK

This repository contains the Virtualization SDK for building custom data source integrations for the Delphix Dynamic Data Platform.

# Development process

At a very high level, our development process usually looks like this:

1. Make local changes to SDK and appgate code. Test these changes locally. Iterate on this until you have everything working.
2. Publish a review for SDK code, and also publish a "provisional" review of appgate code. Address any feedback.
3. Push the SDK code and publish new SDK builds to our internal servers.
4. Modify the appgate code to use the newly-published SDK build from artifactory.
5. Finalize your appgate review.
6. Push the appgate changes.

These steps are described in more detail below.

## Local Development

To do local development, we need to generate an SDK build locally. We also need to get appgate code to use that local build, rather than an official build from artifactory.

### Making a Local SDK build

There are two separate components in play here -- a JAR that is used by our appgate code, and a Python distribution that is used by end users and by our blackbox tests. There are separate build procedures for each of these.

#### Versioning
The first thing to do is to change the version number. In the root of the SDK codebase, open the `build.gradle` file, and change the version. For almost all cases, this will simply involve incrementing the "build number", which is the three-digit number at the very end of the version.

#### Building the JAR
In order to build an SDK runtime JAR, navigate to the root directory of the repository, and execute:
```
./gradlew jar
```
This will produce the jar under `build/libs`.

Note that the build not yet do a lot of error checking. So, it is sometimes not immediately apparent if the build did not succeed. Check the timestamp on the `sdk-<version>.jar` file to make sure it's been newly-built. If it's not up to date, you might need to modify the script `bin/build.sh` to produce more output, rerun the jar task, and look at the failure messages.

#### Building the Python distribution

To build the Python source distribution, navigate to the root directory of the repository and type:
```
./gradlew sdist
```

The results of this build will be stored in the various `*/build/python-dist` directories. (One each for `common`, `platform`, etc.)

### Testing a Local SDK build

There are three levels of testing:
- Unit Testing
- Testing with appgate code
- Testing with qa-gate code

#### Unit Testing

Running `./gradlew test` from the top level of the repository will run all SDK unit tests. Smaller sets of tests can be run from inside each directory (`common`, `platform`, etc.) by going into that directory and running `../gradlew test`.

#### Testing With Appgate Code

Usually your SDK changes will require corresponding appgate changes. You can test this by importing a "local build" of the SDK JAR into your appgate code, as described below. Once that is done, you can test as you normally would test appgate code: run unit tests, manually test on a VM, run blackbox tests, whatever.

#### Testing With Qa-Gate Code

Unfortunately, there is currently no way to point blackbox tests at a local SDK. You must always publish your Python distribution to our Pypi server (details below) before you can run blackbox tests against it.

### Using a Local SDK Build With Appgate Code

We need to put the local SDK build somewhere that the appgate code can access it, and we need to actually tell the appgate code to use it.

#### Making Local SDK Build Available

This step is easy. Simply copy `build/libs/sdk-<version>.jar` to `appliance/lib` in the `app-gate`.

Don't forget to check this change into git if you plan on using `git dx-test` or `git appliance-deploy` to test.  (Note: you will **not** be pushing this! We'll undo this change later.)


#### Using Local SDK Build (For Intellij and Delphix Engine use)

Delphix Engine and IntelliJ both use gradle to build.  So, we have to ensure that the gradle build knows how to find and use our local SDK build. This is a two-step process.


1. We need to tell gradle to look for jars in the `lib` directory. In order to do that, we will have to add the following code to `appliance/gradle-lib/java-common.gradle`:

	```
	    flatDir {
	        dirs "${gradleLibDir}/../lib/"
	    }
	```

	The above entry has to be added in the list of external repositories. Here is a more complete listing.

	```
	/*
	 * External repositories we fetch jars from. This should never include a repository
	 * that is not managed by Delphix. Third party repos should be mirrored through
	 * http://artifactory.delphix.com/.
	 */
	repositories {
	    /*
	     * Legacy location for jars that were checked directly into the app-gate.
	     */
	    ivy {
	        ivyPattern "${gradleLibDir}/../lib/[module]/ivy-[revision].xml"
	        artifactPattern "${gradleLibDir}/../lib/[module]/[artifact]-[revision].[ext]"
	    }
	    ...
	    ...
	    flatDir {
	        dirs "${gradleLibDir}/../lib/"
	    }
	}
```

2. We have to tell gradle to actually use our local SDK where applicable. We have two modules that need to see the SDK: `appdata` and `workflow`. So, we have to edit both `appliance/server/appdata/build.gradle` and `appliance/server/workflow/build.gradle`).

	We need to add the following line:
	```
	compile name: "sdk-<version>"
	```

	We also need to remove (or comment out) this line so that gradle will not try to use an artifactory build:
	```
	implementation group: "com.delphix.virtualization", name: "sdk", version: virtualizationSdkVer
	```

Once you complete the above two steps, IntelliJ should notice the changes to your build files and rebuild the project. If you don't have the auto-rebuild option turned on, refresh the gradle build.


#### Using Local SDK Build (For Eclipse use)

Eclipse does not use gradle to build, so you have to follow special steps if you're using Eclipse.

Comment out/remove the following line from `ivy-eclipse-deps.xml`:
```
<dependency org="com.delphix.virtualization" name="sdk" rev="version"/>
```

Add the following entry to `dlpx-app-gate/.classpath`:
```
<classpathentry kind="lib" path="appliance/lib/sdk-<version>.jar"/>
```

## SDK Review and Provisional Appgate review

Once you're finished with local development and testing, you can publish your final SDK review to reviewboard.

In addition, it's customary to publish a "provisional" appgate review, so that people can get insight into how the out-for-review SDK changes will actually be used by the appgate. Of course, this review will contain all your temporary local-build changes mentioned above. So, in your review, you'll want to mention that these temporary changes will be reverted before the review is finalized.

## Pushing and Deploying SDK Code


### Publishing

There are two Gradle tasks that do publishing: `publishDebug` and `publishProd`. They differ in two ways:

1. They publish the Python distributions to separate repositories on Artifactory (the jar is always published to the same one.). `publishDebug` uploads to `dvp-local-pypi`. This is a special repository that has been setup to test the SDK. It falls back our our production PyPI repository, but artifacts uploaded to `dvp-local-pypi` do not impact production artifacts. This should be used for testing. `publishProd` does upload the Python distributions to our production Artifactory PyPI repository, `delphix-local`.

2. `publishProd` runs tests, formatting, and linting while `publishDebug` does not.

NOTE: The external release to `pypi.org` is done outside of the build system.

#### Setup

1. There are three environment variables that need to be set in order to publish: `ARTIFACTORY_PYPI_USER`, `ARTIFACTORY_PYPI_PASS`, and `ARTIFACTORY_JAR_KEY`.

	`ARTIFACTORY_PYPI_USER` and `ARTIFACTORY_PYPI_PASS` are one set of credentials used to upload the Python distributions to our internal PyPI repositories. The credentials are the same for both internal PyPI repositories mentioned above.
	`ARTIFACTORY_JAR_KEY`

   - `ARTIFACTORY_PYPI_USER` and `ARTIFACTORY_PYPI_PASS` is the username/password combo given to you by whoever setup your Artifactory pypi account. This is an account separate from your Artifactory account. If you do not have one, please reach out to the `#artifactory` channel and request a `dvp-uploaders-python` account. See <https://docs.delphix.com/pages/viewpage.action?spaceKey=EO&title=Artifactory-instance#Artifactory-instance-SDKpythonpackages> for directions on how to add the account. These are used to upload the Python distributions to our internal PyPI repositories. The credentials are the same for both internal PyPI repositories mentioned above.
   - `ARTIFACTORY_JAR_KEY` is your Artifactory API key and is used to upload the jar. It can be retreived from http://artifactory.delphix.com/artifactory/webapp/#/profile. You may have to login. This is different from the PyPI credentials because the artifacts are being uploaded to different repositories on Artifactory.

2. `twine` needs to be installed. This is a Python package that is used to upload Python distributions. If it's not installed, install it by running `pip install twine`.


#### Debug Publishing

Run `./gradlew publishDebug`. This will build the jar, every Python distribution, and upload them to Artifactory with the Python distributions going to our testing repository, `dvp-local-pypi`.

You can install `dvp` from this repository with the command `pip install -i https://artifactory.delphix.com/artifactory/api/pypi/dvp-local-pypi/simple dvp==<version>`.

#### Final Publishing

Once you are absolutely certain all changes have been made run `./gradlew publishProd`. This will run checks, build the jar, create the Python distributions, and upload all of them to Artifactory with the Python distributions going to `delphix-local`.

## Using Newly-Deployed SDK Build

Now, we have to go back to our `appgate` code and make it point to the newly-deployed build on artifactory, instead of the local build we used to test.

First, undo the temporary changes we made earlier:
1. Delete `appliance/lib/sdk-<version>.jar`. Make sure you delete from git as well as just removing from the filesystem.
2. Undo your changes to `appliance/gradle-lib/java-common.gradle` so that the gradle build doesn't look for local jars.
3. Undo your changes to `appliance/server/appdata/build.gradle` and `appliance/server/workflow/build.gradle`.
4. If you are an Eclipse user, undo your changes to `ivy-eclipse-deps.xml` and `dlpx-app-gate/.classpath`.

Next, we need to point to our newly-deployed version:
1. Modify `appliance/gradle.properties` and change `virtualizationSdkVer` to refer to your new version number.
2. Modify `ivy-eclipse-deps.xml` and change the `com.delphix.virtualization` line to refer to your new version number.

## Finalizing Appgate Review

Once you've got the above changes completed, tested, and checked into git, you can update your appgate review. Now, your review will be ready for final ship-its.
