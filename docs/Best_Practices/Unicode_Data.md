#Dealing with Unicode Data
Sometimes plugin authors need to run commands or scripts containing unicode characters. This may result in errors
during the plugin build or during the execution of the commands if proper encoding is not provided. To properly use
the unicode characters in plugin code, the following lines should be included at top of the script.

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
```