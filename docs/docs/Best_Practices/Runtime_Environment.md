# Plugin Runtime Environment

## Process Lifetime
Plugin code runs inside of a Python interpreter process on the Delphix Engine.

A fair question to ask is "What is the lifetime of this interpreter process?"  After all, if the interpreter
process runs for a long time, then the plugin might be able to store things in memory for later access.

Unfortunately, **there are no guarantees about process lifetime**. Your interpreter process could last two years, or it could last 400 microseconds. There is no way to know or predict this ahead of time.

So, do not make any assumptions about interpreter process lifetime in your plugin code.


## Available Modules
Our Python 2.7 runtime environment only contains the [Python Standard Library](https://docs.python.org/2/library/). No additional Python modules/libraries are available.

If you want to use some Python module that is not part of the standard library, you might be able to do so.
You would need to include that library as part of your plugin. That would involve downloading the source
code for that module, and copying it into your source directory. For more information on how to lay out code in your source directory, see [Code Sharing](/Best_Practices/Code_Sharing.md).

### Warnings
There are two major things to watch out for if you decide to incorporate a 3rd-party library.

1) Make sure you're legally allowed to do so! The licensing agreement on the module will decide if, and
under what circumstances, you're allowed to make copies of, and redistribute the module. Some modules will
allow this, some will disallow this, and some will allow this for a fee.

2) Some Python libraries include native code (often written in C or C++). There is no support for using
such libraries with plugin code.  The reason for this is that native code needs to be
specially compiled and built for the machine that it the library will be running on. And, unfortunately,
the machine your plugin runs on (the Delphix Engine) is likely very different from the machine you use
to develop and build your plugin.

## Network Access
As of Delphix Engine version 6.0.11.0, plugin code is able to use the network directly. No network access is
possible in earlier versions.

For example, suppose your plugin wants to talk to some DBMS running on some remote host.
If the DBMS supports it, your plugin code might be able to connect to the DBMS server and talk to the
DBMS directly. This can avoid the need to do DBMS operations via running Bash/Powershell code on the remote host.


### Example
```python
import httplib
import json

dbms_port = 5432

# Directly contact our DBMS's REST server to get a list of databases
def list_databases(remote_ip):
    cx = httplib.HTTPConnection(remote_ip, dbms_port)
    cx.request("GET", "/databases")
    response = cx.getresponse()
    return json.loads(response.read())
```

What your plugin can access depends entirely on the customer. Some customers will set up their Delphix
Engines such that plugins have full access to the entire internet. Some will completely restrict the network
so that the plugin can only access a small handful of remote hosts.

If your plugin has any specific network requirements, it's recommended to try, in your code, to confirm that these requirements are met. For example, the plugin could make such a check in the
`discovery.repository()` operation, and throw an error if the check fails. Like any other requirement, this should of course be documented.
