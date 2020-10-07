# Plugin Config
For all regular fields in a plugin config go [here](/References/Plugin_Config.md). The following fields described are the ones needed to migrate Lua toolkits to Python plugins.

## Fields

|Field Name|Required|Type|Description|
|----------|:------:|:--:|-----------|
|luaName|N|string|The name of the Lua toolkit this plugin should upgrade from. This field is required if the minimumLuaVersion is defined.|
|minimumLuaVersion|N|string|The lowest major minor version of the Lua toolkit that upgrade is supported from. This field is required if the luaName is defined.|

## Example
Assume a lua toolkit with the following `main.json` file:

```json
{
	"type": "Toolkit",
	"name": "delphixdb",
	"prettyName": "DelphixDB",
	"version": "1.0.0",
	"defaultLocale": "en-us",
	"hostTypes": ["UNIX"],
	"discoveryDefinition": {
		"type": "ToolkitDiscoveryDefinition",
		"repositorySchema": {
			"type": "object",
			"properties": {
				"installPath": {
					"type": "string",
					"prettyName": "Delphix DB Binary Installation Path",
					"description": "The path to the Delphix DB installation binaries"
				},
				"version": {
					"type": "string",
					"prettyName": "Version",
					"description": "The version of the Delphix DB binaries"
				}
			}
		},
		"repositoryIdentityFields": ["installPath"],
		"repositoryNameField": "installPath",
		"sourceConfigSchema": {
			"type": "object",
			"properties": {
				"dataPath": {
					"type": "string",
					"prettyName": "Data Path",
					"description": "The path to the Delphix DB instance's data"
				},
				"port": {
					"type": "integer",
					"prettyName": "Port",
					"description": "The port of the Delphix DB"
				},
				"dbName": {
					"type": "string",
					"prettyName": "Delphix DB Name",
					"description": "The name of the Delphix DB instance."
				}
			}
		},
		"sourceConfigIdentityFields": ["dataPath"],
		"sourceConfigNameField": "dataPath"
	},
	"linkedSourceDefinition": {
		"type": "ToolkitLinkedStagedSource",
		"parameters": {
			"type": "object",
			"additionalProperties": false,
			"properties": {
				"primaryDbName": {
					"type": "string",
					"prettyName": "Primary DB Name",
					"description": "The name of the primary database to link.",
					"default": "primaryDB"
				},
				"stagingDbName": {
				"type": "string",
					"prettyName": "Staging DB Name",
					"description": "The name of the staging database to create."
				},
				"stagingPort": {
					"type": "integer",
					"prettyName": "Staging Port",
					"description": "The port of the staging database to create.",
					"default": 1234
				}
			}
		}
	},
	"virtualSourceDefinition": {
		"type": "ToolkitVirtualSource",
		"parameters": {
			"type": "object",
			"additionalProperties": false,
			"properties": {
				"port": {
					"type": "integer",
					"prettyName": "Port",
					"description": "Port that provisioned database should use.",
					"default": 1234
				},
				"dbName": {
					"type": "string",
					"prettyName": "Database Name",
					"description": "Name to use for newly provisioned database.",
					"default": "vdb"
				}
			}
		}
	},
	"snapshotSchema": {
		"type": "object",
		"properties": {
			"snapshotID": {
				"type": "string",
				"prettyName": "Snapshot ID",
				"description": "A unique ID for this snapshot"
			}
		}
	}
}
```

Here is a valid plugin config for a plugin that wants to be upgradable from the toolkit:

```yaml
id: ea009cb4-f76b-46dc-bbb6-689e7acecce4
name: DelphixDB
luaName: delphixdb
minimumLuaVersion: "1.0"
language: PYTHON27
hostTypes:
- UNIX
pluginType: STAGED
entryPoint: plugin_runner:plugin
srcDir: src
schemaFile: schema.json
buildNumber: 2.0.0
```

!!! info "`id` and `luaName` fields in plugins versus `name` field in toolkits"
    * The `luaName` will be used to determine if an already uploaded Lua toolkit is considered a lower version of the Pyhon plugin being uploaded.
    * If the `luaName` is not set then no Lua toolkit will be upgraded.
    * If the `id` of the plugin being uploaded happens to match the `name` in the Lua toolkit already installed on the Delphix Engine, the upload will fail regardless of what the `luaName` is.  
    * When uploading a plugin with the `luaName` set, that `luaName` and `id` pair will be the only pair uploaded successfully. Uploading a new plugin with the same `luaName` but different `id` will fail.
