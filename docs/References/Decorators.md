---
title: Virtualization SDK
---

# Decorators

The Virtualization SDK exposes decorators to be able to annotate functions that correspond to each [Plugin Operation](Plugin_Operations.md). 
In the example below, it first creates a `plugin` object by invoking `platform.plugin()`, that can then be used to tag plugin operations.


```python

from dlpx.virtualization import platform

// Initialize a plugin object
plugin = platform.plugin()

@plugin.virtual_source.start()
def start(virtual_source, repository, source_config):
  print "running start" 
```

!!! note
    Decorators exposed by the Virtualization SDK are inherently python function calls and needs parentheses `()` appended at the end.

Assuming the name of the object, is `plugin` as above, the table below lists the corresponding decorators for each plugin operation.

Plugin Operation | Decorator
---------------- |  --------
[SourceConfig Discovey](Plugin_Operations.md#sourceconfig-discovery) | `@plugin.discovery.source_config()`
[Repository Discovey](Plugin_Operations.md#repository-discovery) | `@plugin.discovery.repository()`
[Direct Pre-Snapshot](Plugin_Operations.md#linkedsource-pre-snapshot) | `@plugin.linked.pre_snapshot()`
[Direct Post-Snapshot](Plugin_Operations.md#linkedsource-post-snapshot) | `@plugin.linked.post_snapshot()`
[Staged Pre-Snapshot](Plugin_Operations.md#linkedsource-pre-snapshot) | `@plugin.linked.pre_snapshot()`
[Staged Post-Snapshot](Plugin_Operations.md#linkedsource-post-snapshot) | `@plugin.linked.post_snapshot()`
[Staged Start-Staging](Plugin_Operations.md#linkedsource-start-staging) | `@plugin.linked.start_staging()`
[Staged Stop-Staging](Plugin_Operations.md#linkedsource-stop-staging) | `@plugin.linked.stop_staging()`
[Staged Status](Plugin_Operations.md#linkedsource-status) | `@plugin.linked.status()`
[Staged Worker](Plugin_Operations.md#linkedsource-worker) | `@plugin.linked.worker()`
[Staged MountSpecification](Plugin_Operations.md#linkedsource-mount-specification) | `@plugin.linked.mount_specification()`
[VirtualSource Configure](Plugin_Operations.md#virtualsource-configure) | `@plugin.virtual.configure()`
[VirtualSource Unconfigure](Plugin_Operations.md#virtualsource-unconfigure) | `@plugin.virtual.unconfigure()`
[VirtualSource Reconfigure](Plugin_Operations.md#virtualsource-reconfigure) | `@plugin.virtual.reconfigure()`
[VirtualSource Start](Plugin_Operations.md#virtualsource-start) | `@plugin.virtual.start()`
[VirtualSource Stop](Plugin_Operations.md#virtualsource-stop) | `@plugin.virtual.stop()`
[VirtualSource Pre-Snapshot](Plugin_Operations.md#virtualsource-pre-snapshot) | `@plugin.virtual.pre_snapshot()`
[VirtualSource Post-Snapshot](Plugin_Operations.md#virtualsource-post-snapshot) | `@plugin.virtual.post_snapshot()`
[VirtualSource MountSpecification](Plugin_Operations.md#virtualsource-mount-specification) | `@plugin.virtual.mount_specification()`
[VirtualSource Status](Plugin_Operations.md#virtualsource-status) | `@plugin.virtual.status()`

!!! note
    A plugin should only implement the **direct** operations or the **staged** operations based on the [plugin type](Glossary.md#plugin-type)