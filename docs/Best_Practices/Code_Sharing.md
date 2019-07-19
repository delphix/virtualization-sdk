# Code Sharing

All Python modules inside of `srcDir` can be imported just as they would be if the plugin was executing locally. When a plugin operation is executed `srcDir` is the current working directory so all imports need to be relative to `srcDir` regardless of the path of the module doing the import.

Please refer to Python's [documentation on modules](https://docs.python.org/2/tutorial/modules.html#modules) to learn more about modules and imports.

## Example

Assume we have the following file structure:

```
postgres
├── plugin_config.yml
├── schema.json
└── src
    ├── operations
    │   ├── __init__.py
    │   └── discovery.py
    ├── plugin_runner.py
    ├── resources
    │   ├── __init__.py
    │   ├── execute_sql.sh
    │   ├── list_installs.sh
    │   └── list_schemas.sql
    └── utils
        ├── __init__.py
        └── execution_util.py
```

Any module in the plugin could import `execution_util.py` with `from utils import execution_util`.

!!! warning "Gotcha"
	Since the platform uses Python 2.7, every directory needs to have an `__init__.py` file in it otherwise the modules and resources in the folder will not be found at runtime. For more information on `__init__.py` files refer to Python's [documentation on packages](https://docs.python.org/2/tutorial/modules.html#packages).
	
	Note that the `srcDir` in the plugin config file (`src` in this example) does _not_ need an `__init__.py` file.

Assume `schema.json` contains:

```
{
    "repositoryDefinition": {
        "type": "object",
        "properties": {
            "name": { "type": "string" }
        },
        "nameField": "name",
        "identityFields": ["name"]
    },
    "sourceConfigDefinition": {
        "type": "object",
        "required": ["name"],
        "additionalProperties": false,
        "properties": {
            "name": { "type": "string" }
        },
        "nameField": "name",
        "identityFields": ["name"]
    }
}
```

To keep the code cleaner, this plugin does two things:

1. Splits discovery logic into its own module: `discovery.py`.
2. Uses two helper funtions `execute_sql` and `execute_shell` in `utils/execution_util.py` to abstract all remote execution.

### plugin_runner.py

When the platform needs to execute a plugin operation, it always calls into the function decorated by the `entryPoint` object. The rest of the control flow is determined by the plugin. In order to split logic, the decorated function must delegate into the appropriate module. Below is an example of `plugin_runner.py` delegating into `discovery.py` to handle repository and source config discovery:

```python
from operations import discovery

from dlpx.virtualization.platform import Plugin


plugin = Plugin()


@plugin.discovery.repository()
def repository_discovery(source_connection):
    return discovery.find_installs(source_connection);


@plugin.discovery.source_config()
def source_config_discovery(source_connection, repository):
    return discovery.find_schemas(source_connection, repository)


```
!!! note
	`discovery.py` is in the `operations` package so it is imported with `from operations import discovery`.

### discovery.py
In `discovery.py` the plugin delegates even further to split business logic away from remote execution. `utils/execution_util.py` deals with remote execution and error handling so `discovery.py` can focus on business logic. Note that `discovery.py` still needs to know the format of the return value from each script.

```python
from dlpx.virtualization import libs

from generated.definitions import RepositoryDefinition, SourceConfigDefinition
from utils import execution_util


def find_installs(source_connection):
    installs = execution_util.execute_shell(source_connection, 'list_installs.sh')

    # Assume 'installs' is a comma separated list of the names of Postgres installations.
    install_names = installs.split(',')
    return [RepositoryDefinition(name=name) for name in install_names]


def find_schemas(source_connection, repository):
    schemas = execution_util.execute_sql(source_connection, repository.name, 'list_schemas.sql')

    # Assume 'schemas' is a comma separated list of the schema names.
    schema_names = schemas.split(',')
    return [SourceConfigDefinition(name=name) for name in schema_names]
```
!!! note
	Even though `discovery.py` is in the `operations` package, the import for `execution_util` is still relative to the `srcDir` specified in the plugin config file. `execution_util` is in the `utils` package so it is imported with `from utils import execution_util`. 
	
### execution_util.py

`execution_util.py ` has two methods `execute_sql` and `execute_shell`. `execute_sql` takes the name of a SQL script in `resources/` and executes it with `resources/execute_sql.sh`. `execute_shell` takes the name of a shell script in `resources/` and executes it.

```python
import pkgutil

from dlpx.virtualization import libs


def execute_sql(source_connection, install_name, script_name):
    psql_script = pkgutil.get_data("resources", "execute_sql.sh")
    sql_script = pkgutil.get_data("resources", script_name)

    result = libs.run_bash(
        source_connection, psql_script, variables={"SCRIPT": sql_script}, check=True
    )
    return result.stdout


def execute_shell(source_connection, script_name):
    script = pkgutil.get_data("resources", script_name)

    result = libs.run_bash(source_connection, script, check=True)
    return result.stdout
```

!!! note
	Both `execute_sql` and `execute_shell` use the `check` parameter which will cause an error to be raised if the exit code is non-zero. For more information refer to the `run_bash` [documentation](/References/Platform_Libraries.md#run_bash).