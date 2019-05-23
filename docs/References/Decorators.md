---
title: Virtualization SDK
---

# Decorators

The Virtualization SDK exposes decorators to be able to annotate functions that correspond to each [Plugin Operation](Plugin_Operations.md).
In the example below, it first instantiates a `Plugin()` object, that can then be used to tag plugin operations.


```python
from dlpx.virtualization.platform import Plugin

# Initialize a plugin object
plugin = Plugin()

# Use the decorator to annotate the function that corresponds to the "Virtual Source Start" Plugin Operation
@plugin.virtual_source.start()
def my_start(virtual_source, repository, source_config):
  print "running start" 
```

!!! info
    Decorators exposed by the Virtualization SDK are inherently python function calls and needs parentheses `()` appended at the end.

Assuming the name of the object, is `plugin` as above, the table below lists the corresponding decorators for each plugin operation.

Plugin Operation | Decorator
---------------- |  --------
[Repository Discovey](Plugin_Operations.md#repository-discovery) | `@plugin.discovery.repository()`
[Source Config Discovey](Plugin_Operations.md#source-config-discovery) | `@plugin.discovery.source_config()`
[Direct Linked Source Pre-Snapshot](Plugin_Operations.md#direct-linked-source-pre-snapshot) | `@plugin.linked.pre_snapshot()`
[Direct Linked Source Post-Snapshot](Plugin_Operations.md#direct-linked-source-post-snapshot) | `@plugin.linked.post_snapshot()`
[Staged Linked Source Pre-Snapshot](Plugin_Operations.md#staged-linked-source-pre-snapshot) | `@plugin.linked.pre_snapshot()`
[Staged Linked Source Post-Snapshot](Plugin_Operations.md#linkedsource-post-snapshot) | `@plugin.linked.post_snapshot()`
[Staged Linked Source Start-Staging](Plugin_Operations.md#staged-linked-source-start-staging) | `@plugin.linked.start_staging()`
[Staged Linked Source Stop-Staging](Plugin_Operations.md#staged-linked-source-stop-staging) | `@plugin.linked.stop_staging()`
[Staged Linked Source Status](Plugin_Operations.md#staged-linked-source-status) | `@plugin.linked.status()`
[Staged Linked Source Worker](Plugin_Operations.md#staged-linked-source-worker) | `@plugin.linked.worker()`
[Staged Linked Source Mount Specification](Plugin_Operations.md#staged-linked-source-mount-specification) | `@plugin.linked.mount_specification()`
[Virtual Source Configure](Plugin_Operations.md#virtual-source-configure) | `@plugin.virtual.configure()`
[Virtual Source Unconfigure](Plugin_Operations.md#virtual-source-unconfigure) | `@plugin.virtual.unconfigure()`
[Virtual Source Reconfigure](Plugin_Operations.md#virtual-source-reconfigure) | `@plugin.virtual.reconfigure()`
[Virtual Source Start](Plugin_Operations.md#virtual-source-start) | `@plugin.virtual.start()`
[Virtual Source Stop](Plugin_Operations.md#virtual-source-stop) | `@plugin.virtual.stop()`
[VirtualSource Pre-Snapshot](Plugin_Operations.md#virtualsource-pre-snapshot) | `@plugin.virtual.pre_snapshot()`
[Virtual Source Post-Snapshot](Plugin_Operations.md#virtual-source-post-snapshot) | `@plugin.virtual.post_snapshot()`
[Virtual Source Mount Specification](Plugin_Operations.md#virtual-source-mount-specification) | `@plugin.virtual.mount_specification()`
[Virtual Source Status](Plugin_Operations.md#virtual-source-status) | `@plugin.virtual.status()`

!!! warning
    A plugin should only implement the **direct** operations or the **staged** operations based on the [plugin type](Glossary.md#plugin-type)
