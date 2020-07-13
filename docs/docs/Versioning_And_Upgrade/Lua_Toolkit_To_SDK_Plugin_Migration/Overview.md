# Overview

Before the Virtualization SDK was written, Delphix only supported [toolkits](/References/Glossary.md#lua-toolkit) written in Lua. There was only limited documentation to help people write, build, and upload toolkits. Multiple toolkits were released and are still used by customers today, so as we move towards only supporting SDK Plugins, there needs to be a way to get customers off of Lua toolkits and onto SDK plugins.

If you are reading this and have no idea what a Lua toolkit is, there is no reason to read further into this section. Everything written in these pages will assume the goal is to write specific code as part of a plugin to convert objects created using Lua toolkits to use the newly uploaded Python plugin.

In the next few pages, we also make the assumption that you've written both a Lua toolkit and a Python plugin before and know some of the terminology already established. If this is not true, please try [building a plugin](/Building_Your_First_Plugin/Overview.md) and [writing some upgrade migrations](/Versioning_And_Upgrade/Upgrade.md) first before coming back here to learn how to add upgrading from Lua toolkits into the mix as described below.

## Basic no-schema Migration
One way to migrate from a Lua toolkit to a plugin is to write an exactly equivalent plugin that does not make any [schema](/References/Schemas.md) changes to the objects that were defined originally in the Lua toolkit. If this is the scenario you are in, then you only need to update the [plugin config](Plugin_Config.md) with a couple of new Lua migration specific fields.


## Migration with schema changes
The other way to migrate from a Lua toolkit to a plugin is to wait and write a python plugin only once you have new features you want to release. These new features may include schema changes to any of the objects. In this case you will need to update both the [plugin config](Plugin_Config.md) and write new [Lua upgrade operations](Plugin_Operations.md) for each of the objects that needs to be modified during the upgrade.

## Supporting migrations with older versions of Lua
Having the ability to define Lua upgrade operations in the new plugin code means that older Lua version migration scripts can be [converted](Converting_Migration_Scripts.md), enabling multi-step upgrades from older Lua versions to migrate and become plugins.

!!! warning "New versions of a Lua toolkit is strongly discouraged after Python Plugin is written"
	After having written a Plugin to migrate a specific Lua toolkit, while possible, you should avoid writing new major/minor versions of the toolkit in Lua. Patch releases with no schema changes can still be done. If you need to write a new Lua toolkit version please contact the Delphix Virtualization SDK Engineering team to get help on updating migrations accordingly.
