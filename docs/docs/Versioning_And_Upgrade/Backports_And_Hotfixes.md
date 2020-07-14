# Backports and Hotfixes

If your plugin uses an ["enterprise-style"](/Versioning_And_Upgrade/Versioning.md#enterprise-style-release-strategy) release strategy, then you'll probably want to occasionally provide new "minor" or "patch" versions that build atop older versions.

Code changes that are applied atop old releases are usually called "backports". Sometimes, they are also called "hotfixes", if the change is specifically created for a single user.

These releases present a problem: although they are built atop an older code branch, they are still newer than some releases from a newer code branch. Below, we'll walk through how we prevent users from "upgrading" to a new-branch release that would be incompatible with an installed old-branch release.

### Motivating Example
Let's take a look at an example of a possible timeline of releases.

> **February**: The initial version of a plugin is released, with build number "1.0". This is a simple plugin that uses a simple strategy for syncing dSources.

> **April**: A new version is released, with build number "1.1". This adds some bugfixes and adds some small optimizations to improve the performance of syncing.

> **August**: A new version is released, with build number "2.0". This uses a completely new syncing strategy that is far more sophisticated and efficient.

Let's assume that not all users will want to upgrade to the 2.0 release immediately. So, even months later, you expect to have a significant number of users still on version 1.0 or 1.1.

Later, in October, a bug is found which impacts all releases. This bug is important enough that you want to fix it for **all** of your end users (not just the ones using 2.0).

Here are the behaviors we need:

* Our 2.0 end users should be able to get the new bugfix without giving up any of the major new features that were part of 2.0.
* Our 1.0 and 1.1 end users should be able to get the new bugfix without also needing to accept all the major new features that were part of 2.0.
* Once an end user has received the bugfix, it should be impossible to lose the bugfix in an upgrade.

### Strategy

You can include a [data migration](/Versioning_And_Upgrade/Upgrade.md#data-migrations) along with your bugfix. If your bugfix involves a schema change, you will have to do this anyways. If not, you can still include a data migration that simply does nothing. If a user with the bugfix attempts to "upgrade" to 2.0, the Delphix Engine will prevent it, because the 2.0 releases does not include this migration.

You would typically follow these steps:

* Fix the bug by applying a code change atop the 2.0 code.
* Include the new data migration in your 2.1 release.
* Separately, apply the same bugfix atop the 1.1 code. Note: depending on how code changed between 1.1 and 2.0, this 1.1-based bugfix might not contain the exact same code as we used with 2.0.
* Make another new release of the plugin, this time with build number "1.2". This release includes the 1.1-based bugfix. It also should include the new data migration.


This meets our requirements:

* Our 2.0 end users can install version 2.1. This gives them the bugfix, and keeps all the features from 2.0.
* Our 1.0 and 1.1 end users can install version 1.2. This gives them the bugfix without any of the 2.0 features.
* It is impossible for a 2.1 end user to lose the bugfix, because the Delphix Engine will not allow the build number to go "backwards". So, a 2.1 end user will not be able to install versions 2.0, 1.1, or 1.0.
* It is also impossible for a 1.2 end user to lose the bugfix.
    * They cannot install 1.0 or 1.1 because the build number is not allowed to decrease.
    * They also cannot install 2.0. The missing data migration on 2.0 will prevent this.

Note that a 1.2 end user can still upgrade to 2.1 at any time. This will allow them to keep the bugfix, and also take advantage of the new features that were part of 2.0.
