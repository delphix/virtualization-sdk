# Managing Scripts for Remote Execution

To execute a PowerShell or Bash script or Expect script on a remote host, you must provide the script as a string to `run_powershell` or `run_bash` or `run_expect`. While you can keep these strings as literals in your Python code, best practice is to keep them as resource files in your source directory and access them with `pkgutil`.

[pkgutil](https://docs.python.org/2/library/pkgutil.html) is part of the standard Python library. The method that is applicable to resources is [pkgutil.get_data](https://docs.python.org/2/library/pkgutil.html#pkgutil.get_data).

### Basic Usage

Given the following plugin structure:

```
├── plugin_config.yml
├── schema.json
└── src
    ├── plugin_runner.py
    └── resources
        ├── __init__.py
        └── get_date.sh
```

Assume `SnapshotDefinition` is:

```
"snapshotDefinition": {
    "type" : "object",
    "additionalProperties" : false,
    "properties" : {
        "name": {"type": "string"},
        "date": {"type": "string"}
    }
}
```

and `src/resources/get_date.sh` contains:

```
#!/usr/bin/env bash
date
```


If `get_date.sh` is needed in `post_snapshot`, it can be retrieved and executed:

```python
import pkgutil

from dlpx.virtualization import libs
from dlpx.virtualization.platform import Plugin

from generated.definitions import SnapshotDefinition


plugin = Plugin()

@plugin.linked.post_snapshot()
def post_snapshot(direct_source, repository, source_config):
	# Retrieve script contents
	script_content = pkgutil.get_data('resources', 'get_date.sh')

	# Execute script on remote host
	response = libs.run_bash(direct_source.connection, script_content)

	# Fail operation if the timestamp couldn't be retrieved
	if response.exit_code != 0:
		raise RuntimeError('Failed to get date: {}'.format(response.stdout))

	return SnapshotDefinition(name='Snapshot', date=response.stdout)
```

!!! note "Python's Working Directory"
	This assumes that `src/` is Python's current working directory. This is the behavior of the Virtualization Platform.

!!! warning "Resources need to be in a Python module"
	`pkgutil.get_data` cannot retrieve the contents of a resource that is not in a Python package. This means that a resource that is in the first level of your source directory will not be retrievable with `pkgutil`. Resources must be in a subdirectory of your source directory, and that subdirectory must contain an `__init__.py` file.

### Multi-level Packages

Given the following plugin structure:

```
├── plugin_config.yml
├── schema.json
└── src
    ├── plugin_runner.py
    └── resources
        ├── __init__.py
        ├── database
        │   ├── __init__.py
        │   └── execute_sql.sh
        └── platform
            ├── __init__.py
            └── get_date.sh
```

The contents of `src/resources/platform/get_date.sh` can be retrieved with:

```python
script_content = pkgutil.get_data('resources.platform', 'get_date.sh')
```
