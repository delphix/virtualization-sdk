# Versioning

Almost all software products are periodically updated to include new features and bug fixes. Plugins are no exception -- a plugin's code will very likely be different two years from now.

To deal with this, plugins use **versioning**. This just means that a plugin communicates (to the user, and to the Delphix Engine) exactly what code is in use.

## Versioning Information

There are three different pieces of version-related information, each used for different purposes.

### External Version

This field is intended only for use by the end user. The Delphix Engine does not use this field, and therefore imposes no restrictions on its content. This is a free-form string which the plugin can use in any way it feels like.

Examples might be "5.3.0", "2012B", "MyPlugin Millennium Edition, Service Pack 3", "Playful Platypus" or "Salton City".

The external version is specified using the `externalVersion` property in your [plugin config](/References/Plugin_Config/) file.

### Build Number

Unlike "external version", this field is intended to convey information to the Delphix Engine. This is a string of integers, separated by periods. Examples would be "5.3.0", "7", "5.3.0.0.0.157".

The Delphix Engine uses the build number to guard against users trying to "downgrade" their plugin to an older, incompatible version. So, if a user has build number "3.4.1" installed, then they may not install a version with a build number like "2.x.y", "3.3.y" or "3.4.0".

The build number is specified using the `buildNumber` property in your [plugin config](/References/Plugin_Config/) file.

This field is required to be a string. You might need to enclose your build number in quotes in order to prevent YAML from interpreting the field as a number. For example:
```
        buildNumber: "1"   # OK: The quotes mean this is a string.
        buildNumber: 1     # BAD: YAML will interpret this as an integer.
        buildNumber: "1.2" # OK: The quotes mean this is a string.
        buildNumber: 1.2   # BAD: YAML will interpret this as a floating-point number.
        buildNumber: 1.2.3 # OK: YAML treats this as a string, since it cannot be a number.
```

#### Build Number Format Rules

Your build number must be a string, conforming to these rules:

* The string must be composed of a sequence of non-negative integers, not all zero, separated by periods.
* Trailing zeros are ignored. So, "1.0.0" is treated the same as "1".
* Build numbers are sortable numerically, with earlier numbers having more significance than later numbers. So, "2.0" comes after "1.99999", and "1.10" comes after "1.2".
* The Delphix Engine will never allow installation of plugin with a build number that is ordered before the the already-installed build number.

Please also see the [App-Style vs. Enterprise-Style section](#app-style-vs-enterprise-style) below. We generally recommend using a single integer build number for app-style development. Build numbers need to have multiple parts if you are doing enterprise-style development.

### (post-beta) Plugin Metadata

TODO: What is plugin metadata? How may it be used? What are the rules and best practices?

## Versioning Strategies
### App-Style vs. Enterprise-Style

There are two main strategies for releasing software:

* You can use an "app-style" release strategy. Here, all users are expected to use the latest available version of the software. Most consumer software works this way today -- websites, phone apps, etc.
* You can use an "enterprise-style" release strategy. Here, you might distinguish "major" releases of your software from "minor" releases. You might expect some customers to continue to use older major releases for a long time, even after a new major release comes out. This strategy is often used for software like operating systems and DBMSs, where upgrading can cause significant disruption.

An app-style strategy is much simpler, but also more limiting:

* At any time, there is only one branch under active development.
* Customers that want bugfixes must update to the latest version.
* The plugin's build number can be a simple integer that is incremented with each new release.

An enterprise-style strategy is more flexible, but also more cumbersome:

* There may be multiple branches under active development at any time. Typically one branch for every "major release" that is still being supported. This requires careful coordination to make sure that each new code change ends up on the correct branch (or branches).
* It is possible to supply bugfix-only minor releases (often called "backport releases") which build atop older major releases. Customers do not need to move to the new major version in order to get these bugfixes.
* The plugin's build number needs to be composed of multiple integers.
* The plugin may need to implement special logic to prevent certain incompatible upgrades. More details [here](/Versioning_And_Upgrading/Compatibility/#plugin-defined-compatibility)

You may use whichever of these strategies works best for you. The SDK and the Delphix Engine support either strategy. You can even change your mind later and switch to the other strategy.
