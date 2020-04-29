# Managing Versions With Replication

In order to ensure incompatible plugin versions on the source and target do not cause issues with provisioning and failover, plugin authors can use the below recommendations.

- Make sure to build your plugin with the newest Virtualization SDK version available.
- Make sure there is only one artifact built for a given official version of the plugin.
- Make sure the official release of a plugin does not use the same build number as a development build.
- Make sure to use a versionining scheme (the external version defined in the plugin configuration) that helps easily identify which plugin is older or newer than the plugin already installed on the Delphix Engine.
- Make sure to publish or maintain a plugin version compatibility matrix which lists out the plugin version, Virtualization SDK it was built with and the Delphix Engine version (or versions) it is compatible with.
