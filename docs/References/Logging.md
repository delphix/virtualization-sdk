# Logging

## What is logging?

The Delphix Engine keeps plugin-specific log files. A plugin can, at any point in any of its [operations](Glossary.md#plugin-operation), write out some text to its log file(s). These log files can be examined later, typically to try to debug a problem with the plugin.

## How to log

The Delphix engine provides [callbacks](Glossary.md#callback) that plugins can use to write to log files.

Making a log entry is easy, and looks like this:
```python
from dlpx.virtualization import libs

libs.log_debug("Here is the text that goes in the log file")
```

Inside the log file, you'll be able to see not only your text, but also a timestamp.


## Why log?

Logging is typically done to enable your plugin to be more easily debugged.

### Example
Imagine you notice that your plugin is taking a very long time to do discovery. Everything works, it just takes much longer than expected. You'd like to figure out why.

Suppose your plugin has a discovery operation that looks like this (code is abbreviated to be easier to follow):
```python
def my_operation(resources):
  version_result = libs.run_bash(command=resources["get_db_version"])
  users_result = libs.run_bash(command=resources["get_db_users"])
  db_results = libs.run_bash(command=resources["get_databases"])
  status_result = libs.run_bash(command=resources["get_database_statuses"])
  # Later, do something will all these results
```

Now, imagine that you notice that it's taking a long time to do discovery, and you'd like to try to figure out why. One thing that might help is to add logging, like this:
```python
def my_operation(resources):
  libs.log_debug("About to get DB version")
  version_result = dlpx.run_bash(command=resources["get_db_version"])
  libs.log_debug("About to get DB users")
  users_result = dlpx.run_bash(command=resources["get_db_users"])
  libs.log_debug("About to get databases")
  db_results = libs.run_bash(command=resources["get_databases"])
  libs.log_debug("About to get DB statuses")
  status_result = dlpx.run_bash(command=resources["get_database_statuses"])
  libs.log_debug("Done collecting data")
```

When you look at the log file, perhaps you'll see something like this:

**TODO: Convert this to actual format used in our log files**

```
2019-03-01T09:22:17|About to get DB version
2019-03-01T09:22:19|About to get DB users
2019-03-01T09:35:41|About to get databases
2019-03-01T09:35:44|About to get DB statuses
2019-03-01T09:35:49|Done collecting data
```

You can see that it only takes a few seconds for us do each of our data collection steps, with the exception of getting the users, which takes over 13 minutes!

We now know that our slowdown is something to do with how our bash script is collecting all the users. Logging has gotten us a lot closer to figuring out the problem.

## How to retrieve logs

**TODO: Add content here after we have a firm process for doing this (there may be a UI coming soon?)**

## Logging Levels

We already looked at an example of the `log_debug` callback. There are two more: `log_info` and `log_error`. Both work exactly the same way.

Each of these three logging levels has its own log file. Thus, calling `log_error` will write to an `error.log` file.

These levels are also hierarchical:
`log_error` writes only to `error.log`.
`log_info` writes to `info.log` and `error.log`.
`log_debug` writes to `debug.log`, `info.log`, and `error.log`.

`log_error` is meant to be used for cases where you know for sure there is a problem. The distinction between what counts as "info" and what counts as "debug" is entirely up to you. Some plugins will pick one of them and use it exclusively. Some will decide to count only the most important messages as "info", with everything else counting as "debug".

## Sensitive data

Remember that logging data means writing that data out in cleartext. Make sure you never log any data that could be secret or sensitive (passwords, etc.). For more details please see our section on [sensitive data](/Best_Practices/Sensitive_Data.md)
