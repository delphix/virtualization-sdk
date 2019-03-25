# Plugin Config File
The plugin config file is a [YAML](https://yaml.org/) file that marks the root of a plugin and defines metadata about the plugin and its structure. The config file is read at build time to generate the upload artifact.

The name of the file does not matter and can be specified during the build, but, by default, the build looks for `plugin_config.yml`.

## Fields

|Field Name|Required|Type|Description|
|----------|:------:|:--:|-----------|
|name|Y|string|The name of the plugin. This is the plugin's identifier and must be unique.|
|prettyName|Y|string|The display name of the plugin. This will be used in the UI.|
|version|Y|string|The [plugin's version](Plugin_Versioning) in the format `x.y.z`.
|hostTypes|Y|list|The host type that the plugin supports. Either `UNIX` or `WINDOWS`.|
|schemaFile|Y|string|The path to the JSON file that contains the [plugin's schema definitions](Schemas).<br><br>This path can be absolute or relative to the directory containing the plugin config file.|
|srcDir|Y|string|The path to the directory that contains the source code for the plugin. During execution of a plugin operation, this directory will be the current working directory of the Python interpreter. Any modules or resources defined outside of this directory will be inaccessible at runtime.<br><br>This path can be absolute or relative to the directory containing the plugin config file.|
|entryPoint|Y|string|A fully qualified Python symbol that points to the `dlpx.virtualization.platform.Plugin` object that defines the plugin.<br><br>It must be in the form `importable.module:object_name` where `importable.module` is in `srcDir`.|
|manualDiscovery|Y|boolean|True if the plugin supports manual discovery of source config objects.|
|pluginType|Y|enum|The ingestion strategy of the plugin. Can be either `STAGED` or `DIRECT`.|
|language|Y|enum|Must be `PYTHON27`.|
|defaultLocale|N|enum|The local to be used by the plugin if the Delphix user does not specify one. Plugin messages will be displayed in this locale by default. The default value is `en-us`.|

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

This is a valid plugin configuration file for the plugin:

```yaml
name: dlpx-mongo
prettyName: MongoDB
version: 2.0.0
hostTypes:
  - UNIX
entryPoint: mongo_runner:mongodb
srcDir: src/
schemaFile: schema.json
manualDiscovery: true
pluginType: DIRECT
language: PYTHON27
```