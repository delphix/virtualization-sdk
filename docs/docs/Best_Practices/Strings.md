# Working With Strings

Unfortunately, Python 2.7 makes it very easy to accidentally write string-related code that will sometimes work, but sometimes fail (especially for people who are not using English). Read on for some tips for how to avoid this.

## The Two String Types
Python 2.7 has two different types that are both called "strings". One represents
a sequence of **bytes**, and the other represents a sequence of **characters**.

```python
# The default string (aka 'str object') represents bytes
my_bytes = "This string is a sequence of bytes"

# A 'Unicode object' represents characters (note the u just before the quote)
my_characters = u"This string is a sequence of characters"
```

## Unicode Strings Are Preferred

There are a couple of reasons to prefer the "unicode object" over the "str object".

First, in most cases, we care about characters, and we're not particularly interested in which bytes
are used to represent those characters.  That is, we might care that we have a "letter H" followed by a "letter I", but it's usually irrelevant to us what byte values happen to be used.

Second, there are lots of different schemes available which give rules for how to represent characters as bytes. These schemes are called "encodings"; some examples include "ASCII", "UTF-8", "Shift-JIS", and "UCS-2".  Each encoding uses different rules about which characters are represented by which bytes.

A "str object" doesn't know anything about encodings... it is just a sequence of bytes. So, when a programmer is working with one of these byte strings, they have to know which encoding rules are in play.

In order to avoid problems, **we recommend using Unicode strings everywhere** in your plugin code.

## Delphix I/O

Your plugin will sometimes need to send strings back and forth to Delphix code. There are two supported formats for doing this.  Any time you receive a string from Delphix, it will be in one of the two following forms. This includes arguments to your plugin operations, and return values from "Delphix Libs" functions. Likewise, any time you send a string to Delphix, it must be in one of these two forms.

Acceptable forms:

1. A Unicode string (recommended)
2. A "str object" (byte string) that uses the UTF-8 encoding

## Converting Between Types

Sometimes (hopefully rarely!), you might find yourself needing to convert back and forth between byte strings and character strings. For example, you might need to read or write a file on a remote system that is required to use some specific encoding. Here's how to do that:

```python
# Converting from a character string ("unicode") to a byte string ("str")
my_utf8_byte_string = my_character_string.encode("utf-8")
my_utf16_byte_string = my_character_string.encode("utf-16")

# Converting from a byte string to a character string
my_character_string1 = my_utf8_byte_string.decode("utf-8")
my_character_string2 = my_utf16_byte_string.decode("utf-16")
my_character_string3 = my_ascii_byte_string.decode("ascii")
```

Things to note:

- `encode` goes from characters to bytes. `decode` goes from bytes to characters.
- If you try to `encode` a character string using the `ascii` encoding, but your character string contains non-ascii characters, you'll get an error. More generally: some encodings will error out with some characters.
- If you don't specify an encoding, Python will supply a default. But, there's a good chance the default will be wrong for your use case. So, always specify the encoding!
- Don't try to `encode` a byte string. If you do this, Python will "helpfully" insert an implicit `decode` first, which tends to cause very confusing error messages. Likewise, don't try to `decode` a character string.
- `utf-8` is likely the best encoding to use for most situations. It accepts all characters, does not have issues with byte ordering, and is understood by most systems. This is not true of most other encodings.

## Using Non-ASCII characters in Python files

Python 2.7 source code files are assumed to use the "ASCII" encoding, unless told otherwise. Unfortunately, ASCII is an obsolete encoding that only knows how to deal with a small number of characters, and only really supports American English.

In order to include non-ASCII characters in your source code, you need to use a different encoding than ASCII, and you need to tell the Python interpreter which encoding you're using.  In Python 2.7, this is done with a "magic" comment at the very top of each file.

Here is an example of the first line of a Python file that uses the UTF-8 encoding:
```python
# -*- coding: utf-8 -*-
```

If you do not specify an encoding, and the source code contains any non-ASCII characters, you will get errors
 when building the plugin using [dvp build](/References/CLI.md#build) or during the execution of a plugin operation.

### Example

```python
# -*- coding: utf-8 -*-
from dlpx.virtualization.platform import Plugin
from dlpx.virtualization import libs
from generated.definitions import RepositoryDefinition

plugin = Plugin()

@plugin.discovery.repository()
def repository_discovery(source_connection):
    # Create a repository with name that uses non-ASCII characters
    return [RepositoryDefinition(name=u"Théâtre")]
```
