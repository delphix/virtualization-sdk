---
title: Virtualization SDK
---

# Decorators

The Virtualization SDK exposes decorators to be able to annotate functions that correspond to each [Plugin Operation](Plugin_Operations.md). 
In the example below, it first creates a `plugin` object using `platform.plugin()`, that can then be used to tag plugin operations.


```python

from dlpx.virtualization import platform

// Initialize a plugin object
plugin = platform.plugin()

@plugin.virtualsource.start()
def start(source, repository, source_config):
  print "running start" 
```

!!! note
    A decorator is inherently a python function call and needs parentheses `()` appended at the end.

Assuming the name of the object, is `plugin` as above, the table below lists the corresponding decorators for each plugin operation.

Plugin Operation | Decorator
---------------- |  --------
[SourceConfig Discovey](Plugin_Operations.md#sourceconfig-discovery) | `@plugin.discovery.sourceconfig()`
[Repository Discovey](Plugin_Operations.md#repository-discovery) | `@plugin.discovery.repository()`
[LinkedSource Pre-Snapshot](Plugin_Operations.md#linkedsource-pre-snapshot) | `@plugin.linkedsource.pre_snapshot()`
[LinkedSource Post-Snapshot](Plugin_Operations.md#linkedsource-post-snapshot) | `@plugin.linkedsource.post_snapshot()`
[LinkedSource Start-Staging](Plugin_Operations.md#linkedsource-start-staging) | `@plugin.linkedsource.start_staging()`
[LinkedSource Stop-Staging](Plugin_Operations.md#linkedsource-stop-staging) | `@plugin.linkedsource.stop_staging()`
[LinkedSource Status](Plugin_Operations.md#linkedsource-status) | `@plugin.linkedsource.status()`
[LinkedSource Worker](Plugin_Operations.md#linkedsource-worker) | `@plugin.linkedsource.worker()`
[LinkedSource MountSpecification](Plugin_Operations.md#linkedsource-mountspecification) | `@plugin.linkedsource.mountspecification()`
[VirtualSource Configure](Plugin_Operations.md#virtualsource-configure) | `@plugin.virtualsource.configure()`
[VirtualSource Unconfigure](Plugin_Operations.md#virtualsource-unconfigure) | `@plugin.virtualsource.unconfigure()`
[VirtualSource Reconfigure](Plugin_Operations.md#virtualsource-reconfigure) | `@plugin.virtualsource.reconfigure()`
[VirtualSource Start](Plugin_Operations.md#virtualsource-start) | `@plugin.virtualsource.start()`
[VirtualSource Stop](Plugin_Operations.md#virtualsource-stop) | `@plugin.virtualsource.stop()`
[VirtualSource Pre-Snapshot](Plugin_Operations.md#virtualsource-pre-snapshot) | `@plugin.virtualsource.pre_snapshot()`
[VirtualSource Post-Snapshot](Plugin_Operations.md#virtualsource-post-snapshot) | `@plugin.virtualsource.post_snapshot()`
[VirtualSource MountSpecification](Plugin_Operations.md#virtualsource-mountspecification) | `@plugin.virtualsource.mountspecification()`
[VirtualSource Status](Plugin_Operations.md#virtualsource-status) | `@plugin.virtualsource.status()`