# Hidden Properties
Hidden Properties provides plugin developers capability to provide properties that will be shown to user once certain conditions or 
checks are successful based on user inputs. `Hidden Properties` help plugin developers control the flow of user inputs by 
showing only the required properties at first and show the remaining properties based on the user input afterward.

The `hideExpression` accepts an expression that evaluates to a boolean value. The expression can access values from 
other properties. Access values from other properties as below:

=== "Common Root Object"
    | Expression                                                 | JSON Structure                                                     | Description                                              |
    |:-----------------------------------------------------------|:-------------------------------------------------------------------|:---------------------------------------------------------|
    | `model.<property_name>`                                    | <pre>{<br>  "X": "", <br>  "Y": ""<br>}</pre>                      | To hide Y based on X, use `model.X`                      |
    | `field.parent.<N>.parent.model?.<property_name>`<br/><br/> | <pre>{<br>  "X": "", <br>  "Y": {<br>    "Z": ""<br>  }<br>}</pre> | To hide Z based on X, use `field.parent.parent.model?.X` |
    
=== "Different Root Object"
    | Expression                                                               | JSON Structure                                                                                                   | Description                                                    |
    |:-------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------|
    | `field.parent.<N>.parent.model?.<root_names>?.<property_name>`<br/><br/> | <pre>{<br>  "A": {<br>    "B": ""<br>  }, <br>  "X": {<br>    "Y": ""<br>  }<br>}</pre>                          | To hide Y based on B, use `field.parent.parent.model?.A?.B`    |
    |                                                                          | <pre>{<br>  "A": {<br>    "B": {<br>      "C": ""<br>    }<br>  }, <br>  "X": {<br>    "Y": ""<br>  }<br>}</pre> | To hide Y based on C, use `field.parent.parent.model?.A?.B?.C` |

!!! info 
    `parent.<N>.parent` - Parent repeated N times as per JSON structure

## Schema Configuration

### Attributes
|   Attribute    |  Value  |                             Description                              |
|:--------------:|:-------:|:--------------------------------------------------------------------:|
| hideExpression | boolean | If the value evaluates to true, the property is not shown in the UI. |

### Where
- As a Sub-schema of [dxFormProperties](../Schemas.md#dxformproperties), for all data types property.

### Applicable Data Types
- string
- integer
- number
- array
- object
- boolean

### Usage
```json title="Schema" hl_lines="4 5 6"
{
  "<Property_Name>": {
    "type": "string",
    "dxFormProperties": {
      "hideExpression": "<expression that evalutes to a boolean value>"
    }
  }  
}
```

## Examples

???+ example "Examples"
    === "Expressions"
        |                     Expression                      |                           Description                           |
        |:---------------------------------------------------:|:---------------------------------------------------------------:|
        |                 `!model.userName`                   |         Returns true if the userName property is empty.         |
        |                `model.booleanFlag`                  |     Returns true or false based on the booleanFlag property     |
        |          `model.backupType === 'PRIMARY'`           |       Returns true if the backupType property is PRIMARY.       |
        | `model.backupType !== 'PRIMARY' && !model.userName` | Return true if backupType is not primary and userName is empty. |
    === "Common Root Object"
        `password` is a string property which will be shown in the UI if `userName` is present and not empty.
        ```json
        {
          "userName": {
            "type": "string"
          },
          "password": {
            "type": "string",
            "dxFormProperties": {
              "hideExpression": "!model.userName"
            }
          }
        }
        ```
        ![Common Root](images/Dynamic_UI_Common_Root.gif)
    === "Different Root Object"
        `password` is a string property which will be shown in the UI if `userName` is present and not empty.
        ```json
        {
          "userDetails": {
            "type": "object",
            "properties": {
              "userName": {
                "type": "string"
              }
            }
          },
          "securityDetails": {
            "type": "object",
            "properties": {
              "password": {
                "type": "string",
                "dxFormProperties": {
                  "hideExpression": "!field.parent.parent.model?.userDetails?.userName"
                }
              }
            }
          }
        }
        ```
        ![Different Root](images/Dynamic_UI_Different_Root.gif)