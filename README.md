# Copyright (c) 2019 by Delphix. All rights reserved.

# Delphix Virtualization SDK

This repository contains the Virtualization SDK for building custom data source integrations for the Delphix Dynamic Data Platform.


# Development process

At a very high level, our development process looks like this:

1. Make local changes to SDK and appgate code. Test these changes locally. Iterate on this until you have everything working.
2. Publish a review for SDK code, and also publish a "provisional" review of appgate code. Address any feedback.
3. Push the SDK code and publish a new SDK build to artifactory.
4. Modify the appgate code to use the newly-published SDK build from artifactory.
5. Finalize your appgate review.
6. Push the appgate changes.

These steps are described in more detail below.

## Local Development

To do local development, we need to generate an SDK build locally. We also need to get appgate code to use that local build, rather than an official build from artifactory.

### Making a Local SDK build

#### Versioning
The first thing to do is to change the version number. In the root of the SDK codebase, open the `build.gradle` file, and change the version. For almost all cases, this will simply involve incrementing the "build number", which is the three-digit number at the very end of the version.

#### Building
In order to build an SDK runtime JAR, navigate to the root directory of the repository, and execute:
```
./build.sh
```
The build script will produce a few build directories and output `sdk-<version>.jar` file.

Note that the build script does not yet do a lot of error checking. So, it is sometimes not immediately apparent if the build did not succeed. Check the timestamp on the `sdk-<version>.jar` file to make sure it's been newly-built. If not, you might have to scroll through the `build.sh` output to find an error message.

#### Cleaning Up
In order to clean up the build directories, execute the `clean.sh` script:
```
./clean.sh
```

### Using a Local SDK Build With Appgate Code

We need to put the local SDK build somewhere that the appgate code can access it, and we need to actually tell the appgate code to use it.

#### Making Local SDK Build Available

This step is easy. Simply copy `sdk-<version>.jar` to `appliance/lib` in the `app-gate`.

Don't forget to check this change into git if you plan on using `git dx-test` or `git appliance-deploy` to test.  (Note: you will **not** be pushing this! We'll undo this change later.)


#### Using Local SDK Build (For Intellij and Delphix Engine use)

Delphix Engine and IntelliJ both use gradle to build.  So, we have to ensure that the gradle build knows how to find and use our local SDK build. This is a two-step process.


**Step 1** We need to tell gradle to look for jars in the `lib` directory. In order to do that, we will have to add the following code to `appliance/gradle-lib/java-common.gradle`:

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

**Step 2** We have to tell gradle to actually use our local SDK where applicable. We have two modules that need to see the SDK: `appdata` and `workflow`. So, we have to edit both `appliance/server/appdata/build.gradle` and `appliance/server/workflow/build.gradle`).

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


## Platform wrappers unit testing

If you added any wrappers to `plugin.py`, you can add corresponding unit tests to `test_plugin.py`.

To run the platform wrappers unit test, run the following command from your terminal in the virtualization-sdk/platform/ directory:
```
../gradlew :platform:test_python2.7
```

## SDK Review and Provisional Appgate review

Once you're finished with local development and testing, you can publish your final SDK review to reviewboard.

In addition, it's customary to publish a "provisional" appgate review, so that people can get insight into how the out-for-review SDK changes will actually be used by the appgate. Of course, this review will contain all your temporary local-build changes mentioned above. So, in your review, you'll want to mention that these temporary changes will be reverted before the review is finalized.

## Pushing and Deploying SDK Code

Once you've got ship-its for your review, you can `git push` them.

We do not yet have an autobuild/autodeploy mechanism for SDK changes, and so you must manually publish a new build to artifactory.

As above, you just need to run `./build.sh` from the root of your SDK repo to build. You should double-check that the name of the generated jar file really matches the correct version format.

To deploy, run the following command from your terminal:
```
curl -H 'X-JFrog-Art-Api: <Artifactory-API-key>' -T /path/to/virtualization-sdk/sdk-<version>.jar "http://artifactory.delphix.com/artifactory/virtualization-sdk/com/delphix/virtualization/sdk/<version>/sdk-<version>.jar"
```
You can retrieve your API key by navigating to http://artifactory.delphix.com/artifactory/webapp/#/profile (make sure you're logged in).


## Using Newly-Deployed SDK Build

Now, we have to go back to our `appgate` code and make it point to the newly-deployed build on artifactory, instead of the local build we used to test.

First, undo the temporary changes we made earlier:
1. Delete `appliance/lib/sdk-<version>.jar`. Make sure you delete from git as well as just removing from the filesystem.
2. Undo your changes to `appliance/gradle-lib/java-common.gradle` so that the gradle build doesn't look for local jars.
3. Undo your changes to `appliance/server/appdata/build.gradle` and `appliance/server/workflow/build.gradle`.
4. If you are an Eclipse user, undo your changes to `ivy-eclipse-deps.xml` and `dlpx-app-gate/.classpath`.

Next, we need to point to our newly-deployed version:
1. Modify `appliance/gradle.properties` and change `virtualizationSdkVer` to refer to your new version number.
2. Modify `ivy-eclipse.deps.xml` and change the `com.delphix.virtualization` line to refer to your new version number.


## Publishing Python packages to internal pypi for nightly Blackbox testing
For Blackbox testing we need to make sure the SDK tool version matches to the
SDK build of the engine. For this we will need to use the SDK python packages generated as part of the
gradle build process. Specifically to test build and upload we need the tools package which contains the
cli. After pushing an appgate side change which will modify the SDK version you will need
to update the SDK version in this repo, rebuild the packages and upload then to our internal pypi repo so that
Blackbox can make use of them in regression.  Once we have the final SDK packaging settled that will
replace this solution.

You will need to have credentials to upload to our internal delphix-virtual-pypi. You can contact devops for this.

Create a .pypirc file in your home directory so you do not have to retype credentials every time.
EX:
```bash
[~] cat ~/.pypirc
[distutils]
index-servers =
    delphix

[delphix]
repository: https://artifactory.delphix.com/artifactory/api/pypi/delphix-virtual-pypi
username: user
password: pass
```

Install twine as other publishing methods are deprecated: `pip install twine`

Run `./gradlew build` to generate the packages. Make sure the version is set correctly in `build.gradle`

Run the following to upload the packages from the virtualization-sdk root directory
```bash
twine upload -r delphix tools/build/python-dist/*
twine upload -r delphix libs/build/python-dist/*
twine upload -r delphix platform/build/python-dist/*
twine upload -r delphix common/build/python-dist/*

```

## Finalizing Appgate Review

Once you've got the above changes completed, tested, and checked into git, you can update your appgate review. Now, your review will be ready for final ship-its.