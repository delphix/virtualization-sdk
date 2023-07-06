# Hidden Properties
Hidden Properties provides plugin developers capability to provide properties that will be shown to user once certain conditions or 
checks are successful based on user inputs. `Hidden Properties` help plugin developers control the flow of user inputs by 
showing only the required properties at first and show the remaining properties based on the user input afterward.

The `hideExpression` accepts an expression that evaluates to a boolean value. The expression can access values from 
other properties. Access values from other properties as below:

=== "Same Level"
    1. Expression - `model.<property_name>`
    2. Example
        - `userName` and `paasword` are on same level.
        - use `!model.userName` in `password`.

=== "One Level up"
    1. Expression - `field.parent.parent.model.<property_name>`
    2. Example
        - `userName` is at `userDetails.userName`.
        - `password` is at`userDetails.security.password`.
        - use `!field.parent.parent.model.userName` in `password`.

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

    === "Single Level"
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
        ![Single Level](images/Dynamic_UI_Same_Level.gif)

    === "Multi Level"
        `password` is a string property which will be shown in the UI if `userName` is present and not empty.
        ```json
        {
          "userName": {
            "type": "string"
          },
          "security": {
            "type": "object",
            "properties": {
              "details": {
                "type": "object",
                "properties": {
                  "password": {
                    "type": "string",
                    "dxFormProperties": {
                      "hideExpression": "!field.parent.parent.model.userName"
                    }
                  }
                }
              }
            }
          }
        }
        ```
        ![Multi Level - TBD]()