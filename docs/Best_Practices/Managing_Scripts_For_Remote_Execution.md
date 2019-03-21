# Managing Scripts for Remote Execution

To execute a PowerShell or Bash script on a remote host, you must provide a the script as a string to `run_powershell` or `run_bash`. While you can keep these strings as literals in your Python code, it's best practice to keep them as resource files in your source directory and access them with `pkgutil`.

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


The contents of `src/resources/get_date.sh` can be retrieved with:

```python
script_content = pkgutil.get_data('resources', 'get_date.sh')
```

!!! note "NOTE"
	This assumes that `src/` is Python's current working directory. This is the behavior of the Virtualization Platform.
	
!!! note "NOTE"
	`pkgutil.get_data` cannot retrieve the contents of a resource that is not in a Python module. This means that a resource that is in the first level of your source directory will not be retrievable with `pkgutil`. Resources must be in a subdirectory of your source direcotry and that subdirectory must contain an `__init__.py` file. 
	
### Mutli-level Packages

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

The contents of `src/resources/platform/get_data.sh` can be retrieved with:

```python
script_content = pkgutil.get_data('resources.platform', 'get_date.sh')
```