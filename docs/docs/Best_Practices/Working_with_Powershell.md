
### Error handling in Powershell

!!! info
    Commands run via run_powershell are executed as a script. The exit code returned by run_powershell as part of the RunPowershellResult is determined by the exit code from the script.
PowerShell gives you a few ways to handle errors in your scripts:

1. Set $ErrorActionPreference. This only applies to PowerShell Cmdlets. For scripts or other executables such as sqlcmd, PowerShell will return with exit code 0 even if there is an error, regardless of the value of $ErrorActionPrefe       rence. The allowable values for $ErrorActionPreference are:

      Continue (default) – Continue even if there is an error.                            
      SilentlyContinue – Acts like Continue with the exception that errors are not displayed           
      Inquire – Prompts the user in case of error            
      Stop -  Stops execution after the first error

2. Use exception handling by using traps and try/catch blocks or if statements to detect errors and return with non-zero exit codes

3. Use custom error handling that can be invoked after launching each command in the script to correctly detect errors. 

### Examples

The following example will show you how setting $ErrorActionPreference will return exit codes

In the below code, `ls nothing123` is expected to fail.

```Windows
ls nothing123
Write-Host "Test"
```

Here is the output when the above commands runs  on a remote host and the script will return the value of `$?` to be True eventhough the script failed.

```PS C:\Users\dtully\test> ./test1.ps1
ls : Cannot find path 'C:\Users\dtully\test\nothing123' because it does not exist.
At C:\Users\dtully\test\test1.ps1:1 char:1
+ ls nothing123
+ ~~~~~~~~~~~~~
    + CategoryInfo          : ObjectNotFound: (C:\Users\dtully\test\nothing123:String) [Get-ChildItem], ItemNotFoundEx
   ception
    + FullyQualifiedErrorId : PathNotFound,Microsoft.PowerShell.Commands.GetChildItemCommand

PS C:\Users\dtully\test> Write-Host $?
True
```
Now lets set $ErrorActionPreference=Stop.

```Windows
$ErrorActionPreference = "Stop"
ls nothing123
Write-Host "Test"
```
Now when we run the command again we see the return value of `$?` to be False.

```Windows
PS C:\Users\dtully\test> ./test1.ps1
ls : Cannot find path 'C:\Users\dtully\test\nothing123' because it does not exist.
At C:\Users\dtully\test\test1.ps1:2 char:1
+ ls nothing123
+ ~~~~~~~~~~~~~
    + CategoryInfo          : ObjectNotFound: (C:\Users\dtully\test\nothing123:String) [Get-ChildItem], ItemNotFoundException
    + FullyQualifiedErrorId : PathNotFound,Microsoft.PowerShell.Commands.GetChildItemCommand

PS C:\Users\dtully\test> Write-Host $?
False
```

The following example shows how you can use the function verifySuccess to detect whether the previous command failed, and if it did print, print an error message and return with an exit code of 1.

```Windows
function die {
    Write-Error "Error: $($args[0])"
    exit 1
}
 
function verifySuccess {
    if (!$?) {
        die "$($args[0])"
    }
}
 
Write-Output "I'd rather be in Hawaii"
verifySuccess "WRITE_OUTPUT_FAILED"
 
& C:\Program Files\Delphix\scripts\myscript.ps1
verifySuccess "MY_SCRIPT_FAILED"
```
