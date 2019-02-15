#
# Copyright (c) 2019 by Delphix. All rights reserved.
#

# Delphix Virtualization SDK

This repository contains the Virtualization SDK for building custom data source integrations for the Delphix Dynamic Data Platform.

## SDK Runtime JAR for app-gate

### Development process
Based on the contents of this repository, we build an SDK jar file that we later upload to the artifactory, and pull into the app-gate build. Hence, the following development process follows:
1. Make changes to the SDK files in the virtualization-sdk repo.
2. Build an SDK JAR (described below).
3. Pull the SDK JAR into the app-gate build (also described below).
4. Make app-gate changes.
5. Run appropriate tests.
6. Put up a review for the virtualization-sdk changes and attach app-gate test runs in the testing section.
7. Put up a review for the app-gate changes and include a link to the corresponding virtualization-sdk review. Make sure not include the changes related to pulling in a local SDK JAR described in the later section.
8. Add a link to the app-gate review in the description of the virtualization-sdk review.
9. Once the code is ready to ship, publish the SDK JAR to the artifactory (described in the last section).
10. Push the app-gate changes.

### Building SDK runtime JAR
In order to build an SDK runtime JAR, navigate to the root directory of the repository, and execute:
```
./build.sh
```
The build script will produce a few build directories and output `sdk-<versoion>.jar` file. In order to clean up the build directories, execute `clean.sh` script:
```
./clean.sh
```

### Pulling SDK runtime JAR into app-gate

**IMPORTANT**
Make sure to undo the below changes to `app-gate` code when pushing your code to trunk.

Copy `sdk-<version>.jar` to `appliance/lib` in the `app-gate`. This step applies to both Intellij and Eclipse users.

#### For Intellij users
Now, we have to ensure that the gradle build knows to look for jars in the lib directory. In order to do that, we will have to add the following code to `appliance/gradle-lib/java-common.gradle`:

```
    flatDir {
        dirs "${gradleLibDir}/../lib/"
    }
```

The above entry has to be added in the list of external repositories:

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
Then, go to the gradle build file for the module you want to use the SDK JAR (e.g. `appliance/server/appdata/build.gradle`, `appliance/server/workflow/build.gradle`), and add the following line:
```
compile name: "sdk-<version>"
```
Intellij should notice the changes to your build files and rebuild the project. If you don't have the auto-rebuild option turned on, refresh the gradle build. In order to avoid the conflict of class names, you will have to comment out the line that declares the production SDK JAR as a dependency:
```
implementation group: "com.delphix.virtualization", name: "sdk", version: virtualizationSdkVer
```

#### For Eclipse users
Comment out/remove the following line from `ivy-eclipse-deps.xml`:
```
<dependency org="com.delphix.virtualization" name="sdk" rev="version"/>
```
Add the following entry to `dlpx-app-gate/.classpath`:
```
<classpathentry kind="lib" path="appliance/lib/sdk-<version>.jar"/>
```

### Publishing SDK runtime JAR
Once you're sure that your changes to the virtualization-sdk repo are correct by testing them against the app-gate code, it's time to publish an SDK JAR to production. Make sure that the version of the JAR is correct given the latest published version in [http://artifactory.delphix.com/artifactory/virtualization-sdk/com/delphix/virtualization/sdk/][] and the guidelines of semantic versioning ([https://semver.org/][]). Once you're ready, run the following command from your terminal:
```
curl -H 'X-JFrog-Art-Api: <Artifactory-API-key>' -T /path/to/virtualization-sdk/sdk-<version>.jar "http://artifactory.delphix.com/artifactory/virtualization-sdk/com/delphix/virtualization/sdk/<version>/sdk-<version>.jar"
```
You can retrieve your API key by navigating to [http://artifactory.delphix.com/artifactory/webapp/#/profile][] (make sure you're logged in).

