# Decorators

The Virtualization SDK exposes [decorators](/References/Decorators.md) as mentioned in the regular documentation. Below we list the additional operations added to suport Lua to Python migrations. This assumes `Plugin()` is instantiated as `plugin`:

Plugin Operation | Decorator
---------------- |  --------
[Lua Repository Data Migration](Plugin_Operations.md#lua-repository-data-migration) | `@plugin.upgrade.repository(lua_version, MigrationType.LUA)`
[Lua Source Config Data Migration](Plugin_Operations.md#lua-source-config-data-migration) | `@plugin.upgrade.source_config(lua_version, MigrationType.LUA)`
[Lua Linked Source Data Migration](Plugin_Operations.md#lua-linked-source-data-migration) | `@plugin.upgrade.linked_source(lua_version, MigrationType.LUA)`
[Lua Virtual Source Data Migration](Plugin_Operations.md#lua-virtual-source-data-migration) | `@plugin.upgrade.virtual_source(lua_version, MigrationType.LUA)`
[Lua Snapshot Data Migration](Plugin_Operations.md#lua-snapshot-data-migration) | `@plugin.upgrade.snapshot(lua_version, MigrationType.LUA)`

!!! info "lua_version format"
    The `lua_version` field in this decorator should be the (major,minor) version of the Lua toolkit. This means if the version is set to `1.1.HOTFIX123` in the `main.json` file for the Lua toolkit, the `lua_version` passed into this decorator should be `1.1`.
