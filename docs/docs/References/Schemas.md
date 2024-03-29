# Schemas

## About Schemas

Any time a plugin needs to store its own data, or needs to ask the user for data, the Delphix Engine needs to be told about the format of that data:

* What is the set of data needed and what should they be called?
* What is the type of each piece of data: Strings? Integers? Booleans?

Plugins use [schemas](Glossary.md#schema) to describe the format of such data. Once a schema is defined, it is used in three ways

1. It tells the Delphix Engine how to store the data for later use.
2. It is used to autogenerate a custom user interface, and to validate user inputs.
3. It is used to [autogenerate Python classes](Schemas_and_Autogenerated_Classes.md) that can be used by plugin code to access and manipulate user input and stored data.

There are five plugin-customizable data formats:

Delphix Object | Schema | Autogenerated Class
-------------- | ------ | -------------------
[Repository](Glossary.md#repository) | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-schema) | [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-class)
[Source Config](Glossary.md#source-config) | [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-schema) | [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-class)
[Linked Source](Glossary.md#linked-source) | [LinkedSourceDefinition](Schemas_and_Autogenerated_Classes.md#linkedsourcedefinition-schema) | [LinkedSourceDefinition](Schemas_and_Autogenerated_Classes.md#linkedsourcedefinition-class)
[Virtual Source](Glossary.md#virtual-source) | [VirtualSourceDefinition](Schemas_and_Autogenerated_Classes.md#virtualsourcedefinition-schema)| [VirtualSourceDefinition](Schemas_and_Autogenerated_Classes.md#virtualsourcedefinition-class)
[Snapshot](Glossary.md#linked-source) | [SnapshotDefinition](Schemas_and_Autogenerated_Classes.md#snapshotdefinition-schema) | [SnapshotDefinition](Schemas_and_Autogenerated_Classes.md#snapshotdefinition-class)
[Snapshot Parameters](Glossary.md#snapshot-parameters) | [SnapshotParametersDefinition](Schemas_and_Autogenerated_Classes.md#snapshotparametersdefinition-schema) | [SnapshotParametersDefinition](Schemas_and_Autogenerated_Classes.md#snapshotparametersdefinition-class)

!!! warning
    There are limits to how much data can be stored within a plugin defined schema. See [Message Limits](../Best_Practices/Message_Limits.md) for details.

## JSON Schemas

Plugins use JSON schemas for their custom datatypes. There are three main things to understand about them, which are explained just below:

* What is JSON?
* What is a JSON schema?
* How has Delphix augmented JSON schemas?

### JSON
JSON stands for "Javascript Object Notation". JSON is a data-interchange format that is intended to be precise and also somewhat human-readable. Here are some simple examples of data in JSON format:

JSON | Description
---- | ------------
`"hello"`     | A string. Note the double quotes.
`17`          | An integer
`true`        | A boolean
`{"name": "Julie", "age": 37}` | A JSON object with two fields, `name` (a string), and `age` (an integer). Objects are denoted with curly braces.
`[ true, false, true] ` | A JSON array with three booleans. Arrays are denoted with square brackets.

For more details on JSON, please see <https://www.json.org/>.

### JSON Schemas

The "JSON schema" format is built on top of JSON. This adds some special rules and keywords that are intended to facilitate the *description* of the format of data (whereas "raw" JSON is intended for storing data).

Here is an example of a JSON schema that defines a (simplified) US address:

```json
{
    "type": "object",
    "required": ["name", "streetNumber", "street", "city", "state", "zip5"],
    "additionalProperties": false,
    "properties": {
        "name": { "type": "string" },
        "streetNumber": { "type": "string" },
        "street": { "type": "string" },
        "unit": { "type": "string" },
        "city": { "type": "string", "pattern": "^[A-Z][A-Za-z ]*$" },
        "state": { "type": "string", "pattern": "^[A-Z]{2}$" },
        "zip5": { "type": "string", "pattern": "^[0-9]{5}"},
        "zipPlus4": { "type": "string", "pattern": "^[0-9]{4}"}
    }
}
```

Note that this is perfectly valid JSON data. It's a JSON object with four fields: `type` (a JSON string), `required` (A JSON array), `additionalProperties` (a JSON boolean), and `properties`. `properties`, in turn is a JSON object with with 8 fields, each of which is a JSON object, with its own properties, etc.

But, this isn't *just* a JSON object. This is a JSON schema. It uses special keywords like `type` `required`, and `additionalProperties`. These have specially-defined meanings in the context of JSON schemas.

Here is a list of the special keywords used by the above schema. Note that this is only a small subset of JSON schema keywords.

keyword | description
------- | -----------
`additionalProperties` | Determines whether the schema allows properties that are not explicitly listed in the `properties` specification. Must be a `true` or `false`.
`pattern` | Used with string types to specify a regular expression that the property must conform to.
`required`| A list of required properties. Properties not listed in this list are optional.
`string`  | Used with `type` to declare that a property must be a string.
`type`    | Specifies a datatype. Common values are `object`, `array`, `number`, `integer`, `boolean`, and `string`.

Some points to note about the address schema above:

* Because of the `required` list, all valid addresses must have fields called `name`, `streetNumber` and so on.
* `unit` and `zipPlus4` do not appear in the `required` list, and therefore are optional.
* Because of `additionalProperties` being `false`, valid addresses cannot make up their own fields like `nickname` or `doorbellLocation`.
* Because of the `pattern`, any `state` field in a valid address must consist of exactly two capital letters.
* Similarly, `city` must only contain letters and spaces, and `zip` and `zipPlus4` must only contain digits.
* Each property has its own valid subschema that describes its own type definition.

Here is a JSON object that conforms to the above schema:

```json
{
  "name": "Delphix",
  "streetNumber": "220",
  "street": "Congress St.",
  "unit": "200",
  "city": "Boston",
  "state": "MA",
  "zip": "02210"
}
```

!!! info
    A common point of confusion is the distinction between a JSON schema and a JSON object that conforms to a schema. Remember, a schema describes the form of data. In our example, the schema *describes* what an address looks like. The address itself is not a schema.


For much more detail on JSON schemas, including which keywords are available, what they mean, and where you can use them, see <https://json-schema.org/understanding-json-schema/>.

!!! info
    Be careful when using the JSON schema keyword `default`. This keyword is commonly misunderstood. Specifically, it does not mean "If the user does not provide a value, then this default value will be auto-substituted instead", as you might expect. In fact, in JSON schemas, `default` has no semantic meaning at all! Currently, the only thing the Delphix Engine will use this for is to pre-fill widgets on the UI.

### Delphix-specific Extensions to JSON Schema

The JSON schema vocabulary is designed to be extensible for special uses, and Delphix has taken advantage of this to add some new Delphix-specific keywords.

The list below outlines each of these keywords, and provides minimal examples of how they might be used.

#### `description`

| Summary | |
|-------- | |
| Required or Optional? | Optional|
| Where? | In any property subschema, at the same level as `type`.|

The `description` keyword can optionally appear on any property. If it does appear, it is used by the UI as explanatory text for the UI widget associated with the property. If it does not appear, then no explanatory text is shown.

In this example, the UI would show "User-readable name for the provisioned database" in small text under the widget.

```json
{
  "properties": {
    "name": {
      "type": "string",
      "description": "User-readable name for the provisioned database"
    }
  }
}
```

#### `identityFields`

| Summary | |
| ------- | |
| Required or Optional? | Required (for repository and source config schemas only) |
| Where? | At the top level of a repository or source config schema, at the same level as `type` and `properties`.|

The `identityFields` is a list of property names that, together, serve as a unique identifier for a repository or source config.

When a plugin's [automatic discovery](Glossary.md#automatic-discovery) code is called, it will return a list of repositories (or source configs). The Delphix Engine needs to be able to compare this new list with whatever repositories it already knows about.

For example, suppose the engine already knows about a single repository with data `{"dbname": "my_databsae", "path": "/var/db/db01"}` (note the misspelling!). And, then suppose that automatic discovery is re-run and it returns repository data `{ "dbname": "my_database", "path": "/var/db/db01"}`.

What should the Delphix Engine do? Should it conclude that "my_databsae" has been deleted, and there is a completely new repository named "my_database"? Or, should it conclude that we still have the same old repository, but with an updated name?

`identityFields` is used to handle this. When the engine compares "new" data with "old" data, it concludes that they belong to the same repository if **all** of the identity fields match. If any of the identity fields do not match, then the "new" repository data is judged to represent a different repository than the old data.

`identityFields` is **required** for [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-schema) and [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-schema) schemas, and may not be used in any other schemas.

In this example, we'll tell the Delphix Engine that `path` is the sole unique identifier.

```json
{
  "properties": {
      "dbname": {"type": "string"},
      "path": {"type": "string"}
  },
  "identityFields": ["path"]
}
```

#### `nameField`

| Summary | |
| ------- | |
| Required or Optional? | Required (for repository and source config schemas only) |
| Where? | At the top level of a repository or source config schema, at the same level as `type` and `properties`.|

The `nameField` keyword specifies a single property that is to be used to name the object in the Delphix Engine. The property must be a string field. This keyword is used at the same level as `properties`. It is **required** for [RepositoryDefinition](Schemas_and_Autogenerated_Classes.md#repositorydefinition-schema) and [SourceConfigDefinition](Schemas_and_Autogenerated_Classes.md#sourceconfigdefinition-schema) schemas, and may not be used in any other schemas.

In this example, we will use the `path` property as the user-visible name.

```json
{
    "properties": {
        "path": { "type": "string" },
        "port": { "type": "integer" }
    },
    "nameField": "path"
}
```

So, if we have an repository object that looks like

```json
{
  "path": "/usr/bin",
  "port": 8800
}
```
then the user will be able to refer to this object as `/usr/bin`.

#### `ordering`

| Summary | |
| ------- | |
| Required or Optional? | Optional |
| Where? | At the top level, same level as `type` and `properties`.|

The `ordering` keyword can be used to order the fields when the UI is autogenerated.

```json
{
    "properties": {
        "path": { "type": "string" },
        "port": { "type": "integer" }
    },
    "ordering": ["port", "path"]
}
```

In the example above, the `port` will be the first field in the autogenerated UI wizard followed by `path`.

#### `password`

| Summary | |
| ------- | |
| Required or Optional? | Optional|
| Where? | As the value for the `format` keyword in any string property's subschema.|

The `password` keyword can be used to specify the `format` of a `string`. (Note that `format` is a standard keyword and is not Delphix-specific). If a property is tagged as a password, then the UI will never show the value on screen, and the value will be encrypted before being stored as described [here](../Best_Practices/Sensitive_Data.md).

In this example, the `dbPass` field on any object will be treated as a password.

```json
{
  "properties": {
    "dbPass": {
      "type": "string",
      "format": "password"
    }
  }
}
```

#### `prettyName`

| Summary | |
| ------- | |
| Required or Optional? | Optional|
| Where? | In any property subschema, at the same level as `type`.|

The `prettyName` keyword can optionally appear on any property. If it does appear, it is used by the UI as a title for the UI widget associated with the property. If it does not appear, then the name of the property is used.

In this example, the user would see "Name of Database" on the UI, instead of just "name".

```json
{
  "properties": {
    "name": {
      "type": "string",
      "prettyName": "Name of Database"
    }
  }
}
```

#### `unixpath`

| Summary | |
| ------- | |
| Required or Optional? | Optional|
| Where? | As the value for the `format` keyword in any string property's subschema.|

The `unixpath` keyword is used to specify the `format` of a string. This will allow the Delphix Engine to verify and enforce that a particular field can be parsed as a valid Unix path.

```json
{
  "properties": {
    "datapath": {
      "type": "string",
      "format": "unixpath"
    }
  }
}
```

#### `reference`

| Summary | |
| ------- | |
| Required or Optional? | Optional|
| Where? | As the value for the `format` keyword in any string property's subschema.|

The `reference` keyword is used to specify the `format` of a string.
This will allow the plugin author to ask the user to select [environments](Glossary.md#environment) and [environment users](Glossary.md#environment-user) on the Delphix Engine.

```json
"properties": {
  "env": {
    "type": "string",
    "format": "reference",
    "referenceType": "UNIX_HOST_ENVIRONMENT"
  },
  "envUser": {
    "type": "string",
    "format": "reference",
    "referenceType": "HOST_USER",
    "matches": "env"
  }
}
```

#### `referenceType`

| Summary | |
| ------- | |
| Required or Optional? | Optional|
| Where? | In any property subschema of type `string` and format `reference`, at the same level as type.|

The `referenceType` keyword is used to specify the [reference](#reference) type. Possible values:

* [Environment](Glossary.md#environment): `UNIX_HOST_ENVIRONMENT`
* [Environment User](Glossary.md#environment-user): `HOST_USER`

```json
"properties": {
  "env": {
    "type": "string",
    "format": "reference",
    "referenceType": "UNIX_HOST_ENVIRONMENT"
  },
  "envUser": {
    "type": "string",
    "format": "reference",
    "referenceType": "HOST_USER",
    "matches": "env"
  }
}
```

#### `matches`

| Summary | |
| ------- | |
| Required or Optional? | Optional|
| Where? | In any property subschema of type `string` and format `reference`, at the same level as type.|

The `matches` keyword is used to map an [environment user](Glossary.md#environment-user) to an [environment](Glossary.md#environment) by specifying the environment's property name.

```json
"properties": {
  "env": {
    "type": "string",
    "format": "reference",
    "referenceType": "UNIX_HOST_ENVIRONMENT"
  },
  "envUser": {
    "type": "string",
    "format": "reference",
    "referenceType": "HOST_USER",
    "matches": "env"
  }
}
```

In the example above, environment user `envUser` maps to environment `env`.

#### `dxFormProperties`

| Summary | |
| ------- | |
| Required or Optional? | Optional|
| Where? | In any property subschema, at the same level as `type`.|

The `dxFormProperties` keyword is used to generate [dynamic UI](Dynamic_UI_Schema_Configuration/Overview.md) and better show the configuration details to user on Delphix Engine UI.

```json
"properties": {
  "textAreaField": {
    "type": "string",
    "dxFormProperties": {
      "rows": 5 
    }
  },
  "userName": {
    "type": "string",
    "minLength": 8,
    "pattern": "postgre.*",
    "dxFormProperties": {
      "validationMessages": {
        "minLength": "The minimum length for userName should be 8.",
        "pattern": "The userName should start with \"postgre\"."
      }
    }
  }
}
```

In the example above, 

* providing `rows` to `textAreaField` of type `string` convert it to a Text Area in UI. 
* For `userName` providing `custom validation message` for inputs helps user better understand the input requirements.

### Delphix-specific Pre-defined Types

Plugins can also take advantage of pre-defined object types offered by Delphix. Currently, these object types let users supply credentials to plugins directly or via password vaults. Password vaults have [a number of benefits for securing and managing secrets](../Best_Practices/Sensitive_Data.md#protecting-sensitive-data-with-password-vaults).

These pre-defined types can be referenced by JSON schemas via the external schema identifier `https://delphix.com/platform/api`. This is only an identifier, not a web address.

The list below describes each of these definitions and shows how they can be referenced by plugins and users. (To understand how to use these objects at runtime, see [this section](../Best_Practices/Sensitive_Data.md#protecting-sensitive-data-with-password-vaults).)

#### `credentialsSupplier`

Defines an object type that lets users supply credentials consisting of a username (optional) and a secret. The secret can be a password or a private key. In case of a private key, a corresponding public key may also be included. This data can be entered directly by the user or supplied by a password vault. If as password or private key is entered directly, the UI will never show the value on screen, and the value will be encrypted before being stored as described [here](../Best_Practices/Sensitive_Data.md#marking-your-data-as-sensitive).

An example of a JSON schema using this type is:

```json
"properties": {
  "myCredentials": {
    "$ref": "https://delphix.com/platform/api#/definitions/credentialsSupplier"
  }
}
```
where `credentialsSupplier` is a definition in the external schema `https://delphix.com/platform/api`.

When providing data for a property of this type, the user has the following four options.

##### Option 1: Username and password

For this option, the user must provide data that satisfies this definition:
```json
{
  "type": "object",
  "required": ["type", "password"],
  "properties": {
    "type": {
      "type": "string",
      "const": "NamedPasswordCredential"
    },
    "username": {
      "type": "string"
    },
    "password": {
      "type": "string",
      "format": "password"
    }
  }
}
```
where `type` is a constant of value `NamedPasswordCredential`. This value is needed by the Delphix engine to determine the option being used. The graphical user interface will not show this element; it will send this constant value automatically to the Delphix engine.

The `username` property is optional.

For example, the user, or the user interface on behalf of the user, can provide:
```json
"properties": {
  "myCredentials": {
    "type": "NamedPasswordCredential",
    "username": "my user name",
    "password": "my password"
  }
}
```

##### Option 2: Username and key(s)

For this option, the user must provide data that satisfies this definition:
```json
{
  "type": "object",
  "required": ["type", "privateKey"],
  "properties": {
    "type": {
      "type": "string",
      "const": "NamedKeyPairCredential"
    },
    "username": {
      "type": "string"
    },
    "publicKey": {
      "type": "string"
    },
    "privateKey": {
      "type": "string",
      "format": "password"
    }
  }
}
```
where the `username` and `publicKey` properties are optional, and `type` is a constant that the
user interface will submit automatically on behalf of the user.

For example, the user, or the user interface on behalf of the user, can provide:
```json
"properties": {
  "myCredentials": {
    "type": "NamedKeyPairCredential",
    "username": "my user name",
    "publicKey": "AAA4QG...HBCDD3=",
    "privateKey": "-----BEGIN RSA PRIVATE KEY-----...-----END RSA PRIVATE KEY-----"
  }
}
```

##### Option 3: CyberArk vault credentials

For this option, the user must provide data that satisfies this definition:
```json
{
  "type": "object",
  "required": ["type", "vault", "queryString"],
  "properties": {
    "type": {
      "type": "string",
      "const": "CyberArkVaultCredential"
    },
    "vault": {
      "type": "string",
      "format": "reference",
      "referenceType": "CyberArkPasswordVault"
    },
    "queryString": {
      "type": "string"
    },
    "expectedSecretType": {
      "type": "string",
      "enum": ["any", "password", "keyPair"],
      "default": "any"
    }
  }
}
```
where `type` is a constant that the user interface will submit automatically on behalf of the user, `vault` is a reference to a CyberArk vault configured in the system, and `queryString` is a parameter for locating the credentials in the vault. For details on configuring and using CyberArk vaults, see the [password-vaults documentation for the Delphix engine](https://cd.delphix.com/docs/latest/password-vault-support).

Optionally, `expectedSecretType` lets the user constrain the secret returned by the vault to passwords or keys (the default is to allow `any` of those two types of secret). An unexpected type of secret returned by the vault will result in a runtime exception.

For example, the user, or the user interface on behalf of the user, can provide:
```json
"properties": {
  "myCredentials": {
    "type": "CyberArkVaultCredential",
    "vault": "CYBERARK_PASSWORD_VAULT-1",
    "queryString": "Safe=test;Object=myObject"
  }
}
```

##### Option 4: HashiCorp vault credentials

For this option, the user must provide data that satisfies this definition:
```json
{
  "type": "object",
  "required": ["type", "vault", "engine", "path", "usernameKey", "secretKey"],
  "properties": {
    "type": {
      "type": "string",
      "const": "HashiCorpVaultCredential"
    },
    "vault": {
      "type": "string",
      "format": "reference",
      "referenceType": "HashiCorpVault"
    },
    "engine": {
      "type": "string"
    },
    "path": {
      "type": "string"
    },
    "usernameKey": {
      "type": "string"
    },
    "secretKey": {
      "type": "string"
    },
    "expectedSecretType": {
      "type": "string",
      "enum": ["any", "password", "keyPair"],
      "default": "any"
    }
  }
}
```
where `type` is a constant that the user interface will submit automatically on behalf of the user, `vault` is a reference to a HashiCorp vault configured in the system, and `engine`, `path`, `usernameKey` and `secretKey` are parameters for locating the credentials in the vault. For details on configuring and using HashiCorp vaults, see the [password-vaults documentation for the Delphix engine](https://cd.delphix.com/docs/latest/password-vault-support).

Optionally, `expectedSecretType` lets the user constrain the secret returned by the vault to passwords or keys (the default is to allow `any` of those two types of secret). An unexpected type of secret returned by the vault will result in a runtime exception.

The `type` property is a constant that the user interface will submit automatically on behalf of the user.

For example, the user, or the user interface on behalf of the user, can provide:
```json
"properties": {
  "myCredentials": {
    "type": "HashiCorpVaultCredential",
    "vault": "HASHICORP_VAULT-2",
    "engine": "kv-v2",
  }
}
```

#### `keyCredentialsSupplier`

This object type is identical to `credentialsSupplier` but requires the secrets to be keys. The available options are [keys](#option-2-username-and-keys), [CyberArk vaults](#option-3-cyberark-vault-credentials) and [HashiCorp vaults](#option-4-hashicorp-vault-credentials). The property `expectedSecretType` is required in all cases and must have the value `keyPair`.

#### `passwordCredentialsSupplier`

This object type is identical to `credentialsSupplier` but requires the secrets to be passwords. The available options are [passwords](#option-1-username-and-password), [CyberArk vaults](#option-3-cyberark-vault-credentials) and [HashiCorp vaults](#option-4-hashicorp-vault-credentials). The property `expectedSecretType` is required in all cases and must have the value `keyPair`.

## JSON Schema Limitations

To be able to autogenerate Python classes there are some restrictions to the JSON Schemas that are supported.

### Generation Error
There are some valid JSON schemas that will cause the property to not be generated in the autogenerated Python classes. Unfortunately the build command will silently fail so be sure to look at the generated classes and verify all the properties exist.

#### Multiple types
For the `type` keyword, only a single type may be specified. Arrays of types are not supported.
```json
{
  "repositoryDefinition": {
    "type": "object",
    "additionalProperties": "false",
    "properties": {
      "data": {
        "type": ["integer", "string"]
      }
    },
    "nameField": "data",
    "identityFields": ["data"]
  }
}
```
The `data` property will not even exist:
```python
from generated.defintions import RepositoryDefinition

repository = RepositoryDefinition()
repository.data = 3
print(repository)
```
This would print:
```
{}
```

#### Combining schemas
For the following keywords, if they are specified the property will not exist in the class.
* anyOf
* allOf
* oneOf
* not
```json
{
  "repositoryDefinition": {
    "type": "object",
    "additionalProperties": "false",
    "properties": {
      "any": {
        "anyOf": [
          {"type": "integer", "minimum": 2},
          {"type": "string", "minLength": 4}
        ]
      },
      "one": {
        "oneOf": [
          {"type": "integer", "minimum": 3},
          {"type": "integer", "maximum": 5}
        ]
      }
    },
    "nameField": "data",
    "identityFields": ["data"]
  }
}
```
The `any` and `one` properties would not exist:
```python
from generated.defintions import RepositoryDefinition

repository = RepositoryDefinition()
repository.any = "string"
repository.one = 6
print(repository)
```
This would print:
```
{}
```

#### Object Additional Properties
The `additionalProperties` keyword inside the object property can either be a boolean or a JSON schema. If it is a schema it needs to have the keyword `type`. If the `additionalProperties` is set to a JSON schema then the `properties` keyword will be ignored. If the keyword is set to a boolean the behaviour will be the same regardless of if it was set to `true` or `false`.

```json
{
  "repositoryDefinition": {
    "type": "object",
    "additionalProperties": "false",
    "properties": {
      "dataOne": {
        "type": "object",
        "addtionalProperties": {"type": "string"}
      },
      "dataTwo": {
        "type": "object",
        "addtionalProperties": {"type": "string"},
        "properties": {
          "data": {"type": "string"}
        }
      },
      "dataThree": {
        "type": "object",
        "addtionalProperties": "false",
        "properties": {
          "data": {"type": "string"}
        }
      },
      "dataFour": {
        "type": "object",
        "addtionalProperties": "true",
        "properties": {
          "data": {"type": "string"}
        }
      },
      "dataFive": {
        "type": "object",
        "addtionalProperties": "false",
      },
      "dataSix": {
        "type": "object",
        "addtionalProperties": "true",
      }
    },
    "nameField": "dataOne",
    "identityFields": ["dataOne"]
  }
}
```
From the schema above, the properties `dataOne` and `dataTwo`, `dataThree` and `dataFour`, and `dataFive` and `dataSix` will have an identical validations. The first two will validate that the object passed in is a dict with key and value both `string` type. The next two will create a new inner Python class called either `OtherDefinitionDataThree` or `OtherDefinitionDataFour`, they optomize for creating only one as they are identical. Inside that object will be one property `data`. The last two properties will validate that the object passed in is a dict with the key as a `string` type, and the value can be anything.

### Validation Keywords
In general all property types are supported however some validation keywords will be ignored during the execution of the Python code. This means that if these keywords are used, no error would be raised within Python if the object violates the schema. Listed below are the keywords ignored for each type that wouldn't validate. Some have examples to be more clear.

#### Number / Integer
* multipleOf
```json
{
  "repositoryDefinition": {
    "type": "object",
    "additionalProperties": "false",
    "properties": {
      "data": {
        "type": "integer",
        "multipleOf": 2
      }
    },
    "nameField": "data",
    "identityFields": ["data"]
  }
}
```
This would work even though it would fail the schema check:
```python
from generated.defintions import RepositoryDefinition

repository = RepositoryDefinition()
repository.data = 3
```

#### Arrays / Tuples
* additionalItems
* minItems
* maxItems
* uniqueItems
* contains
* items
    * Must be a single type, not an array (tuples are not supported):
```json
{
  "repositoryDefinition": {
    "type": "object",
    "additionalProperties": "false",
    "properties": {
      "data": {
        "type": "array",
        "items": [
          {"type": "number"},
          {"type": "string"},
          {"type": "boolean"}
        ]
      }
    },
    "nameField": "data",
    "identityFields": ["data"]
  }
}
```
This would work even though it would fail the schema check:
```python
from generated.defintions import RepositoryDefinition

repository = RepositoryDefinition()
repository.data = ["string", False, 3]
```

#### Objects
* minProperties
* maxProperties
* patternProperties
* dependencies
* propertyNames

#### Enumerated values
If the `enum` keyword is used within a subobject, `type` has to be `string`.
```json
{
  "repositoryDefinition": {
    "type": "object",
    "additionalProperties": "false",
    "properties": {
      "stringData": {
        "enum": ["A", "B", "C"]
      },
      "arrayData": {
        "type": "array",
        "items": {
          "enum": ["DO", "RE", "MI"]
        }
      },
      "objectData": {
        "type": "object",
        "additionalProperties": {
          "enum": ["ONE", "TWO", "THREE"]
        }
      },
      "definedObjectData": {
        "type": "object",
        "properties": {
          "objectStringData": {
            "enum": ["o.A", "o.B", "o.C"]
          },
        },
        "additionalProperties": "false"
      }
    },
    "nameField": "stringData",
    "identityFields": ["stringData"]
  }
}
```
In the above example there are four properties: `stringData`, `arrayData`, `objectData`, and `definedObjectData`. Validation works for stringData but are skipped for the other three. In fact the definedObjectData which with properties would usually create a separte Python class does not at all.
This means the following code would work even though it would fail the schema check:
```python
from generated.defintions import RepositoryDefinition

repository = RepositoryDefinition()
repository.array_data = [10, 11, 12]
repository.object_data = {"key": 1}
repository.defined_object_data = {"key": 2}
```
And this code would actually fail with a `GeneratedClassesError` during the Python execution saying `Invalid enum value D for 'string_data', must be one of [A, B, C] if defined.`:
```python
from generated.defintions import RepositoryDefinition

repository = RepositoryDefinition()
repository.string_data = "D"
```
