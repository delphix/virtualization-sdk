---
name: vsdk-code-review
description: Use when reviewing or writing code in the Delphix Virtualization SDK (virtualization-sdk repo). Covers correctness, exception handling, readability, test quality, and repo conventions (copyright, imports, docstrings, proto conversion, CLI structure).
---

# vSDK Code Review

## Overview

Reference for the conventions used in the `virtualization-sdk` repo.

**What CI gates:** `pytest` (all packages, Ubuntu + macOS + Windows) and `flake8 --max-line-length 88` (Ubuntu only). Everything else in this skill is convention enforced through code review.

Run locally: `sh bin/build_project.sh -f` for flake8, `-t` for tests.

---

## Copyright Headers

Every source file starts with:

```python
#
# Copyright (c) YEAR by Delphix. All rights reserved.
#
```

- Use the current year for new files; for files modified in a later year use `<first_year>, <current_year>`: e.g. `2019, 2026`
- This applies to `.py` files **and** `pyproject.toml` files
- Blank line between the header and the first import or docstring

---

## Imports

Order: **stdlib → third-party → local**, one blank line between each group. All alphabetical within groups. Matches isort defaults.

```python
# stdlib
import logging
import os
from contextlib import contextmanager

# third-party
import click

# local (dlpx namespace)
from dlpx.virtualization._internal import exceptions, file_util
from dlpx.virtualization._internal.commands import build as build_internal
```

Rules:
- **Absolute imports only** — no relative imports (`from . import ...`)
- Multi-line imports use **parentheses**, not backslash continuation
- Align wrapped imports to the opening parenthesis

---

## Formatting

**Only `flake8` is enforced** — `isort` and `yapf` are dev dependencies but are never run in CI or `build_project.sh`. No repo-level config files for any of them.

Flake8 runs with `--max-line-length 88` (both CI and `build_project.sh -f`):

```bash
python -m flake8 src/main/python --max-line-length 88
python -m flake8 src/test/python --max-line-length 88
```

Key observable style patterns in existing code:
- **Max line length: 88 chars** (not PEP 8's 79)
- Function arguments wrap to align under the opening parenthesis
- `isort` / `yapf` may be run locally as a courtesy but are not gated

---

## Docstrings

**Google-style** with `Args` and `Returns` sections. Type info goes in the docstring, not in the signature.

```python
def build(plugin_config, upload_artifact, generate_only, local_vsdk_root=None):
    """Builds the plugin using the configuration provided.

    Args:
        plugin_config (str): Path to the plugin's config yaml file.
        upload_artifact (str): Output file for the build artifact.
        generate_only (bool): If True, only generate classes from schemas.
        local_vsdk_root (str): Local path to the vSDK repo; None uses PyPI.

    Returns:
        str: Path to the generated upload artifact.
    """
```

- Opening `"""` on the definition line
- One-line summary, blank line, then details/Args/Returns

---

## Logging

Every module that logs gets a module-level logger:

```python
logger = logging.getLogger(__name__)
```

Use `logger.debug(...)` for implementation details, `logger.warning(...)` for recoverable issues. Never `print()`.

---

## Exception Hierarchy

Choose the right class for the context:

| Package | Exception | When to use |
|---|---|---|
| `tools` | `UserError` | User-visible CLI errors (bad input, missing file). Caught by cli.py and shown to the user. |
| `tools` | `SDKToolingError` | Internal SDK bugs; not user-actionable. |
| `platform` | `UserError` | User-visible errors in operation validation context. |
| `platform` | `IncorrectReturnTypeError` | Operation impl returned the wrong type. |
| `platform` | `OperationNotDefinedError` | `_internal_*` called but impl was never registered. |
| `platform` | `OperationAlreadyDefinedError` | Decorator applied twice to the same operation. |
| `platform` | `DecoratorNotFunctionError` | Decorated object is not a callable. |
| `common` | `PlatformError` | Engine-side bug detected; will be a Fatal on the Delphix Engine. |
| `common` | `PluginRuntimeError` | Plugin-catchable error; plugin code can handle it. |
| `common` | `IncorrectTypeError` | Type validation failure on proto deserialization. |
| `libs` | `LibraryError` | Error from a libs API call; plugin may retry or raise custom error. |
| `libs` | `PluginScriptError` | Non-zero exit from a subprocess/shell execution. |
| `libs` | `IncorrectArgumentTypeError` | Wrong type passed to a libs API function. |

All exceptions expose a `.message` property. Raise with a helpful string:

```python
raise exceptions.UserError(
    "The src directory {} is not a subdirectory of plugin root {}.".format(
        src_dir, plugin_root))
```

---

## Proto Conversion

Classes that wrap protobuf messages implement **bidirectional conversion**:

```python
def to_proto(self):
    """Converts RemoteConnection to common_pb2.RemoteConnection."""
    proto = common_pb2.RemoteConnection()
    proto.environment.CopyFrom(self.environment.to_proto())
    proto.user.CopyFrom(self.user.to_proto())
    return proto

@staticmethod
def from_proto(connection):
    """Converts common_pb2.RemoteConnection to RemoteConnection."""
    if not isinstance(connection, common_pb2.RemoteConnection):
        raise IncorrectTypeError(RemoteConnection, 'connection',
                                 type(connection), common_pb2.RemoteConnection)
    environment = RemoteEnvironment.from_proto(connection.environment)
    user = RemoteUser.from_proto(connection.user)
    return RemoteConnection(environment=environment, user=user)
```

Rules:
- `to_proto()` — instance method, returns the protobuf message
- `from_proto()` — `@staticmethod`, validates type with `isinstance`, returns the wrapper class
- Use `CopyFrom()` for nested proto fields (not direct assignment)
- Chain conversions for nested objects

---

## Namespace Packages

Each package's `__init__.py` at the `dlpx.virtualization` level must extend the path:

```python
__path__ = __import__('pkgutil').extend_path(__path__, __name__)
```

This allows the five separately-installed packages to share the `dlpx.virtualization` namespace.

---

## Testing Conventions

- Tests live in `src/test/python/dlpx/virtualization/` mirroring the main source tree
- Each package has a `conftest.py` at `src/test/python/dlpx/virtualization/conftest.py`
- Use `pytest` for test runner; `mock` (not `unittest.mock`) for patching
- Test classes prefixed with `Test`; methods prefixed with `test_`

```python
import mock
import pytest

class TestBuildCommand:

    @staticmethod
    @pytest.fixture()
    def mock_plugin_config(tmp_path):
        # fixture setup
        ...

    @staticmethod
    @mock.patch('dlpx.virtualization._internal.commands.build.os.path.exists')
    def test_build_succeeds(mock_exists, mock_plugin_config):
        mock_exists.return_value = True
        # assertions
        ...

    @staticmethod
    @pytest.mark.parametrize('level,expected', [
        (logging.DEBUG, 'DEBUG'),
        (logging.INFO, 'INFO'),
    ])
    def test_log_levels(level, expected):
        ...
```

Run tests: `python -m pytest src/test/python` from the package directory, or `sh bin/build_project.sh -t -m <pkg>` from the repo root.

---

## CLI Structure (tools package)

`cli.py` is **declarations only** — no business logic:

```python
# cli.py
@delphix_sdk.command()
@click.argument('plugin_config', ...)
def build(plugin_config, ...):
    """One-line help string for the command."""
    build_internal.build(plugin_config, ...)
```

All logic goes in `commands/<cmd>.py`. This is a firm convention — keep `cli.py` as the single source of truth for the CLI surface area.

---

## Correctness

### vSDK-specific invariants

- **New operation decorator** (`linked.x()` / `virtual.x()`): the `_internal_*` method must guard with `if not self.x_impl: raise OperationNotDefinedError(Op.X)` before calling the impl.
- **`from_proto()` must validate type** with `isinstance` and raise `IncorrectTypeError` before accessing any field on the proto object.
- **Proto field assignment** must use `CopyFrom()` for nested message fields — direct assignment (`proto.field = other_proto`) silently fails.
- **New wrapper class** exposed to plugin authors: needs both `to_proto()` and `from_proto()` unless it is purely plugin-input (no round-trip needed).
- **`__all__` in `_plugin_classes.py`** must include any new public class; `platform/__init__.py` uses `from _plugin_classes import *` so the wildcard picks it up automatically — but `__all__` must be updated.

### General correctness

- No mutable default arguments (`def f(x=[])` — use `None` and assign inside).
- Return values checked at call sites where the caller depends on them.
- No silently swallowed exceptions (`except Exception: pass` or bare `except:`).
- Branching logic covers all cases — check for missing `else` / unhandled enum values.

---

## Exception Handling

- Catch the **most specific** exception possible; re-raise or log anything unexpected.
- `UserError` messages must be **actionable** — tell the user what went wrong and how to fix it, not just what the code observed.
- Do not catch `UserError` inside library/platform code — let it propagate to `cli.py`.
- When wrapping a lower-level exception, preserve context: `raise UserError("...") from e`.

---

## Readability & Modularity

- Functions should do one thing. `_internal_*` methods in particular should only do proto conversion + delegation to the impl — no business logic.
- Avoid deeply nested conditionals; early-return or extract helper functions.
- Names should reflect the domain: use `source_config`, `repository`, `snapshot` — not `sc`, `repo`, `snap`.
- Constants belong at module level (UPPERCASE), not buried in function bodies.

---

## Test Quality

- New operations need tests in `test_plugin.py` covering: successful call, `OperationNotDefinedError` when impl is not set, and `OperationAlreadyDefinedError` when decorated twice.
- Tests should assert **behaviour**, not implementation details (avoid asserting on private attributes like `_impl`).
- Fixtures in `conftest.py` should be extended for new fields (e.g. new `_impl = None` in the operation fixture).
- Parametrized tests (`@pytest.mark.parametrize`) preferred over copy-paste test variants.

---

## Common Review Checklist

**Style & conventions:**
- [ ] Copyright header present and correct format
- [ ] Imports: stdlib → third-party → local, alphabetical, parentheses for multi-line
- [ ] Google-style docstrings for public functions
- [ ] `logger = logging.getLogger(__name__)` at module level (not `print`)
- [ ] Max line length 88 chars (`flake8 --max-line-length 88`)

**Correctness:**
- [ ] New operation `_internal_*`: guards `if not self.x_impl: raise OperationNotDefinedError`
- [ ] `from_proto()`: validates type with `isinstance` before field access
- [ ] Proto field assignment uses `CopyFrom()` for nested messages
- [ ] No mutable default arguments; no silently swallowed exceptions
- [ ] Correct exception class for the package/context (see table above)
- [ ] `UserError` messages are actionable (say what went wrong and how to fix it)

**Architecture:**
- [ ] Proto classes: `to_proto()` + `from_proto()` with type validation
- [ ] `__init__.py` for new `dlpx.virtualization` packages: includes `pkgutil.extend_path`
- [ ] New public class added to `_plugin_classes.__all__`
- [ ] New operations: `Operation` enum value, public decorator name, `_internal_*` method name, and all docstring/comment references use the **same operation name** consistently
- [ ] New required operations: `plugin_validator.py` updated to enforce the operation is implemented
- [ ] New CLI commands: logic in `commands/<cmd>.py`, not `cli.py`

**Tests:**
- [ ] Tests mirror the source tree path; use `pytest` + `mock`
- [ ] New operations covered in `test_plugin.py`: success, `OperationNotDefinedError`, `OperationAlreadyDefinedError`
- [ ] `conftest.py` fixtures updated for new `_impl` fields
- [ ] `sh bin/build_project.sh -f` passes (flake8)
- [ ] `sh bin/build_project.sh -t` passes (unit tests)

**Docs changes** (`docs/` only — skip for pure code PRs):
- [ ] Release note heading format: `# Release - v5.1.0` / `# Breaking Changes - v5.1.0` (no period after `v`)
- [ ] New operation added to `Plugin_Operations.md` summary table, `Decorators.md` table, and `Classes.md` (if a new class was introduced)
- [ ] `Schemas.md` row count updated if a new schema was added
- [ ] New workflow added to `Workflows.md` if referenced from the operations table
- [ ] Internal anchor links use the correct glossary/section slug (not a copy-paste from a similar row)
