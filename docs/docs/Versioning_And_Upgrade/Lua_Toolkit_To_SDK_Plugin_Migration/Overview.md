# Overview

Before the Virtualization SDK was written, Delphix use to support toolkits written only in Lua. The toolkit was written, built, and uploaded to the Delphix engine using scripts with little documentation. Multiple toolkits were released and are still used by customers today, so as we move towards only supporting SDK Plugins, there must be a way to get customers off of lua toolkits and onto SDK plugins.

If you are reading this and have no idea what a lua toolkit is, there is no reason to read further into this section. Everything written in these pages will assume the goal is to write specific code as part of a plugin to be able to upgrade objects that were created using old toolkits into objects in the Delphix Engine pointing to a plugin. 

Reading the next few pages we also make the assuption that you've written both a lua toolkit and a python plugin before and know some of the terminology already established. If this is not true, please try [building a plugin](/Building_Your_First_Plugin/Overview.md) and [writing some upgrade migrations](/Versioning_And_Upgrade/Upgrade.md) first before coming back here to learn how to add upgrading from lua toolkits into the mix.

## Basic no-schema Migration
One way to migrate from a lua toolkit to a plugin is to write an exactly equivalent plugin that does not make any [schema](/References/Schemas.md) changes to the objects that were defined originally in the lua toolkit. If this is the scenario you are in, then you only need to update the [plugin config](Plugin_Config.md) with a couple new lua migration specific fields.


## Migration with schema changes
The other way to migrate from a lua toolkit to a plugin is to wait and write a python plugin only once you have new features you want to release. These new features may include schema changes to any of the object. In this case you will need to update both the [plugin config](Plugin_Config.md) and write new [lua upgrade operations](Plugin_Operations.md) for each of the objects that needs to be modified during the upgrade.

## Supporting migrations with older versions of lua
Having the ability to define lua upgrade operations in the new plugin code means that older lua version migration scripts can be [converted](Converting_Migration_Scripts.md), enabling multi-step upgrades from older lua versions to migrate and become plugins. 