# Concurrent Plugin Operations

The Delphix Engine limits how many [Plugin Operations](../References/Plugin_Operations.md) it will run concurrently against a given plugin's toolkit container. This limit scales with the number of CPUs available to the Delphix Engine. Any operations requested beyond this limit are queued and run once a slot frees up — they are not run in parallel and do not fail.

## Concurrency limit by CPU count

The number of plugin operations the engine will run concurrently for a plugin is:

```
min(32, <Engine CPUs> + 4)
```

For example:

| Engine CPUs | Max concurrent plugin operations |
|---|---|
| 2 | 6 |
| 4 | 8 |
| 8 | 12 |
| 28+ | 32 (capped) |

This reflects the current default sizing of the engine's callback thread pool and may change in future Delphix Engine releases.

## Impact

When more plugin operations are triggered at once than the engine can run concurrently — for example, many dSources or VDBs backed by the same plugin syncing or snapshotting around the same time — the extra operations sit in a queue rather than starting immediately. This can look like a single operation is hanging (for example, a `Staged Linked Source Mount Specification` call that appears to take hours) when it is actually waiting for a thread to free up, not stuck in plugin code.

## Recommendations

- When sizing an environment with many objects sharing a single plugin, account for this limit, especially on lower-CPU Delphix Engines.
- Stagger sync/snapshot schedules across objects using the same plugin where possible, rather than scheduling them all at the same time.
- If a plugin operation appears to hang for an unusually long time, first check whether the engine is already running the maximum number of concurrent operations for that plugin before assuming the plugin itself is stuck.
