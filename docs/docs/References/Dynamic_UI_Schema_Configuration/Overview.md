# Overview

Before Delphix Engine 14.0.0.0 release, virtualization SDK only supported basic UI configuration which made UI configuration 
for plugin defined schema complex and cluttered. Plugin developers were not able to modify the behaviour of Delphix Engine UI 
based on the plugin defined schema.

From 14.0.0.0 onwards, plugin developers can modify the Delphix Engine UI based on the plugin defined schema. 

`Dynamic UI Schema Configuration` creates Delphix Engine UI which helps user better understand the plugin configuration 
and also helps plugin developers control the flow of the configuration.

# Schema Attribute

Plugin developers need to add a single attribute [dxFormProperties](../Schemas.md#dxformproperties) to any field they would like 
to control the UI. Other attributes like `rows`, `hideExpression` can be provided to [dxFormProperties](../Schemas.md#dxformproperties) 
to create a specific type of Dynamic UI behaviour.

Table below lists all the allowed attributes within [dxFormProperties](../Schemas.md#dxformproperties) to create UI.

|                   Attribute                   | Description                                                         |
|:---------------------------------------------:|:--------------------------------------------------------------------|
| [Collapsible Section](Collapsible_Section.md) | Allows to collapse and expand `object` and `array` type properties. |
|       [Hidden Fields](Hidden_Fields.md)       | Allows to hide properties based on conditions.                      |
|           [Text Area](Text_Area.md)           | Convert any string field to multi line text input property.         |
| [Validation Messages](Validation_Messages.md) | Add custom validation messages to user inputs.                      |

# Version Compatibility

|        Dynamic UI Schema Configuration        |       Earliest Supported vSDK Version        |          Latest Supported vSDK Version          | Earliest Supported DE Version |                    Latest Supported DE Version                    |
|:---------------------------------------------:|:--------------------------------------------:|:-----------------------------------------------:|:-----------------------------:|:-----------------------------------------------------------------:|
| [Collapsible Section](Collapsible_Section.md) | [4.0.2](https://pypi.org/project/dvp/4.0.2/) | [Latest Release](https://pypi.org/project/dvp/) |           14.0.0.0            | [Latest Release](https://cd.delphix.com/docs/latest/new-features) |
|       [Hidden Fields](Hidden_Fields.md)       | [4.0.2](https://pypi.org/project/dvp/4.0.2/) | [Latest Release](https://pypi.org/project/dvp/) |           14.0.0.0            | [Latest Release](https://cd.delphix.com/docs/latest/new-features) |
|           [Text Area](Text_Area.md)           | [4.0.2](https://pypi.org/project/dvp/4.0.2/) | [Latest Release](https://pypi.org/project/dvp/) |           14.0.0.0            | [Latest Release](https://cd.delphix.com/docs/latest/new-features) |
| [Validation Messages](Validation_Messages.md) | [4.0.2](https://pypi.org/project/dvp/4.0.2/) | [Latest Release](https://pypi.org/project/dvp/) |           14.0.0.0            | [Latest Release](https://cd.delphix.com/docs/latest/new-features) |

