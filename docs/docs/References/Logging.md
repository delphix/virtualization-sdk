# Logging

## What is logging?

The Virtualization Platform keeps plugin-specific log files. A plugin can, at any point in any of its [plugin operations](Glossary.md#plugin-operation), write out some text to its log file(s). These log files can be examined later, typically to try to debug a problem with the plugin.

## Overview

The Virtualization Platform integrates with Python's built-in [logging framework](https://docs.python.org/2/library/logging.html). A special [Handler](https://docs.python.org/2/library/logging.html#handler-objects) is exposed by the platform at `dlpx.virtualization.libs.PlatformHandler`. This handler needs to be added to the Python logger your plugin creates. Logging statements made through Python's logging framework will then be routed to the platform.

## Basic Setup
 Below is the absolute minimum needed to setup logging for the platform. Please refer to Python's [logging documentation](https://docs.python.org/2/library/logging.html) and the [example below](#customized-example) to better understand how it can be customized.

```python
import logging

from dlpx.virtualization.libs import PlatformHandler

# Get the root logger.
logger = logging.getLogger()
logger.addHandler(PlatformHandler())

# The root logger's default level is logging.WARNING.
# Without the line below, logging statements of levels
# lower than logging.WARNING will be suppressed.
logger.setLevel(logging.DEBUG)
```

!!! note "Logging Setup"
	Python's logging framework is global. Setup only needs to happen once, but where it happens is important. Any logging statements that occur before the `PlatformHandler` is added will not be logged by the platform.
	
	It is highly recommended that the logging setup is done in the plugin's entry point module before any operations are ran.
	
!!! warning "Add the PlatformHandler to the root logger"
	Loggers in Python have a hierarchy and all loggers are children of a special logger called the "root logger". Logging hierarchy is not always intuitive and depends on how modules are structured.
	
	To avoid this complexity, add the `PlatformHandler` to the root logger. The root logger can be retrieved with `logging.getLogger()`.
	
	
## Usage
Once the `PlatformHandler` has been added to the logger, logging is done with Python's [Logger](https://docs.python.org/2/library/logging.html#logger-objects) object. Below is a simple example including the basic setup code used above:

```python
import logging

from dlpx.virtualization.libs import PlatformHandler

logger = logging.getLogger()
logger.addHandler(PlatformHandler())

# The root logger's default level is logging.WARNING.
# Without the line below, logging statements of levels
# lower than logging.WARNING will be suppressed.
logger.setLevel(logging.DEBUG)

logger.debug('debug')
logger.info('info')
logger.error('error')
```

### Example
Imagine you notice that your plugin is taking a very long time to do discovery. Everything works, it just takes much longer than expected. You'd like to figure out why.

!!! info
    Refer to [Managing Scripts for Remote Execution](/Best_Practices/Managing_Scripts_For_Remote_Execution.md) for how remote scripts can be stored and retrieved.

Suppose your plugin has a source config discovery operation that looks like this (code is abbreviated to be easier to follow):
```python
import pkgutil

from dlpx.virtualization import libs
from dlpx.virtualization.platform import Plugin


plugin = Plugin()

@plugin.discovery.repository()
def repository_discovery(source_connection): 
  return [RepositoryDefinition('Logging Example')]


@plugin.discovery.source_config()
def source_config_discovery(source_connection, repository):
  version_result = libs.run_bash(source_connection, pkgutil.get_data('resources', 'get_db_version.sh'))
  users_result = libs.run_bash(source_connection, pkgutil.get_data('resources', 'get_db_users.sh'))
  db_results = libs.run_bash(source_connection, pkgutil.get_data('resources', 'get_databases.sh'))
  status_result = libs.run_bash(source_connection, pkgutil.get_data('resources', 'get_database_statuses.sh'))

  # Return an empty list for simplicity. In reality
  # something would be done with the results above.
  return []
 
```

Now, imagine that you notice that it's taking a long time to do discovery, and you'd like to try to figure out why. One thing that might help is to add logging, like this:
```python
import logging
import pkgutil

from dlpx.virtualization import libs
from dlpx.virtualization.platform import Plugin

from generated.definitions import RepositoryDefinition

# This should probably be defined in its own module outside
# of the plugin's entry point file. It is here for simplicity.
def _setup_logger():
	# This will log the time, level, filename, line number, and log message.
    log_message_format = '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s'
	log_message_date_format = '%Y-%m-%d %H:%M:%S'

	# Create a custom formatter. This will help with diagnosability.
	formatter = logging.Formatter(log_message_format, datefmt= log_message_date_format)

	platform_handler = libs.PlatformHandler()
	platform_handler.setFormatter(formatter)

	logger = logging.getLogger()
	logger.addHandler(platform_handler)

	# By default the root logger's level is logging.WARNING.
	logger.setLevel(logging.DEBUG)


# Setup the logger.
_setup_logger()

# logging.getLogger(__name__) is the convention way to get a logger in Python.
# It returns a new logger per module and will be a child of the root logger.
# Since we setup the root logger, nothing else needs to be done to set this
# one up.
logger = logging.getLogger(__name__)


plugin = Plugin()

@plugin.discovery.repository()
def repository_discovery(source_connection): 
  return [RepositoryDefinition('Logging Example')]

@plugin.discovery.source_config()
def source_config_discovery(source_connection, repository):
  logger.debug('About to get DB version')
  version_result = libs.run_bash(source_connection, pkgutil.get_data('resources', 'get_db_version.sh'))
  logger.debug('About to get DB users')
  users_result = libs.run_bash(source_connection, pkgutil.get_data('resources', 'get_db_users.sh'))
  logger.debug('About to get databases')
  db_results = libs.run_bash(source_connection, pkgutil.get_data('resources', 'get_databases.sh'))
  logger.debug('About to get DB statuses')
  status_result = libs.run_bash(source_connection, pkgutil.get_data('resources', 'get_database_statuses.sh'))
  logger.debug('Done collecting data')
  
  # Return an empty list for simplicity. In reality
  # something would be done with the results above.
  return []
```

When you look at the log file, perhaps you'll see something like this:

```
[Worker-360|JOB-315|ENVIRONMENT_DISCOVER(UNIX_HOST_ENVIRONMENT-5)] [2019-04-30 12:10:42] [DEBUG] [python_runner.py:44] About to get DB version
[Worker-360|JOB-316|DB_SYNC(APPDATA_CONTAINER-21)] [2019-04-30 12:19:35] [DEBUG] [python_runner.py:49] About to get DB users
[Worker-325|JOB-280|ENVIRONMENT_REFRESH(UNIX_HOST_ENVIRONMENT-5)] [DEBUG] [plugin_runner.py:51] About to get databases
[Worker-326|JOB-281|SOURCES_DISABLE(UNIX_HOST_ENVIRONMENT-5)] [DEBUG] [plugin_runner.py:53] About to get DB statuses
```

You can see that it only takes a few seconds for us do each of our data collection steps, with the exception of getting the users, which takes over 13 minutes!

We now know that our slowdown is something to do with how our bash script is collecting all the users. Logging has gotten us a lot closer to figuring out the problem.

## How to retrieve logs

Download a support bundle by going to **Help** > **Support Logs**  and select **Download**. The logs will be in a the support bundle under `log/mgmt_log/plugin_log/<plugin name>`.

## Logging Levels

Python has a number of [preset logging levels](https://docs.python.org/2/library/logging.html#logging-levels) and allows for custom ones as well. Since logging on the Virtualization Platform uses the `logging` framework, log statements of all levels are supported.

However, the Virtualization Platform will map all logging levels into three files: `debug.log`, `info.log`, and `error.log` in the following way:

|Python Logging Level|Logging File|
|:------------------:|:-----------:|
|DEBUG| debug.log|
|INFO| info.log|
|WARN| error.log|
|WARNING| error.log|
|ERROR| error.log|
|CRITICAL| error.log|

As is the case with the `logging` framework, logging statements are hierarchical: logging statements made at the `logging.DEBUG` level will be written only to `debug.log` while logging statements made at the `logging.ERROR` level will be written to `debug.log`, `info.log`, and `error.log`.

## Sensitive data

Remember that logging data means writing that data out in cleartext. Make sure you never log any data that could be secret or sensitive (passwords, etc.). For more details please see our section on [sensitive data](/Best_Practices/Sensitive_Data.md)
