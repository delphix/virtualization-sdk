# Versioning

Almost all software products are periodically updated to include new features and bug fixes. Plugins are no exception -- a plugin's code will very likely be different two years from now.

To deal with this, plugins use **versioning**. This just means that a plugin communicates (to the user, and to the Delphix Engine) exactly what code is in use.

## Versioning Information

There are three different pieces of version-related information, each used for different purposes.

### External Version

This field is intended only for use by the end user. The Delphix Engine does not use this field, and therefore imposes no restrictions on its content. This is a free-form string which the plugin can use in any way it feels like.

Examples might be "5.3.0", "2012B", "MyPlugin Millennium Edition, Service Pack 3", "Playful Platypus" or "Salton City".

The external version is specified using the `externalVersion` property in your [plugin config](/References/Plugin_Config.md) file.

!!! tip
    Use an external version that makes it easier for end users to determine newer vs older plugins.

### Build Number

Unlike "external version", this field is intended to convey information to the Delphix Engine. This is a string of integers, separated by periods. Examples would be "5.3.0", "7", "5.3.0.0.0.157".

The Delphix Engine uses the build number to guard against end users trying to "downgrade" their plugin to an older, incompatible version. So, if a user has build number "3.4.1" installed, then they may not install a version with a build number like "2.x.y", "3.3.y" or "3.4.0".

The build number is specified using the `buildNumber` property in your [plugin config](/References/Plugin_Config.md) file.

This field is required to be a string. You might need to enclose your build number in quotes in order to prevent YAML from interpreting the field as a number. Examples:

`buildNumber` | Allowed | Details
-------- | ---- | -----------
1 | No |  YAML will interpret this as an integer.
1.2 | No | YAML will interpret this as a floating-point number.
"1" | Yes | The quotes mean this is a string.
"1.2" | Yes | The quotes mean this is a string.
1.2.3 | Yes | YAML treats this as a string, since it cannot be a number.

#### Build Number Format Rules

Your build number must be a string, conforming to these rules:

* The string must be composed of a sequence of non-negative integers, not all zero, separated by periods.
* Trailing zeros are ignored. So, "1.0.0" is treated the same as "1".
* Build numbers are sortable numerically, with earlier numbers having more significance than later numbers. So, "2.0" comes after "1.99999", and "1.10" comes after "1.2".
* The Delphix Engine will never allow installation of plugin with a build number that is ordered before the the already-installed build number.

!!! tip
    You can upload a plugin with the same `buildNumber` as the installed plugin. However this should only be done while a plugin is being developed. Plugin releases for end users should never have the same `buildNumber`

Please also see the [App-Style vs. Enterprise-Style section](#app-style-vs-enterprise-style) below. We generally recommend using a single integer build number for app-style development. Build numbers need to have multiple parts if you are doing enterprise-style development.

## Release Strategies

There are two main strategies for releasing software:

#### "App-style" Release Strategy
Here, all users are expected to use the latest available version of the software. Most consumer software works this way today -- websites, phone apps, etc. An app-style strategy is much simpler, but also more limiting:

* At any time, there is only one branch under active development.
* Customers that want bugfixes must upgrade to the latest version.
* The plugin's build number can be a simple integer that is incremented with each new release.

### "Enterprise-style" Release Strategy
Here, you might distinguish "major" releases of your software from "minor" releases. You might expect some customers to continue to use older major releases for a long time, even after a new major release comes out. This strategy is often used for software like operating systems and DBMSs, where upgrading can cause significant disruption. An enterprise-style strategy is more flexible, but also more cumbersome:

* There may be multiple branches under active development at any time. Typically one branch for every "major release" that is still being supported. This requires careful coordination to make sure that each new code change ends up on the correct branch (or branches).
* It is possible to supply bugfix-only minor releases (often called "patch releases") which build atop older major releases. Customers do not need to move to the new major version in order to get these bugfixes.
* The plugin's build number needs to be composed of multiple integers.

If you are using this strategy read more [here](#Backports_And_Hotfixes.md) about how to deal with backports and hotfixes.

You may use whichever of these strategies works best for you. The SDK and the Delphix Engine support either strategy. You can even change your mind later and switch to the other strategy.

## Recommendations

* Build your plugin with the newest Virtualization SDK version available.
* Only publish one artifact built for a given official version of the plugin.
* The official release of a plugin should not use the same build number as a development build.
* Use an [external version](#external-version) that helps easily identify newer plugins.
* Publish a plugin version compatibility matrix which lists out the plugin version, the Virtualization SDK it was built with and the Delphix Engine version(s) it supports.
