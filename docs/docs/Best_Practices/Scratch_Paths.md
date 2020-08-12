#Scratch Paths

A scratch path is a directory reserved for plugin use on each remote host. This is intended for uses such as:

- Storage of small amounts of persistent data
- A place to mount VDB data
- Temporary logs for debugging (Be careful that you don't use too much space though!)

The location of this scratch area is given by the `scratch_path` property on the [RemoteHost](/References/Classes/#remotehost) object.


Things to note about the scratch path:

- No guarantees are made about where the path is located on the system.
- No guarantees are made about how much space might be available in this directory. It is strongly advised that you use only a small amount of disk space here.
- The directory will be owned by the "primary user" associated with the remote host. This might be a completely different user from the one that is associated with a particular dsource or VDB.
- If you need to store dSource- or VDB-specific data, it is highly recommended that you create a separate subdirectory for each dSource/VDB inside this scratch area. It's also recommended to name this subdirectory using the GUID of the dSource/VDB, so that you avoid accidental name collisions.
- The Delphix Engine will not do any cleanup for you, so be sure to delete anything you're no longer using. For example, any VDB-specific information must be deleted in your [unconfigure](/References/Plugin_Operations/#virtual-source-unconfigure) operation (and dSource data gets deleted in your [stopStaging](/References/Plugin_Operations/#staged-linked-source-stop-staging) operation.)
- Do not store any [sensitive information](Sensitive_Data.md) here!
