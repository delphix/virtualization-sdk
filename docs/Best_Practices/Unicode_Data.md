# Working with Unicode Data

To use unicode characters in the plugin code, the following lines should be included at top of the plugin code:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
```

Otherwise, there may be errors when building the plugin using [dvp build](/References/CLI.md#build) or during the execution of a plugin operation.

## Example

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dlpx.virtualization.platform import Plugin
from dlpx.virtualization import libs
from generated.definitions import RepositoryDefinition

plugin = Plugin()

@plugin.discovery.repository()
def repository_discovery(source_connection):
    # Create a repository with name ☃
    command = 'echo ☃'
    result = libs.run_bash(source_connection, command)
    return [RepositoryDefinition(name=result.stdout)]
```    