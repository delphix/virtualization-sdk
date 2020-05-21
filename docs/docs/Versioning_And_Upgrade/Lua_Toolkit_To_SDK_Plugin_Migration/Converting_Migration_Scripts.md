# Converting Migration Scripts
To convert migrations that were originally written in lua we need to determine which from version the migration is from, which object type the migration is written for, and lastely convert the code into python code using the [decorators](Decorators.md) described previously.

## Example
Assume there are two versions of a lua toolkit, 1.0.0 and 1.1.0 where the 1.1.0 version is following the basic toolkit directory structure (actually containing all operations):

```
├── main.json
├── discovery 
│   ├── repositoryDiscovery.lua
│   └── sourceConfigDiscovery.lua
├── staged 
│   ├── mountSpec.lua
│   ├── ...
│   └── worker.lua
├── virtual 
│   ├── configure.lua
│   ├── ...
│   └── unconfigure.lua
├── upgrade 
│   └── 1.0
│       ├── upgradeLinkedSource.lua
│       ├── ...
│       └── upgradeVirtualSource.lua
├── resources 
└── ├── log.sh
    ├── ...
    └── stop.sh
```

`upgradeLinkedSource.lua` contains:

```lua
parameters.dsOldValue = "remove"
parameters.dsUpdateValue = 1
parameters.dsLanguage = "LUA"
return parameters
```

This can be equalivalently converted into the python code:

```python
from dlpx.virtualization.platform import Plugin

plugin = Plugin()

@plugin.upgrade.linked_source("1.0", MigrationType.LUA)
def upgrade_linked_source(old_linked_source):
  new_linked_source = dict(old_linked_source)
  new_linked_source["dsOldValue"] = "remove"
  new_linked_source["dsUpdateValue"] = 1
  new_linked_source["dsLanguage"] = "LUA"
  return new_linked_source
```

You will need to determine how far back in the lua upgrade chain you want to support multi-step upgrade from, and convert all of them accordingly. Remember that the execution of these scripts rely on there not being any missing migrations, and will be executed from the lowest version that exists to the highest version.
