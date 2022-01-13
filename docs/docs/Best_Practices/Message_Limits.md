# Message Limits

There are limits on how much data can be sent back and forth between the plugin and engine at a time. There are five scenarios where this comes into play:

1. Inputs sent from the engine to the plugin, as arguments to a [Plugin Operation](/References/Plugin_Operations.md). For example, the schema-defined `Repository` object that is provided as input to plugin operations.

2. Outputs sent back from the plugin to the engine, as the return values from plugin operations.

3. Exception messages and call stacks thrown by plugin code. For example, the `message` field within [User Visible Errors](/Best_Practices/User_Visible_Errors.md).

4. Inputs sent from the plugin to the engine, as arguments to a [Platform library](/References/Platform_Libraries.md) function. For example, the `message` field that is passed to `logger.debug`.

5. Outputs sent back from the engine to the plugin, as the return values from Platform Library functions. For example, the `stdout` resulting from a call to `libs.run_bash`.

For case 1 and 2, the total size of data must be less than 4 mebibytes (4 MiB).

For case 3, the total size of data must be less than 128 kibibytes (128 KiB).

For case 4 and 5, the total size of data must be less than 192 mebibytes (192 MiB).

The actual size of this information at runtime is dependent on how the Python interpreter chooses to represent the information, so it's not always possible to know ahead of time what the exact size will be.

Here are some examples of where problems may occur:

1. Using `libs.run_bash` to print the entire contents of a large file to stdout.

2. Using a single `logger` command with many pages of output.

3. Throwing an exception with a large message or stack trace.

4. Large amount of metadata in a plugin defined schema like `Repository` or `Virtual Source`.

## How to tell if the message size was exceeded

The plugin operation or platform library callback will fail with a RPC error. The exception will look like:

```
Error
Discovery of "my_plugin" failed: Plugin operation "Repository Discovery" got a RPC error for plugin "my_plugin". UNAVAILABLE: Network closed for unknown reason
```

## What to do if the maximum metadata or message size is exceeded

Reach out to us via the [Virtualization SDK GitHub repository](https://github.com/delphix/virtualization-sdk/) for guidance.
