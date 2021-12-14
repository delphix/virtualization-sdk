# Plugin Config
The plugin config is a [YAML](https://yaml.org/) file that marks the root of a plugin and defines metadata about the plugin and its structure. The config file is read at build time to generate the upload artifact.

The name of the file can be specified during the build. By default, the build looks for `plugin_config.yml` in the current working directory.

## Fields

|Field Name|Required|Type|Description|
|----------|:------:|:--:|-----------|
|id|Y|string|The unique id of the plugin in a valid UUID format.|
|name|N|string|The display name of the plugin. This will be used in the UI. If it is not specified name will be equal to id.|
|externalVersion|N|string|The plugin's [external version](/Versioning_And_Upgrade/Versioning.md#external-version). This is a freeform string. If it is not supplied, the build number is used as an external version.
|buildNumber|Y|string|The plugin's [build number](/Versioning_And_Upgrade/Versioning.md#build-number). This string must conform to the format described [here](/Versioning_And_Upgrade/Versioning.md#build-number-format-rules).
|hostTypes|Y|list|The host type that the plugin supports. Either `UNIX` or `WINDOWS`.|
|schemaFile|Y|string|The path to the JSON file that contains the [plugin's schema definitions](Schemas.md).<br><br>This path can be absolute or relative to the directory containing the plugin config file.|
|srcDir|Y|string|The path to the directory that contains the source code for the plugin. During execution of a plugin operation, this directory will be the current working directory of the Python interpreter. Any modules or resources defined outside of this directory will be inaccessible at runtime.<br><br>This path can be absolute or relative to the directory containing the plugin config file.|
|entryPoint|Y|string|A fully qualified Python symbol that points to the `dlpx.virtualization.platform.Plugin` object that defines the plugin.<br><br>It must be in the form `importable.module:object_name` where `importable.module` is in `srcDir`.|
|manualDiscovery|N|boolean|True if the plugin supports manual discovery of source config objects. The default value is `true`.|
|pluginType|Y|enum|The ingestion strategy of the plugin. Can be either `STAGED` or `DIRECT`.|
|language|Y|enum|Must be `PYTHON38`.|
|defaultLocale|N|enum|The locale to be used by the plugin if the Delphix user does not specify one. Plugin messages will be displayed in this locale by default. The default value is `en-us`.|
|rootSquashEnabled|N|boolean|This dictates whether "root squash" is enabled on NFS mounts for the plugin (i.e. whether the `root` user on remote hosts has access to the NFS mounts). Setting this to `false` allows processes usually run as `root`, like Docker daemons, access to the NFS mounts. The default value is `true`. This field only applies to Unix hosts.|
|extendedStartStopHooks|N|boolean|This controls whether the user's pre-start and post-start hooks will run during enable operations (and, likewise, whether pre-stop and post-stop hooks will run during disable operations). The default value is `false`.|

## Example
Assume the following basic plugin structure:

```
├── plugin_config.yml
├── schema.json
└── src
    └── mongo_runner.py
```

`mongo_runner.py` contains:

```python
from dlpx.virtualization.platform import Plugin


mongodb = Plugin()
```

This is a valid plugin config for the plugin:

```yaml
id: 7cf830f2-82f3-4d5d-a63c-7bbe50c22b32
name: MongoDB
hostTypes:
  - UNIX
entryPoint: mongo_runner:mongodb
srcDir: src/
schemaFile: schema.json
pluginType: DIRECT
language: PYTHON38
buildNumber: 0.1.0
```
This is a valid plugin config for the plugin with `manualDiscovery` set to `false` and an `externalVersion` set:

```yaml
id: 7cf830f2-82f3-4d5d-a63c-7bbe50c22b32
name: MongoDB
hostTypes:
  - UNIX
entryPoint: mongo_runner:mongodb
srcDir: src/
schemaFile: schema.json
manualDiscovery: false
pluginType: DIRECT
language: PYTHON38
externalVersion: "MongoDB 1.0"
buildNumber: "1"
```
